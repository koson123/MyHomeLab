using Playnite.SDK;
using Playnite.SDK.Models;
using Playnite.SDK.Plugins;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Web.Script.Serialization;

namespace GameHubSync
{
    public class GameHubSync : GenericPlugin
    {
        private static readonly ILogger Logger = LogManager.GetLogger();
        private static readonly Guid PluginGuid = Guid.Parse("7e6b7718-3a0b-4a44-bfe2-c21d88e8361a");
        private readonly string configPath;

        public override Guid Id => PluginGuid;

        public GameHubSync(IPlayniteAPI api) : base(api)
        {
            var dataPath = GetPluginUserDataPath();
            Directory.CreateDirectory(dataPath);
            configPath = Path.Combine(dataPath, "gamehub.json");
            EnsureConfigTemplate();
        }

        public override IEnumerable<MainMenuItem> GetMainMenuItems(GetMainMenuItemsArgs args)
        {
            yield return new MainMenuItem
            {
                MenuSection = "@Game Hub",
                Description = "Sync library to Game Hub",
                Action = _ => SyncLibrary(true)
            };

            yield return new MainMenuItem
            {
                MenuSection = "@Game Hub",
                Description = "Open Game Hub config folder",
                Action = _ => OpenConfigFolder()
            };
        }

        public override void OnLibraryUpdated(OnLibraryUpdatedEventArgs args)
        {
            try
            {
                var config = LoadConfig();
                if (config.SyncOnLibraryUpdated)
                {
                    SyncLibrary(false);
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Game Hub automatic library sync failed.");
            }
        }

        private void SyncLibrary(bool showDialog)
        {
            try
            {
                var config = LoadConfig();
                ValidateConfig(config);

                var games = PlayniteApi.Database.Games.Select(ToSnapshot).ToList();
                var payload = new Dictionary<string, object>
                {
                    ["device_name"] = string.IsNullOrWhiteSpace(config.DeviceName) ? Environment.MachineName : config.DeviceName,
                    ["agent_url"] = string.IsNullOrWhiteSpace(config.AgentUrl) ? null : config.AgentUrl,
                    ["games"] = games
                };

                var serializer = new JavaScriptSerializer
                {
                    MaxJsonLength = int.MaxValue
                };
                var json = serializer.Serialize(payload);
                var url = config.GameHubUrl.TrimEnd('/') + "/api/v1/import/playnite";

                string responseBody;
                using (var client = new HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(60);
                    client.DefaultRequestHeaders.Add("X-GameHub-Key", config.ApiKey);
                    using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
                    using (var response = client.PostAsync(url, content).GetAwaiter().GetResult())
                    {
                        responseBody = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
                        if (!response.IsSuccessStatusCode)
                        {
                            throw new InvalidOperationException(
                                $"Game Hub returned {(int)response.StatusCode} {response.ReasonPhrase}: {responseBody}");
                        }
                    }
                }

                Logger.Info($"Game Hub sync completed. Sent {games.Count} Playnite games.");
                if (showDialog)
                {
                    PlayniteApi.Dialogs.ShowMessage(
                        $"Game Hub sync completed.\n\nSent {games.Count} games.\n\nServer response:\n{responseBody}",
                        "Game Hub Sync");
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Game Hub library sync failed.");
                if (showDialog)
                {
                    PlayniteApi.Dialogs.ShowErrorMessage(ex.Message, "Game Hub Sync");
                }
            }
        }

        private Dictionary<string, object> ToSnapshot(Game game)
        {
            return new Dictionary<string, object>
            {
                ["database_id"] = game.Id.ToString(),
                ["name"] = game.Name,
                ["game_id"] = string.IsNullOrWhiteSpace(game.GameId) ? null : game.GameId,
                ["plugin_id"] = game.PluginId.ToString(),
                ["source"] = game.Source?.Name,
                ["platforms"] = game.Platforms?.Select(platform => platform.Name).Where(name => !string.IsNullOrWhiteSpace(name)).ToList()
                    ?? new List<string>(),
                ["release_year"] = game.ReleaseYear,
                ["is_installed"] = game.IsInstalled,
                ["install_directory"] = string.IsNullOrWhiteSpace(game.InstallDirectory) ? null : game.InstallDirectory,
                ["playtime_seconds"] = game.Playtime,
                ["play_count"] = game.PlayCount,
                ["last_activity"] = game.LastActivity.HasValue ? game.LastActivity.Value.ToUniversalTime().ToString("o") : null,
                ["hidden"] = game.Hidden,
                ["favorite"] = game.Favorite,
                ["sorting_name"] = string.IsNullOrWhiteSpace(game.SortingName) ? null : game.SortingName
            };
        }

        private GameHubConfig LoadConfig()
        {
            EnsureConfigTemplate();
            var serializer = new JavaScriptSerializer();
            var json = File.ReadAllText(configPath);
            var config = serializer.Deserialize<GameHubConfig>(json);
            return config ?? new GameHubConfig();
        }

        private void ValidateConfig(GameHubConfig config)
        {
            if (string.IsNullOrWhiteSpace(config.GameHubUrl))
            {
                throw new InvalidOperationException($"GameHubUrl is missing in {configPath}");
            }

            if (!Uri.TryCreate(config.GameHubUrl, UriKind.Absolute, out var uri) ||
                (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
            {
                throw new InvalidOperationException("GameHubUrl must be an absolute http:// or https:// URL.");
            }

            if (string.IsNullOrWhiteSpace(config.ApiKey) || config.ApiKey.StartsWith("replace-", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException($"Set ApiKey in {configPath} before syncing.");
            }
        }

        private void EnsureConfigTemplate()
        {
            if (File.Exists(configPath))
            {
                return;
            }

            var serializer = new JavaScriptSerializer();
            var example = new GameHubConfig
            {
                GameHubUrl = "http://gamehub.internal:8787",
                ApiKey = "replace-with-gamehub-api-key",
                DeviceName = Environment.MachineName,
                AgentUrl = "http://gaming-pc.internal:8790",
                SyncOnLibraryUpdated = true
            };
            File.WriteAllText(configPath, serializer.Serialize(example));
        }

        private void OpenConfigFolder()
        {
            Directory.CreateDirectory(GetPluginUserDataPath());
            Process.Start("explorer.exe", GetPluginUserDataPath());
        }
    }

    public class GameHubConfig
    {
        public string GameHubUrl { get; set; }
        public string ApiKey { get; set; }
        public string DeviceName { get; set; }
        public string AgentUrl { get; set; }
        public bool SyncOnLibraryUpdated { get; set; } = true;
    }
}
