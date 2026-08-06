#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/lib-hip-deploy.sh
source "${SCRIPT_DIR}/lib-hip-deploy.sh"

SHOW_VERSION="false"
RUN_DOCTOR="false"

while [ "$#" -gt 0 ]; do
	case "$1" in
		--version)
			SHOW_VERSION="true"
			;;
		--dry-run)
			HIP_DRY_RUN="true"
			;;
		--doctor)
			RUN_DOCTOR="true"
			;;
		*)
			hip_log_error "unknown option: $1"
			exit 1
			;;
	esac
	shift
done

hip_setup_colors
hip_load_configuration development

if [ "${SHOW_VERSION}" = "true" ]; then
	hip_print_version_info development
	exit 0
fi

if [ "${RUN_DOCTOR}" = "true" ]; then
	hip_run_doctor
	exit $?
fi

hip_require_base_dependencies

hip_require_token

START_EPOCH="$(hip_epoch_now)"

hip_progress 1 10 "Validating configuration and environment"
hip_validate_paths_and_runtime

if [ "${HIP_DRY_RUN}" = "true" ]; then
	hip_print_dry_run_plan development
	exit 0
fi

hip_progress 2 10 "Checking git status policy"
hip_git_check_target_policy development

hip_progress 3 10 "Pulling latest changes"
hip_git_pull_if_enabled

hip_progress 4 10 "Requesting deployment confirmation"
hip_confirm_or_abort "Deploy HIP to development container '${HIP_CONTAINER_NAME}' from '${HIP_REPO_ROOT}'?"

hip_progress 5 10 "Preparing deployment state directories"
hip_ensure_state_directories

VERSION="$(tr -d '[:space:]' < "${HIP_REPO_ROOT}/VERSION")"
TIMESTAMP="$(hip_timestamp_now)"

hip_progress 6 10 "Creating backup"
BACKUP_PATH="$(hip_backup_current development "${VERSION}" "${TIMESTAMP}")"

hip_progress 7 10 "Copying runtime files"
hip_copy_runtime_files "${HIP_REPO_ROOT}"

hip_progress 8 10 "Restarting Home Assistant container"
hip_restart_container

hip_progress 9 10 "Waiting for Home Assistant startup"
hip_wait_for_home_assistant "${HIP_WAIT_TIMEOUT}"

hip_progress 10 10 "Running validation and smoke tests"
hip_run_validation_pipeline

REPORT_TMP="$(mktemp)"
cat > "${REPORT_TMP}" <<EOF
HIP Deployment Report
Target: development
Timestamp: $(hip_iso_now)
Version: ${VERSION}
Container: ${HIP_CONTAINER_NAME}
Backup: ${BACKUP_PATH}
Action: deploy

Validation Result:
${HIP_VALIDATE_RESULT:-Skipped}

Smoke Test Result:
${HIP_SMOKE_RESULT:-Skipped}
EOF

REPORT_PATH="$(hip_write_status_and_report deployed "${VERSION}" "${BACKUP_PATH}" "${REPORT_TMP}" "${TIMESTAMP}")"

ELAPSED="$(($(hip_epoch_now) - START_EPOCH))"
FORMATTED_DURATION="$(hip_format_duration "${ELAPSED}")"

hip_print_validation_summary
hip_print_smoke_summary
hip_print_deployment_summary "${FORMATTED_DURATION}" "${REPORT_PATH}" "${VERSION}"

printf '%s\n' "===== HIP DEPLOYMENT REPORT ====="
cat "${REPORT_TMP}"
printf 'Deployment duration: %s\n' "${FORMATTED_DURATION}"
printf '\nReport stored in container: %s\n' "${REPORT_PATH}"
rm -f "${REPORT_TMP}"
