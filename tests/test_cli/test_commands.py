"""Tests for CLI command modules using Click's CliRunner with mocked Client."""

from unittest.mock import MagicMock, patch

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import pytest
import tomli_w
from click.testing import CliRunner

from arize_toolkit.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_client():
    """Provide a mocked Client that bypasses API initialization."""
    client = MagicMock()
    return client


@pytest.fixture(autouse=True)
def patch_get_client(mock_client):
    """Patch get_client to return our mock for all tests."""
    with patch("arize_toolkit.cli.client_factory.get_client", return_value=mock_client) as p:
        # Also patch each module's import of get_client
        modules = [
            "arize_toolkit.cli.spaces",
            "arize_toolkit.cli.orgs",
            "arize_toolkit.cli.users",
            "arize_toolkit.cli.models",
            "arize_toolkit.cli.monitors",
            "arize_toolkit.cli.prompts",
            "arize_toolkit.cli.custom_metrics",
            "arize_toolkit.cli.evaluators",
            "arize_toolkit.cli.dashboards",
            "arize_toolkit.cli.imports",
        ]
        patches = [patch(f"{m}.get_client", return_value=mock_client) for m in modules]
        for p in patches:
            p.start()
        yield mock_client
        for p in patches:
            p.stop()


# --- Help tests ---


class TestHelpOutput:
    def test_root_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "models" in result.output
        assert "projects" in result.output
        assert "monitors" in result.output

    @pytest.mark.parametrize(
        "group",
        [
            "spaces",
            "orgs",
            "users",
            "models",
            "projects",
            "monitors",
            "prompts",
            "custom-metrics",
            "evaluators",
            "dashboards",
            "imports",
            "config",
        ],
    )
    def test_group_help(self, runner, group):
        result = runner.invoke(cli, [group, "--help"])
        assert result.exit_code == 0


# --- Spaces ---


