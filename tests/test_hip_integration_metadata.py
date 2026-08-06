from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "custom_components" / "hip" / "manifest.json"
SERVICES = ROOT / "custom_components" / "hip" / "services.yaml"
TRANSLATIONS = ROOT / "custom_components" / "hip" / "translations" / "en.json"
TOOLS = ROOT / "tools"
CONFIG = ROOT / "config"
ROOT_DEPLOY_WRAPPERS = {
    "deploy-dev.sh",
    "deploy-prod.sh",
}

REQUIRED_SERVICES = {
    "validate",
    "reload",
    "health_check",
    "export_support_bundle",
    "run_smoke_tests",
    "version",
    "kernel_status",
    "module_status",
    "event_statistics",
    "check_updates",
    "open_release_notes",
    "deployment_status",
}

REQUIRED_DEPLOYMENT_SCRIPTS = {
    "deploy-dev.sh",
    "deploy-prod.sh",
    "rollback-dev.sh",
    "rollback-prod.sh",
    "validate.sh",
}

REQUIRED_DEPLOYMENT_ENV_FILES = {
    "dev.env.example",
    "prod.env.example",
}


def test_manifest_declares_config_flow_and_domain() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["domain"] == "hip"
    assert manifest["config_flow"] is True
    assert manifest["version"] == "2.5.3"


def test_services_yaml_contains_required_service_names() -> None:
    content = SERVICES.read_text(encoding="utf-8")
    for service in REQUIRED_SERVICES:
        assert f"{service}:" in content


def test_translations_expose_runtime_health_issue() -> None:
    data = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    assert "issues" in data
    assert "runtime_health" in data["issues"]


def test_required_deployment_scripts_exist() -> None:
    for script_name in REQUIRED_DEPLOYMENT_SCRIPTS:
        script_path = TOOLS / script_name
        assert script_path.exists()
        content = script_path.read_text(encoding="utf-8")
        assert content.startswith("#!/usr/bin/env bash")


def test_required_deployment_env_files_exist() -> None:
    for env_name in REQUIRED_DEPLOYMENT_ENV_FILES:
        env_path = CONFIG / env_name
        assert env_path.exists()
        content = env_path.read_text(encoding="utf-8")
        assert "HIP_HA_TOKEN=" in content
        assert "HIP_REPOSITORY=" in content
        assert "HIP_CONFIG_PATH=" in content
        assert "HIP_REQUIRE_CLEAN_TREE=" in content


def test_gitignore_excludes_machine_specific_env_files() -> None:
    ignore_content = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "config/dev.env" in ignore_content
    assert "config/prod.env" in ignore_content
    assert "/mnt/apps/configs/hip/" in ignore_content


def test_deployment_library_uses_external_configuration_directory() -> None:
    content = (TOOLS / "lib-hip-deploy.sh").read_text(encoding="utf-8")
    assert "HIP_DEFAULT_CONFIG_DIR=\"/mnt/apps/configs/hip\"" in content
    assert "HIP_CONFIG_DIR" in content
    assert "HIP_RUNTIME_PACKAGES_DIR=\"/config/packages\"" in content


def test_no_templated_entity_id_in_state_triggers_or_conditions() -> None:
    pattern = re.compile(
        r"(?:condition:\\s*state|platform:\\s*state)[\\s\\S]{0,260}?entity_id:\\s*\\\"\\{\\{",
        re.IGNORECASE,
    )
    for yaml_path in ROOT.glob("homeassistant/packages/**/*.yaml"):
        content = yaml_path.read_text(encoding="utf-8")
        assert pattern.search(content) is None, f"templated state entity_id found in {yaml_path}"


def test_root_deploy_wrappers_exist() -> None:
    for script_name in ROOT_DEPLOY_WRAPPERS:
        script_path = ROOT / script_name
        assert script_path.exists()
        content = script_path.read_text(encoding="utf-8")
        assert "tools/" in content
