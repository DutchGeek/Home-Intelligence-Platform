from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[import-not-found]

from tools.hip_package_compiler import (
    DuplicateDomainError,
    DuplicateEntityIdError,
    MalformedYamlError,
    compile_packages,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_compile_packages_successful_merge(tmp_path: Path) -> None:
    source = tmp_path / "homeassistant" / "packages"
    output = tmp_path / "build" / "packages"
    report = tmp_path / "build" / "package-report.json"

    _write(
        source / "testpkg" / "helpers.yaml",
        "input_text:\n  helper_one:\n    name: Helper One\n",
    )
    _write(
        source / "testpkg" / "scripts.yaml",
        "script:\n  test_script:\n    alias: Test Script\n    sequence: []\n",
    )

    artifacts, compile_report = compile_packages(source, output, report)

    assert [artifact.package_name for artifact in artifacts] == ["testpkg"]
    assert compile_report.compiled_package_count == 1
    assert compile_report.skipped_package_count == 0
    assert compile_report.warning_count == 0
    assert report.exists()
    rendered = (output / "testpkg.yaml").read_text(encoding="utf-8")
    assert "input_text:" in rendered
    assert "script:" in rendered
    assert "test_script:" in rendered


def test_compile_packages_detects_duplicate_top_level_domains(tmp_path: Path) -> None:
    source = tmp_path / "homeassistant" / "packages"
    output = tmp_path / "build" / "packages"
    report = tmp_path / "build" / "package-report.json"

    _write(
        source / "dup_pkg" / "helpers_a.yaml",
        "input_text:\n  helper_one:\n    name: Helper One\n",
    )
    _write(
        source / "dup_pkg" / "helpers_b.yaml",
        "input_text:\n  helper_two:\n    name: Helper Two\n",
    )

    with pytest.raises(DuplicateDomainError):
        compile_packages(source, output, report)


def test_compile_packages_detects_duplicate_entity_ids(tmp_path: Path) -> None:
    source = tmp_path / "homeassistant" / "packages"
    output = tmp_path / "build" / "packages"
    report = tmp_path / "build" / "package-report.json"

    _write(
        source / "dup_ids" / "automations.yaml",
        "automation:\n"
        "  - id: duplicate_id\n"
        "    alias: First\n"
        "    trigger: []\n"
        "    action: []\n"
        "  - id: duplicate_id\n"
        "    alias: Second\n"
        "    trigger: []\n"
        "    action: []\n",
    )

    with pytest.raises(DuplicateEntityIdError):
        compile_packages(source, output, report)


def test_compile_packages_skips_empty_package(tmp_path: Path) -> None:
    source = tmp_path / "homeassistant" / "packages"
    output = tmp_path / "build" / "packages"
    report = tmp_path / "build" / "package-report.json"

    (source / "empty_pkg").mkdir(parents=True)
    _write(
        source / "valid_pkg" / "helpers.yaml",
        "input_text:\n  helper_one:\n    name: Helper One\n",
    )

    artifacts, compile_report = compile_packages(source, output, report)

    assert [artifact.package_name for artifact in artifacts] == ["valid_pkg"]
    assert compile_report.skipped_package_count == 1
    assert compile_report.warning_count == 1
    assert "Skipping empty package 'empty_pkg'" in compile_report.warnings
    assert report.exists()


def test_compile_packages_rejects_malformed_yaml(tmp_path: Path) -> None:
    source = tmp_path / "homeassistant" / "packages"
    output = tmp_path / "build" / "packages"
    report = tmp_path / "build" / "package-report.json"

    _write(source / "broken_pkg" / "scripts.yaml", "script:\n  bad: [\n")

    with pytest.raises(MalformedYamlError):
        compile_packages(source, output, report)