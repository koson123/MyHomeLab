using System.Diagnostics;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Win32;

namespace GameHubClient;

internal static class Program
{
    internal const string ProductName = "Trevor Game Hub";
    internal const string RunValueName = "TrevorGameHubAgent";

    [STAThread]
    private static async Task Main(string[] args)
    {
        if (args.Any(a => string.Equals(a, "--agent", StringComparison.OrdinalIgnoreCase)))
        {
            await AgentHost.RunAsync();
            return;
        }

        ApplicationConfiguration.Initialize();
        Application.Run(new SetupForm());
    }
}

internal sealed class SetupForm : Form
{
    private readonly TextBox gameHubUrl = new() { Width = 430 };
    private readonly TextBox apiKey = new() { Width = 430, UseSystemPasswordChar = true };
    private readonly TextBox agentToken = new() { Width = 430, UseSystemPasswordChar = true };
    private readonly TextBox deviceName = new() { Width = 430 };
    private readonly NumericUpDown agentPort = new() { Minimum = 1024, Maximum = 65535, Value = 8790, Width = 120 };
    private readonly TextBox agentUrl = new() { Width = 430 };
    private readonly TextBox playniteExtensions = new() { Width = 430 };
    private readonly CheckBox dryRun = new() { Text = "Dry-run launches until I intentionally turn this off", Checked = true, AutoSize = true };
    private readonly Label status = new() { AutoSize = true, Text = "Ready." };

