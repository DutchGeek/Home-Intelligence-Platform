from __future__ import annotations

# pyright: reportMissingTypeStubs=false

import argparse
import json
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml  # type: ignore[import-not-found]
from yaml.constructor import ConstructorError  # type: ignore[import-not-found]


class PackageCompilerError(Exception):
    """Base error for package compilation failures."""


class DuplicateDomainError(PackageCompilerError):
    """Raised when a package declares the same top-level domain twice."""


class DuplicateEntityIdError(PackageCompilerError):
    """Raised when a list-based domain contains duplicate entity IDs."""


class MalformedYamlError(PackageCompilerError):
    """Raised when a YAML file cannot be parsed."""


class StrictYamlLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: StrictYamlLoader, node: yaml.nodes.MappingNode) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key ({key})",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node)
    return mapping


StrictYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(slots=True)
class PackageArtifact:
    package_name: str
    output_path: Path
    merged_config: dict[str, Any]


@dataclass(slots=True)
class PackageCompileReport:
    package_name: str
    source_directory: str
    generated_file: str | None
    domains: list[str]
    entity_counts_per_domain: dict[str, int]
    warnings: list[str]
    compile_duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_name": self.package_name,
            "source_directory": self.source_directory,
            "generated_file": self.generated_file,
            "domains": self.domains,
            "entity_counts_per_domain": self.entity_counts_per_domain,
            "warnings": self.warnings,
            "compile_duration_ms": self.compile_duration_ms,
        }


@dataclass(slots=True)
class CompilerReport:
    source_root: str
    output_root: str
    report_path: str
    compile_duration_ms: int
    compiled_package_count: int
    skipped_package_count: int
    warning_count: int
    warnings: list[str]
    packages: list[PackageCompileReport]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_root": self.source_root,
            "output_root": self.output_root,
            "report_path": self.report_path,
            "compile_duration_ms": self.compile_duration_ms,
            "compiled_package_count": self.compiled_package_count,
            "skipped_package_count": self.skipped_package_count,
            "warning_count": self.warning_count,
            "warnings": self.warnings,
            "packages": [package.to_dict() for package in self.packages],
        }


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    try:
        raw = yaml.load(file_path.read_text(encoding="utf-8"), Loader=StrictYamlLoader)
    except yaml.YAMLError as exc:
        raise MalformedYamlError(f"malformed YAML in {file_path}: {exc}") from exc

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise MalformedYamlError(
            f"YAML document must be a mapping at top-level in {file_path}"
        )
    return raw


def _validate_list_domain_ids(
    package_name: str,
    domain: str,
    domain_value: Any,
    fragment_path: Path,
) -> None:
    if not isinstance(domain_value, list):
        return

    seen_ids: dict[str, int] = {}
    for index, item in enumerate(domain_value):
        if not isinstance(item, dict):
            continue
        if "id" not in item:
            continue

        entity_id = item["id"]
        if entity_id in (None, ""):
            continue

        entity_id_text = str(entity_id)
        if entity_id_text in seen_ids:
            first_index = seen_ids[entity_id_text]
            raise DuplicateEntityIdError(
                "duplicate entity id in package "
                f"'{package_name}' domain '{domain}' from {fragment_path}: "
                f"id '{entity_id_text}' appears at list indexes {first_index} and {index}"
            )
        seen_ids[entity_id_text] = index


def _iter_package_directories(source_root: Path) -> Iterable[Path]:
    return sorted(
        (path for path in source_root.iterdir() if path.is_dir() and not path.name.startswith(".")),
        key=lambda path: path.name,
    )


def _entity_count(value: Any) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 1


def _remove_tree(path: Path) -> None:
    if not path.exists():
        return

    def _onerror(function: Any, function_path: str, exc_info: tuple[type[BaseException], BaseException, Any]) -> None:
        del function
        del function_path
        _, exc, _ = exc_info
        raise PackageCompilerError(f"failed to remove directory '{path}': {exc}") from exc

    shutil.rmtree(path, onerror=_onerror)


def compile_package(package_dir: Path) -> tuple[dict[str, Any], list[str]]:
    package_name = package_dir.name
    fragments = sorted(
        package_dir.rglob("*.yaml"),
        key=lambda path: path.relative_to(package_dir).as_posix(),
    )
    warnings: list[str] = []
    if not fragments:
        warnings.append(f"Skipping empty package '{package_name}'")
        return {}, warnings

    merged: dict[str, Any] = {}
    domain_sources: dict[str, Path] = {}

    for fragment in fragments:
        fragment_data = _load_yaml_file(fragment)
        for domain, domain_value in fragment_data.items():
            if domain in merged:
                first_source = domain_sources[domain]
                raise DuplicateDomainError(
                    "duplicate top-level domain in package "
                    f"'{package_name}': '{domain}' appears in both {first_source} and {fragment}"
                )
            _validate_list_domain_ids(package_name, str(domain), domain_value, fragment)
            merged[str(domain)] = domain_value
            domain_sources[str(domain)] = fragment

    if not merged:
        warnings.append(f"Skipping empty package '{package_name}'")
        return {}, warnings

    return merged, warnings


