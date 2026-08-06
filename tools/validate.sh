#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/lib-hip-deploy.sh
source "${SCRIPT_DIR}/lib-hip-deploy.sh"

hip_setup_colors

TARGET="${HIP_DEPLOY_TARGET:-development}"
hip_load_configuration "${TARGET}"

hip_require_base_dependencies
hip_require_token

START_EPOCH="$(hip_epoch_now)"

hip_progress 1 3 "Preparing deployment state directories"
hip_validate_paths_and_runtime
hip_ensure_state_directories

TIMESTAMP="$(hip_timestamp_now)"

hip_progress 2 3 "Running validation and smoke tests"
VALIDATION_OK="true"
if ! hip_run_validation_pipeline; then
	VALIDATION_OK="false"
fi

CURRENT_VERSION="$(tr -d '[:space:]' < "${HIP_REPO_ROOT}/VERSION")"
BACKUP_PATH="$(hip_latest_backup_for_target "${TARGET}")"

hip_progress 3 3 "Writing validation report"

REPORT_TMP="$(mktemp)"
cat > "${REPORT_TMP}" <<EOF
HIP Validation Report
Target: ${TARGET}
Timestamp: $(hip_iso_now)
Container: ${HIP_CONTAINER_NAME}
Action: validate
Version: ${CURRENT_VERSION}

Validation Result:
${HIP_VALIDATE_RESULT:-Skipped}

Smoke Test Result:
${HIP_SMOKE_RESULT:-Skipped}
EOF

REPORT_PATH="$(hip_write_status_and_report validated "${CURRENT_VERSION}" "${BACKUP_PATH}" "${REPORT_TMP}" "${TIMESTAMP}")"

ELAPSED="$(($(hip_epoch_now) - START_EPOCH))"

hip_print_validation_summary
hip_print_smoke_summary

printf '%s\n' "===== HIP VALIDATION REPORT ====="
cat "${REPORT_TMP}"
printf 'Validation duration: %s\n' "$(hip_format_duration "${ELAPSED}")"
printf '\nReport stored in container: %s\n' "${REPORT_PATH}"
rm -f "${REPORT_TMP}"

if [ "${VALIDATION_OK}" != "true" ]; then
	exit 1
fi