class TestSpaces:
    def test_spaces_list(self, runner, mock_client):
        mock_client.get_all_spaces.return_value = [
            {"id": "s1", "name": "space1", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["spaces", "list"])
        assert result.exit_code == 0
        mock_client.get_all_spaces.assert_called_once()

    def test_spaces_list_json(self, runner, mock_client):
        mock_client.get_all_spaces.return_value = [{"id": "s1", "name": "space1"}]
        result = runner.invoke(cli, ["--json", "spaces", "list"])
        assert result.exit_code == 0
        assert '"id"' in result.output

    def test_spaces_get(self, runner, mock_client):
        mock_client.get_space.return_value = {"id": "s1", "name": "test-space"}
        result = runner.invoke(cli, ["spaces", "get", "test-space"])
        assert result.exit_code == 0
        mock_client.get_space.assert_called_once_with("test-space")

    def test_spaces_create(self, runner, mock_client):
        mock_client.create_new_space.return_value = "space-id-123"
        result = runner.invoke(cli, ["spaces", "create", "new-space"])
        assert result.exit_code == 0
        mock_client.create_new_space.assert_called_once_with(name="new-space", private=True, set_as_active=True)


# --- Orgs ---


class TestOrgs:
    def test_orgs_list(self, runner, mock_client):
        mock_client.get_all_organizations.return_value = [
            {"id": "o1", "name": "org1", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["orgs", "list"])
        assert result.exit_code == 0
        mock_client.get_all_organizations.assert_called_once()


# --- Models / Projects ---


class TestModels:
    def test_models_list(self, runner, mock_client):
        mock_client.get_all_models.return_value = [
            {"id": "m1", "name": "model1", "modelType": "classification", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["models", "list"])
        assert result.exit_code == 0
        mock_client.get_all_models.assert_called_once()

    def test_projects_alias(self, runner, mock_client):
        mock_client.get_all_models.return_value = []
        result = runner.invoke(cli, ["projects", "list"])
        assert result.exit_code == 0
        mock_client.get_all_models.assert_called_once()

    def test_models_get(self, runner, mock_client):
        mock_client.get_model.return_value = {"id": "m1", "name": "mymodel"}
        result = runner.invoke(cli, ["models", "get", "mymodel"])
        assert result.exit_code == 0
        mock_client.get_model.assert_called_once_with(model_name="mymodel")

    def test_models_volume(self, runner, mock_client):
        mock_client.get_model_volume.return_value = {"production": 1000, "training": 500}
        result = runner.invoke(cli, ["models", "volume", "mymodel"])
        assert result.exit_code == 0
        mock_client.get_model_volume.assert_called_once()

    def test_models_total_volume(self, runner, mock_client):
        mock_client.get_total_volume.return_value = 5000
        result = runner.invoke(cli, ["models", "total-volume", "--model-name", "mymodel"])
        assert result.exit_code == 0
        assert "5000" in result.output

    def test_models_total_volume_json(self, runner, mock_client):
        mock_client.get_total_volume.return_value = 5000
        result = runner.invoke(cli, ["--json", "models", "total-volume", "--model-name", "mymodel"])
        assert result.exit_code == 0
        assert "5000" in result.output


# --- Monitors ---


class TestMonitors:
    def test_monitors_list(self, runner, mock_client):
        mock_client.get_all_monitors.return_value = [
            {"id": "mon1", "name": "monitor1", "monitorCategory": "performance", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["monitors", "list", "--model-name", "mymodel"])
        assert result.exit_code == 0
        mock_client.get_all_monitors.assert_called_once()

    def test_monitors_get(self, runner, mock_client):
        mock_client.get_monitor.return_value = {"id": "mon1", "name": "monitor1"}
        result = runner.invoke(cli, ["monitors", "get", "monitor1", "--model", "mymodel"])
        assert result.exit_code == 0
        mock_client.get_monitor.assert_called_once_with(model_name="mymodel", monitor_name="monitor1")

    def test_monitors_create_performance(self, runner, mock_client):
        mock_client.create_performance_monitor.return_value = "/monitors/123"
        result = runner.invoke(
            cli,
            [
                "monitors",
                "create-performance",
                "my-monitor",
                "--model",
                "mymodel",
                "--environment",
                "production",
                "--performance-metric",
                "accuracy",
                "--threshold",
                "0.95",
            ],
        )
        assert result.exit_code == 0
        mock_client.create_performance_monitor.assert_called_once()

    def test_monitors_delete(self, runner, mock_client):
        mock_client.delete_monitor.return_value = True
        result = runner.invoke(cli, ["monitors", "delete", "monitor1", "--model", "mymodel", "--yes"])
        assert result.exit_code == 0
        mock_client.delete_monitor.assert_called_once()


# --- Prompts ---


class TestPrompts:
    def test_prompts_list(self, runner, mock_client):
        mock_client.get_all_prompts.return_value = [
            {"id": "p1", "name": "prompt1", "description": "test", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["prompts", "list"])
        assert result.exit_code == 0
        mock_client.get_all_prompts.assert_called_once()

    def test_prompts_create(self, runner, mock_client):
        mock_client.create_prompt.return_value = True
        result = runner.invoke(
            cli,
            [
                "prompts",
                "create",
                "my-prompt",
                "--messages",
                '[{"role":"system","content":"You are helpful."}]',
            ],
        )
        assert result.exit_code == 0
        mock_client.create_prompt.assert_called_once()

    def test_prompts_delete(self, runner, mock_client):
        mock_client.delete_prompt.return_value = True
        result = runner.invoke(cli, ["prompts", "delete", "my-prompt", "--yes"])
        assert result.exit_code == 0


# --- Custom Metrics ---


class TestCustomMetrics:
    def test_custom_metrics_list(self, runner, mock_client):
        mock_client.get_all_custom_metrics.return_value = [
            {"id": "cm1", "name": "metric1", "metric": "avg(pred)", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["custom-metrics", "list", "--model-name", "mymodel"])
        assert result.exit_code == 0
        mock_client.get_all_custom_metrics.assert_called_once()

    def test_custom_metrics_create(self, runner, mock_client):
        mock_client.create_custom_metric.return_value = "/custom-metrics/123"
        result = runner.invoke(
            cli,
            [
                "custom-metrics",
                "create",
                "my-metric",
                "--metric",
                "avg(prediction)",
                "--model",
                "mymodel",
            ],
        )
        assert result.exit_code == 0
        mock_client.create_custom_metric.assert_called_once()


# --- Evaluators ---


class TestEvaluators:
    def test_evaluators_list(self, runner, mock_client):
        mock_client.get_evaluators.return_value = [
            {"id": "e1", "name": "eval1", "description": "test", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["evaluators", "list"])
        assert result.exit_code == 0
        mock_client.get_evaluators.assert_called_once()

    def test_evaluators_get(self, runner, mock_client):
        mock_client.get_evaluator.return_value = {"id": "e1", "name": "eval1"}
        result = runner.invoke(cli, ["evaluators", "get", "eval1"])
        assert result.exit_code == 0
        mock_client.get_evaluator.assert_called_once_with(name="eval1")


# --- Dashboards ---


class TestDashboards:
    def test_dashboards_list(self, runner, mock_client):
        mock_client.get_all_dashboards.return_value = [
            {"id": "d1", "name": "dash1", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["dashboards", "list"])
        assert result.exit_code == 0
        mock_client.get_all_dashboards.assert_called_once()

    def test_dashboards_create(self, runner, mock_client):
        mock_client.create_dashboard.return_value = "/dashboards/123"
        result = runner.invoke(cli, ["dashboards", "create", "my-dash"])
        assert result.exit_code == 0
        mock_client.create_dashboard.assert_called_once_with(name="my-dash")


# --- Imports ---


class TestImports:
    def test_files_list(self, runner, mock_client):
        mock_client.get_all_file_import_jobs.return_value = [
            {"id": "f1", "jobId": "j1", "jobStatus": "completed", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["imports", "files", "list"])
        assert result.exit_code == 0
        mock_client.get_all_file_import_jobs.assert_called_once()

    def test_tables_list(self, runner, mock_client):
        mock_client.get_all_table_import_jobs.return_value = [
            {"id": "t1", "jobId": "j1", "jobStatus": "running", "createdAt": "2025-01-01"},
        ]
        result = runner.invoke(cli, ["imports", "tables", "list"])
        assert result.exit_code == 0
        mock_client.get_all_table_import_jobs.assert_called_once()

    def test_files_delete(self, runner, mock_client):
        mock_client.delete_file_import_job.return_value = True
        result = runner.invoke(cli, ["imports", "files", "delete", "job-123", "--yes"])
        assert result.exit_code == 0
        mock_client.delete_file_import_job.assert_called_once_with(job_id="job-123")


# --- Config Persistence (result_callback) ---


def _write_config(path, config):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(config, f)


def _read_config(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


class TestConfigPersistence:
    """Verify that space/org changes are persisted to the config file via result_callback."""

    def test_spaces_switch_updates_profile(self, tmp_path):
        config_file = tmp_path / "config.toml"
        _write_config(
            config_file,
            {"default": {"api_key": "key", "organization": "org1", "space": "old-space"}},
        )

        mock_client = MagicMock()
        mock_client.switch_space.return_value = "https://app.arize.com/..."
        # After switch_space, the client's attributes reflect the new space
        mock_client.space = "new-space"
        mock_client.organization = "org1"

        def fake_get_client(ctx):
            ctx.obj["client"] = mock_client
            return mock_client

        runner = CliRunner()
        with (
            patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file),
            patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path),
            patch("arize_toolkit.cli.spaces.get_client", side_effect=fake_get_client),
        ):
            result = runner.invoke(cli, ["spaces", "switch", "new-space"])

        assert result.exit_code == 0
        saved = _read_config(config_file)
        assert saved["default"]["space"] == "new-space"

    def test_spaces_switch_updates_org(self, tmp_path):
        config_file = tmp_path / "config.toml"
        _write_config(
            config_file,
            {"default": {"api_key": "key", "organization": "org1", "space": "space1"}},
        )

        mock_client = MagicMock()
        mock_client.switch_space.return_value = "https://app.arize.com/..."
        mock_client.space = "space2"
        mock_client.organization = "org2"

        def fake_get_client(ctx):
            ctx.obj["client"] = mock_client
            return mock_client

        runner = CliRunner()
        with (
            patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file),
            patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path),
            patch("arize_toolkit.cli.spaces.get_client", side_effect=fake_get_client),
        ):
            result = runner.invoke(cli, ["spaces", "switch", "space2", "--org", "org2"])

        assert result.exit_code == 0
        saved = _read_config(config_file)
        assert saved["default"]["space"] == "space2"
        assert saved["default"]["organization"] == "org2"

    def test_spaces_create_persists_new_space(self, tmp_path):
        config_file = tmp_path / "config.toml"
        _write_config(
            config_file,
            {"default": {"api_key": "key", "organization": "org1", "space": "old-space"}},
        )

        mock_client = MagicMock()
        mock_client.create_new_space.return_value = "new-id"
        # After create with set_as_active=True, client.space is updated
        mock_client.space = "brand-new-space"
        mock_client.organization = "org1"

        def fake_get_client(ctx):
            ctx.obj["client"] = mock_client
            return mock_client

        runner = CliRunner()
        with (
            patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file),
            patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path),
            patch("arize_toolkit.cli.spaces.get_client", side_effect=fake_get_client),
        ):
            result = runner.invoke(cli, ["spaces", "create", "brand-new-space"])

        assert result.exit_code == 0
        saved = _read_config(config_file)
        assert saved["default"]["space"] == "brand-new-space"

    def test_no_write_when_nothing_changed(self, tmp_path):
        config_file = tmp_path / "config.toml"
        _write_config(
            config_file,
            {"default": {"api_key": "key", "organization": "org1", "space": "same-space"}},
        )

        mock_client = MagicMock()
        mock_client.get_all_spaces.return_value = [{"id": "s1", "name": "same-space", "createdAt": "2025-01-01"}]
        mock_client.space = "same-space"
        mock_client.organization = "org1"

        def fake_get_client(ctx):
            ctx.obj["client"] = mock_client
            return mock_client

        runner = CliRunner()
        with (
            patch("arize_toolkit.cli.config_cmd.CONFIG_FILE", config_file),
            patch("arize_toolkit.cli.config_cmd.CONFIG_DIR", tmp_path),
            patch("arize_toolkit.cli.spaces.get_client", side_effect=fake_get_client),
            patch("arize_toolkit.cli.config_cmd.save_config") as mock_save,
        ):
            result = runner.invoke(cli, ["spaces", "list"])

        assert result.exit_code == 0
        mock_save.assert_not_called()