def compile_packages(
    source_root: Path,
    output_root: Path,
    report_path: Path | None = None,
) -> tuple[list[PackageArtifact], CompilerReport]:
    started = perf_counter()
    if not source_root.exists() or not source_root.is_dir():
        raise PackageCompilerError(f"source package root not found: {source_root}")

    package_dirs = list(_iter_package_directories(source_root))
    if not package_dirs:
        raise PackageCompilerError(f"no package directories found in {source_root}")

    staging_root = output_root.parent / f".{output_root.name}.tmp"
    _remove_tree(staging_root)
    staging_root.mkdir(parents=True, exist_ok=True)

    resolved_report_path = report_path or (output_root.parent / "package-report.json")
    all_warnings: list[str] = []
    package_reports: list[PackageCompileReport] = []

    artifacts: list[PackageArtifact] = []
    for package_dir in package_dirs:
        package_started = perf_counter()
        merged, warnings = compile_package(package_dir)
        package_duration_ms = int((perf_counter() - package_started) * 1000)
        all_warnings.extend(warnings)

        if not merged:
            package_reports.append(
                PackageCompileReport(
                    package_name=package_dir.name,
                    source_directory=str(package_dir),
                    generated_file=None,
                    domains=[],
                    entity_counts_per_domain={},
                    warnings=warnings,
                    compile_duration_ms=package_duration_ms,
                )
            )
            continue

        staging_output_file = staging_root / f"{package_dir.name}.yaml"
        output_file = output_root / f"{package_dir.name}.yaml"
        rendered = yaml.safe_dump(
            merged,
            sort_keys=True,
            default_flow_style=False,
            allow_unicode=False,
        )
        staging_output_file.write_text(rendered, encoding="utf-8")
        artifacts.append(PackageArtifact(package_dir.name, output_file, merged))

        package_reports.append(
            PackageCompileReport(
                package_name=package_dir.name,
                source_directory=str(package_dir),
                generated_file=str(output_file),
                domains=sorted(merged.keys()),
                entity_counts_per_domain={
                    domain: _entity_count(value) for domain, value in sorted(merged.items())
                },
                warnings=warnings,
                compile_duration_ms=package_duration_ms,
            )
        )

    total_duration_ms = int((perf_counter() - started) * 1000)
    compiled_count = len(artifacts)
    skipped_count = sum(1 for report in package_reports if report.generated_file is None)

    compiler_report = CompilerReport(
        source_root=str(source_root),
        output_root=str(output_root),
        report_path=str(resolved_report_path),
        compile_duration_ms=total_duration_ms,
        compiled_package_count=compiled_count,
        skipped_package_count=skipped_count,
        warning_count=len(all_warnings),
        warnings=all_warnings,
        packages=package_reports,
    )

    backup_root = output_root.parent / f".{output_root.name}.previous"
    _remove_tree(backup_root)

    try:
        if output_root.exists():
            output_root.rename(backup_root)
        staging_root.rename(output_root)
        _remove_tree(backup_root)
    except OSError as exc:
        if not output_root.exists() and backup_root.exists():
            backup_root.rename(output_root)
        _remove_tree(staging_root)
        raise PackageCompilerError(
            f"failed to promote compiled artifacts to {output_root}: {exc}"
        ) from exc

    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(json.dumps(compiler_report.to_dict(), indent=2), encoding="utf-8")

    return artifacts, compiler_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile HIP package fragments into Home Assistant-compatible package files")
    parser.add_argument("--source", required=True, help="Path to source package directories")
    parser.add_argument("--output", required=True, help="Path to compiled output directory")
    parser.add_argument("--report", required=False, help="Path to package compilation report JSON")
    args = parser.parse_args()

    source_root = Path(args.source).resolve()
    output_root = Path(args.output).resolve()

    report_path = Path(args.report).resolve() if args.report else None

    try:
        artifacts, compile_report = compile_packages(source_root, output_root, report_path)
    except PackageCompilerError as exc:
        print(f"HIP package compilation failed: {exc}")
        return 1

    print(f"Compiled {len(artifacts)} HIP packages to {output_root}")
    for artifact in artifacts:
        print(f"- {artifact.package_name}: {artifact.output_path}")
    for warning in compile_report.warnings:
        print(f"WARNING: {warning}")
    print(f"Package report: {compile_report.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())