    public SetupForm()
    {
        Text = "Trevor Game Hub Setup";
        Width = 690;
        Height = 560;
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;

        var saved = ClientConfigStore.Load();
        gameHubUrl.Text = saved?.GameHubUrl ?? "http://gamehub.internal:8787";
        apiKey.Text = saved is null ? "" : ClientConfigStore.Unprotect(saved.ApiKeyProtected);
        agentToken.Text = saved is null ? "" : ClientConfigStore.Unprotect(saved.AgentTokenProtected);
        deviceName.Text = saved?.DeviceName ?? Environment.MachineName;
        agentPort.Value = saved?.AgentPort ?? 8790;
        agentUrl.Text = saved?.AgentUrl ?? $"http://{NetworkHelper.GetPreferredLanIPv4()}:{(int)agentPort.Value}";
        playniteExtensions.Text = saved?.PlayniteExtensionsPath ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Playnite", "Extensions");
        dryRun.Checked = saved?.DryRun ?? true;

        agentPort.ValueChanged += (_, _) =>
        {
            if (agentUrl.Text.StartsWith("http://", StringComparison.OrdinalIgnoreCase))
                agentUrl.Text = $"http://{NetworkHelper.GetPreferredLanIPv4()}:{(int)agentPort.Value}";
        };

        var table = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 3,
            RowCount = 10,
            Padding = new Padding(14),
            AutoSize = true
        };
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 150));
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 90));

        AddRow(table, 0, "Game Hub URL", gameHubUrl);
        AddRow(table, 1, "API key", apiKey);
        AddRow(table, 2, "Agent token", agentToken);
        AddRow(table, 3, "Device name", deviceName);
        AddRow(table, 4, "Agent port", agentPort);
        AddRow(table, 5, "Advertised agent URL", agentUrl);

        var browse = new Button { Text = "Browse...", AutoSize = true };
        browse.Click += (_, _) => BrowsePlayniteFolder();
        AddRow(table, 6, "Playnite Extensions", playniteExtensions, browse);

        table.Controls.Add(dryRun, 1, 7);
        table.SetColumnSpan(dryRun, 2);

        var test = new Button { Text = "Test Connection", Width = 130, Height = 34 };
        test.Click += async (_, _) => await TestConnectionAsync();
        var install = new Button { Text = "Install / Update", Width = 130, Height = 34 };
        install.Click += async (_, _) => await InstallAsync();
        var startAgent = new Button { Text = "Start Agent", Width = 110, Height = 34 };
        startAgent.Click += (_, _) => StartInstalledAgent();

        var buttons = new FlowLayoutPanel { FlowDirection = FlowDirection.LeftToRight, AutoSize = true, Dock = DockStyle.Fill };
        buttons.Controls.Add(test);
        buttons.Controls.Add(install);
        buttons.Controls.Add(startAgent);
        table.Controls.Add(buttons, 1, 8);
        table.SetColumnSpan(buttons, 2);

        table.Controls.Add(status, 1, 9);
        table.SetColumnSpan(status, 2);
        Controls.Add(table);
    }

    private static void AddRow(TableLayoutPanel table, int row, string labelText, Control control, Control? extra = null)
    {
        var label = new Label { Text = labelText, AutoSize = true, Anchor = AnchorStyles.Left };
        control.Anchor = AnchorStyles.Left | AnchorStyles.Right;
        table.Controls.Add(label, 0, row);
        table.Controls.Add(control, 1, row);
        if (extra is not null)
        {
            extra.Anchor = AnchorStyles.Left;
            table.Controls.Add(extra, 2, row);
        }
    }

    private void BrowsePlayniteFolder()
    {
        using var dialog = new FolderBrowserDialog
        {
            Description = "Choose Playnite's Extensions folder",
            SelectedPath = playniteExtensions.Text,
            ShowNewFolderButton = true
        };
        if (dialog.ShowDialog(this) == DialogResult.OK)
            playniteExtensions.Text = dialog.SelectedPath;
    }

    private ClientConfig ReadFormConfig()
    {
        if (!Uri.TryCreate(gameHubUrl.Text.Trim(), UriKind.Absolute, out var hub) ||
            (hub.Scheme != Uri.UriSchemeHttp && hub.Scheme != Uri.UriSchemeHttps))
            throw new InvalidOperationException("Game Hub URL must be a valid http:// or https:// address.");

        if (!Uri.TryCreate(agentUrl.Text.Trim(), UriKind.Absolute, out var agent) || agent.Scheme != Uri.UriSchemeHttp)
            throw new InvalidOperationException("Advertised agent URL must be a valid http:// address reachable by the server.");

        if (string.IsNullOrWhiteSpace(apiKey.Text)) throw new InvalidOperationException("Enter the Game Hub API key.");
        if (string.IsNullOrWhiteSpace(agentToken.Text)) throw new InvalidOperationException("Enter the device agent token.");
        if (string.IsNullOrWhiteSpace(deviceName.Text)) throw new InvalidOperationException("Enter a device name.");
        if (string.IsNullOrWhiteSpace(playniteExtensions.Text)) throw new InvalidOperationException("Choose Playnite's Extensions folder.");

        return new ClientConfig
        {
            GameHubUrl = hub.ToString().TrimEnd('/'),
            ApiKeyProtected = ClientConfigStore.Protect(apiKey.Text),
            AgentTokenProtected = ClientConfigStore.Protect(agentToken.Text),
            DeviceName = deviceName.Text.Trim(),
            AgentPort = (int)agentPort.Value,
            AgentUrl = agent.ToString().TrimEnd('/'),
            PlayniteExtensionsPath = playniteExtensions.Text.Trim(),
            DryRun = dryRun.Checked
        };
    }

    private async Task TestConnectionAsync()
    {
        try
        {
            var config = ReadFormConfig();
            status.Text = "Testing Game Hub...";
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
            client.DefaultRequestHeaders.Add("X-GameHub-Key", apiKey.Text);
            using var response = await client.GetAsync(config.GameHubUrl + "/api/v1/providers");
            response.EnsureSuccessStatusCode();
            status.Text = "Connection successful.";
        }
        catch (Exception ex)
        {
            status.Text = "Connection failed.";
            MessageBox.Show(this, ex.Message, Program.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private async Task InstallAsync()
    {
        try
        {
            var config = ReadFormConfig();
            status.Text = "Testing server...";
            using (var client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) })
            {
                client.DefaultRequestHeaders.Add("X-GameHub-Key", apiKey.Text);
                using var response = await client.GetAsync(config.GameHubUrl + "/api/v1/providers");
                response.EnsureSuccessStatusCode();
            }

            status.Text = "Installing client...";
            ClientConfigStore.Save(config);
            Installer.StopExistingAgent();
            Installer.InstallClientExecutable();
            Installer.InstallPlaynitePlugin(config.PlayniteExtensionsPath);
            Installer.EnableStartup();
            Installer.StartAgent();

            status.Text = "Installed. Restart Playnite, then update its game library once to trigger the first sync.";
            MessageBox.Show(
                this,
                "Game Hub client installed.\n\nThe launch agent is starting now. Restart Playnite, then use Update Game Library once. The Game Hub Sync plugin will send your library automatically.\n\nLaunches are still in dry-run mode unless you unchecked that box.",
                Program.ProductName,
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            status.Text = "Install failed.";
            MessageBox.Show(this, ex.ToString(), Program.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void StartInstalledAgent()
    {
        try
        {
            var config = ReadFormConfig();
            ClientConfigStore.Save(config);
            Installer.StopExistingAgent();
            Installer.InstallClientExecutable();
            Installer.StartAgent();
            status.Text = "Agent start requested.";
        }
        catch (Exception ex)
        {
            MessageBox.Show(this, ex.Message, Program.ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}

internal static class Installer
{
    private const string PluginFolderName = "GameHubSync_7e6b7718-3a0b-4a44-bfe2-c21d88e8361a";

    internal static string InstallDirectory => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TrevorGameHub");
    internal static string InstalledExe => Path.Combine(InstallDirectory, "GameHubClient.exe");

    internal static void StopExistingAgent()
    {
        foreach (var process in Process.GetProcessesByName("GameHubClient"))
        {
            try
            {
                if (process.Id == Environment.ProcessId) continue;
                process.Kill(true);
                process.WaitForExit(3000);
            }
            catch { }
        }
    }

    internal static void InstallClientExecutable()
    {
        Directory.CreateDirectory(InstallDirectory);
        var current = Environment.ProcessPath ?? throw new InvalidOperationException("Unable to determine current executable path.");
        if (!Path.GetFullPath(current).Equals(Path.GetFullPath(InstalledExe), StringComparison.OrdinalIgnoreCase))
            File.Copy(current, InstalledExe, true);
    }

    internal static void InstallPlaynitePlugin(string extensionsRoot)
    {
        var target = Path.Combine(extensionsRoot, PluginFolderName);
        Directory.CreateDirectory(target);
        ExtractResource("GameHubClient.Embedded.GameHubSync.dll", Path.Combine(target, "GameHubSync.dll"));
        ExtractResource("GameHubClient.Embedded.extension.yaml", Path.Combine(target, "extension.yaml"));
    }

    internal static void EnableStartup()
    {
        using var key = Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run");
        key?.SetValue(Program.RunValueName, $"\"{InstalledExe}\" --agent", RegistryValueKind.String);
    }

    internal static void StartAgent()
    {
        if (!File.Exists(InstalledExe)) InstallClientExecutable();
        Process.Start(new ProcessStartInfo(InstalledExe, "--agent") { UseShellExecute = true });
    }

    private static void ExtractResource(string resourceName, string outputPath)
    {
        using var input = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName)
            ?? throw new InvalidOperationException($"Embedded resource missing: {resourceName}");
        using var output = File.Create(outputPath);
        input.CopyTo(output);
    }
}

internal static class AgentHost
{
    internal static async Task RunAsync()
    {
        var config = ClientConfigStore.Load() ?? throw new InvalidOperationException("Game Hub client is not configured. Run GameHubClient.exe first.");
        var token = ClientConfigStore.Unprotect(config.AgentTokenProtected);
        if (string.IsNullOrWhiteSpace(token)) throw new InvalidOperationException("Agent token is missing.");

        Directory.CreateDirectory(Installer.InstallDirectory);
        var logPath = Path.Combine(Installer.InstallDirectory, "agent.log");
        AgentLogger.Write(logPath, $"Starting agent on port {config.AgentPort}; dry_run={config.DryRun}");

        var builder = WebApplication.CreateBuilder();
        builder.WebHost.UseUrls($"http://0.0.0.0:{config.AgentPort}");
        var app = builder.Build();

        app.MapGet("/health", () => Results.Json(new
        {
            status = "ok",
            device = config.DeviceName,
            dry_run = config.DryRun,
            version = "0.2.0"
        }));

        app.MapPost("/v1/launch", async (HttpRequest request) =>
        {
            if (!TryAuthorize(request, token)) return Results.Unauthorized();

            LaunchRequest? payload;
            try { payload = await request.ReadFromJsonAsync<LaunchRequest>(); }
            catch { return Results.BadRequest(new { detail = "Invalid JSON" }); }

            if (payload is null || string.IsNullOrWhiteSpace(payload.launch_ref))
                return Results.BadRequest(new { detail = "launch_ref is required" });

            if (!Uri.TryCreate(payload.launch_ref, UriKind.Absolute, out var launchUri) || !AllowedLaunchScheme(launchUri.Scheme))
                return Results.BadRequest(new { detail = "launch_ref scheme is not allowed" });

            AgentLogger.Write(logPath, $"Launch request: {payload.title ?? "unknown"} -> {payload.launch_ref}; dry_run={config.DryRun}");
            if (config.DryRun)
                return Results.Json(new { status = "accepted", dry_run = true, launch_ref = payload.launch_ref });

            try
            {
                Process.Start(new ProcessStartInfo(payload.launch_ref) { UseShellExecute = true });
                return Results.Json(new { status = "launched", dry_run = false });
            }
            catch (Exception ex)
            {
                AgentLogger.Write(logPath, "Launch failed: " + ex.Message);
                return Results.Problem("Launch failed", statusCode: 500);
            }
        });

        await app.RunAsync();
    }

    private static bool TryAuthorize(HttpRequest request, string expectedToken)
    {
        var header = request.Headers["Authorization"].ToString();
        const string prefix = "Bearer ";
        if (!header.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) return false;
        var presented = header[prefix.Length..];
        var a = SHA256.HashData(Encoding.UTF8.GetBytes(presented));
        var b = SHA256.HashData(Encoding.UTF8.GetBytes(expectedToken));
        return CryptographicOperations.FixedTimeEquals(a, b);
    }

    private static bool AllowedLaunchScheme(string scheme) =>
        scheme.Equals("playnite", StringComparison.OrdinalIgnoreCase) ||
        scheme.Equals("steam", StringComparison.OrdinalIgnoreCase);

    private sealed class LaunchRequest
    {
        public int game_id { get; set; }
        public string? title { get; set; }
        public string? provider { get; set; }
        public string? launch_ref { get; set; }
    }
}

internal static class ClientConfigStore
{
    internal static string ConfigPath => Path.Combine(Installer.InstallDirectory, "client.json");

    internal static ClientConfig? Load()
    {
        try
        {
            if (!File.Exists(ConfigPath)) return null;
            return JsonSerializer.Deserialize<ClientConfig>(File.ReadAllText(ConfigPath));
        }
        catch { return null; }
    }

    internal static void Save(ClientConfig config)
    {
        Directory.CreateDirectory(Installer.InstallDirectory);
        var json = JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(ConfigPath, json);
    }

    internal static string Protect(string plain)
    {
        if (string.IsNullOrEmpty(plain)) return "";
        var bytes = ProtectedData.Protect(Encoding.UTF8.GetBytes(plain), null, DataProtectionScope.CurrentUser);
        return Convert.ToBase64String(bytes);
    }

    internal static string Unprotect(string? protectedValue)
    {
        if (string.IsNullOrWhiteSpace(protectedValue)) return "";
        try
        {
            var bytes = ProtectedData.Unprotect(Convert.FromBase64String(protectedValue), null, DataProtectionScope.CurrentUser);
            return Encoding.UTF8.GetString(bytes);
        }
        catch { return ""; }
    }
}

internal sealed class ClientConfig
{
    public string GameHubUrl { get; set; } = "";
    public string ApiKeyProtected { get; set; } = "";
    public string AgentTokenProtected { get; set; } = "";
    public string DeviceName { get; set; } = Environment.MachineName;
    public int AgentPort { get; set; } = 8790;
    public string AgentUrl { get; set; } = "";
    public string PlayniteExtensionsPath { get; set; } = "";
    public bool DryRun { get; set; } = true;
}

internal static class NetworkHelper
{
    internal static string GetPreferredLanIPv4()
    {
        try
        {
            foreach (var nic in NetworkInterface.GetAllNetworkInterfaces()
                         .Where(n => n.OperationalStatus == OperationalStatus.Up && n.NetworkInterfaceType != NetworkInterfaceType.Loopback))
            {
                foreach (var uni in nic.GetIPProperties().UnicastAddresses)
                {
                    if (uni.Address.AddressFamily != AddressFamily.InterNetwork) continue;
                    var text = uni.Address.ToString();
                    if (text.StartsWith("169.254.")) continue;
                    return text;
                }
            }
        }
        catch { }
        return "127.0.0.1";
    }
}

internal static class AgentLogger
{
    internal static void Write(string path, string message)
    {
        try { File.AppendAllText(path, $"{DateTimeOffset.Now:O} {message}{Environment.NewLine}"); }
        catch { }
    }
}
