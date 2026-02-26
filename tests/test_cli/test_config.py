import os
from unittest.mock import patch

from click.testing import CliRunner

from arize_toolkit.cli.config_cmd import resolve_config
from arize_toolkit.cli.main import cli


class TestConfigResolution:
    def test_resolve_from_profile(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {
                        "api_key": "profile-key",
                        "organization": "profile-org",
                        "space": "profile-space",
                    }
                },
            )
            result = resolve_config()
        assert result["api_key"] == "profile-key"
        assert result["organization"] == "profile-org"
        assert result["space"] == "profile-space"

    def test_env_vars_override_profile(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {
                        "api_key": "profile-key",
                        "organization": "profile-org",
                        "space": "profile-space",
                    }
                },
            )
            with patch.dict(os.environ, {"ARIZE_DEVELOPER_KEY": "env-key"}):
                result = resolve_config()
        assert result["api_key"] == "env-key"
        assert result["organization"] == "profile-org"

    def test_cli_flags_override_all(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {
                        "api_key": "profile-key",
                        "organization": "profile-org",
                        "space": "profile-space",
                    }
                },
            )
            with patch.dict(os.environ, {"ARIZE_DEVELOPER_KEY": "env-key"}):
                result = resolve_config(api_key="flag-key", org="flag-org")
        assert result["api_key"] == "flag-key"
        assert result["organization"] == "flag-org"
        assert result["space"] == "profile-space"

    def test_named_profile(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {"api_key": "default-key", "organization": "default-org", "space": "default-space"},
                    "staging": {"api_key": "staging-key", "organization": "staging-org", "space": "staging-space"},
                },
            )
            result = resolve_config(profile="staging")
        assert result["api_key"] == "staging-key"
        assert result["organization"] == "staging-org"

    def test_missing_config_returns_empty(self, tmp_path):
        config_file = tmp_path / "nonexistent.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            result = resolve_config()
        assert result.get("api_key") is None


class TestConfigCommands:
    def test_config_init(self, tmp_path):
        config_file = tmp_path / "config.toml"
        runner = CliRunner()
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file), patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path):
            result = runner.invoke(cli, ["config", "init"], input="test-key\ntest-org\ntest-space\nhttps://app.arize.com\n")
        assert result.exit_code == 0
        assert "saved" in result.output.lower()

    def test_config_list_empty(self, tmp_path):
        config_file = tmp_path / "nonexistent.toml"
        runner = CliRunner()
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            result = runner.invoke(cli, ["config", "list"])
        assert result.exit_code == 0
        assert "No profiles" in result.output

    def test_config_list_with_profiles(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {"api_key": "k", "organization": "org1", "space": "sp1"},
                    "staging": {"api_key": "k2", "organization": "org2", "space": "sp2"},
                },
            )
        runner = CliRunner()
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            result = runner.invoke(cli, ["config", "list"])
        assert result.exit_code == 0
        assert "default" in result.output
        assert "staging" in result.output

    def test_config_show(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            save_config_to(
                config_file,
                {
                    "default": {"api_key": "secret", "organization": "myorg", "space": "myspace"},
                },
            )
        runner = CliRunner()
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file):
            result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "***" in result.output  # api_key is masked
        assert "myorg" in result.output

    def test_config_use(self, tmp_path):
        config_file = tmp_path / "config.toml"
        with patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file), patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path):
            save_config_to(
                config_file,
                {
                    "default": {"api_key": "k1", "organization": "org1", "space": "sp1"},
                    "staging": {"api_key": "k2", "organization": "org2", "space": "sp2"},
                },
            )
            runner = CliRunner()
            result = runner.invoke(cli, ["config", "use", "staging"])
        assert result.exit_code == 0
        assert "Switched" in result.output


def save_config_to(path, config):
    """Write config to a specific path."""
    import tomli_w

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(config, f)
