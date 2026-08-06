#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/lib-hip-deploy.sh
source "${SCRIPT_DIR}/lib-hip-deploy.sh"

hip_setup_colors
hip_load_configuration production
hip_require_base_dependencies
hip_require_token

START_EPOCH="$(hip_epoch_now)"

hip_progress 1 7 "Requesting rollback confirmation"
hip_confirm_or_abort "Rollback HIP in production container '${HIP_CONTAINER_NAME}'?"

hip_progress 2 7 "Preparing deployment state directories"
hip_validate_paths_and_runtime
hip_ensure_state_directories

TIMESTAMP="$(hip_timestamp_now)"

hip_progress 3 7 "Locating latest backup"
BACKUP_PATH="$(hip_latest_backup_for_target production)"
if [ -z "${BACKUP_PATH}" ]; then
  hip_log_error "no production backup found in /config/.storage/hip/backups"
  exit 1
fi

hip_progress 4 7 "Restoring backup"
hip_restore_backup "${BACKUP_PATH}"

hip_progress 5 7 "Restarting Home Assistant container"
hip_restart_container

hip_progress 6 7 "Waiting for Home Assistant startup"
hip_wait_for_home_assistant "${HIP_WAIT_TIMEOUT}"

hip_progress 7 7 "Running validation and smoke tests"
hip_run_validation_pipeline

ROLLED_BACK_VERSION="unknown"
METADATA_TMP="$(mktemp)"
if docker cp "${HIP_CONTAINER_NAME}:${BACKUP_PATH}/metadata.json" "${METADATA_TMP}" >/dev/null 2>&1; then
  ROLLED_BACK_VERSION="$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "${METADATA_TMP}" | head -n1 | sed 's/.*"\([^"]*\)"$/\1/')"
fi
rm -f "${METADATA_TMP}"

REPORT_TMP="$(mktemp)"
cat > "${REPORT_TMP}" <<EOF
HIP Rollback Report
Target: production
Timestamp: $(hip_iso_now)
Container: ${HIP_CONTAINER_NAME}
Backup: ${BACKUP_PATH}
Action: rollback
Version: ${ROLLED_BACK_VERSION}

Validation Result:
${HIP_VALIDATE_RESULT:-Skipped}

Smoke Test Result:
${HIP_SMOKE_RESULT:-Skipped}
EOF

REPORT_PATH="$(hip_write_status_and_report rolled_back "${ROLLED_BACK_VERSION}" "${BACKUP_PATH}" "${REPORT_TMP}" "${TIMESTAMP}")"

ELAPSED="$(($(hip_epoch_now) - START_EPOCH))"

hip_print_validation_summary
hip_print_smoke_summary

printf '%s\n' "===== HIP ROLLBACK REPORT ====="
cat "${REPORT_TMP}"
printf 'Rollback duration: %s\n' "$(hip_format_duration "${ELAPSED}")"
printf '\nReport stored in container: %s\n' "${REPORT_PATH}"
rm -f "${REPORT_TMP}"
