#!/usr/bin/env bash
set -euo pipefail

HIP_REPO_ROOT="${HIP_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
HIP_DEPLOY_TARGET="${HIP_DEPLOY_TARGET:-}"
HIP_HA_URL="${HIP_HA_URL:-}"
HIP_HA_TOKEN="${HIP_HA_TOKEN:-}"
HIP_CONTAINER_NAME="${HIP_CONTAINER_NAME:-}"
HIP_WAIT_TIMEOUT="${HIP_WAIT_TIMEOUT:-300}"
HIP_GIT_REMOTE="${HIP_GIT_REMOTE:-origin}"
HIP_GIT_BRANCH="${HIP_GIT_BRANCH:-main}"
HIP_GIT_PULL="${HIP_GIT_PULL:-true}"
HIP_CONFIRM_DEPLOYMENT="${HIP_CONFIRM_DEPLOYMENT:-true}"
HIP_DRY_RUN="false"
HIP_CONFIGURATION_FILE=""

HIP_VALIDATE_RESULT=""
HIP_SMOKE_RESULT=""
HIP_VALIDATION_STATUS="NOT_RUN"
HIP_SMOKE_STATUS="NOT_RUN"

C_RESET=""
C_BOLD=""
C_RED=""
C_GREEN=""
C_YELLOW=""
C_BLUE=""
C_CYAN=""

hip_setup_colors() {
  if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_RED='\033[31m'
    C_GREEN='\033[32m'
    C_YELLOW='\033[33m'
    C_BLUE='\033[34m'
    C_CYAN='\033[36m'
  fi
}

hip_log_info() {
  printf '%b[INFO]%b %s\n' "${C_BLUE}" "${C_RESET}" "$*"
}

hip_log_ok() {
  printf '%b[ OK ]%b %s\n' "${C_GREEN}" "${C_RESET}" "$*"
}

hip_log_warn() {
  printf '%b[WARN]%b %s\n' "${C_YELLOW}" "${C_RESET}" "$*"
}

hip_log_error() {
  printf '%b[FAIL]%b %s\n' "${C_RED}" "${C_RESET}" "$*" >&2
}

hip_progress() {
  local current="$1"
  local total="$2"
  shift 2
  printf '%b[%s/%s]%b %s\n' "${C_CYAN}" "${current}" "${total}" "${C_RESET}" "$*"
}

hip_require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    hip_log_error "required command not found: $cmd"
    exit 1
  fi
}

hip_require_base_dependencies() {
  hip_require_command docker
  hip_require_command curl
  hip_require_command git
}

hip_has_command() {
  command -v "$1" >/dev/null 2>&1
}

hip_require_token() {
  if [ -z "$HIP_HA_TOKEN" ]; then
    hip_log_error "HIP_HA_TOKEN is not configured in ${HIP_CONFIGURATION_FILE}"
    exit 1
  fi
}

hip_iso_now() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

hip_timestamp_now() {
  date -u +"%Y%m%d%H%M%S"
}

hip_epoch_now() {
  date +%s
}

hip_format_duration() {
  local elapsed="$1"
  local mins secs
  mins=$(( elapsed / 60 ))
  secs=$(( elapsed % 60 ))
  printf '%02dm:%02ds' "$mins" "$secs"
}

hip_load_configuration() {
  local target="$1"
  local env_rel example_rel env_file example_file

  case "$target" in
    development)
      env_rel="config/dev.env"
      example_rel="config/dev.env.example"
      ;;
    production)
      env_rel="config/prod.env"
      example_rel="config/prod.env.example"
      ;;
    *)
      hip_log_error "unsupported deployment target: $target"
      exit 1
      ;;
  esac

  env_file="${HIP_REPO_ROOT}/${env_rel}"
  example_file="${HIP_REPO_ROOT}/${example_rel}"

  if [ ! -f "${env_file}" ]; then
    if [ ! -f "${example_file}" ]; then
      hip_log_error "missing example configuration file: ${example_rel}"
      exit 1
    fi
    cp "${example_file}" "${env_file}"
    hip_log_warn "created ${env_rel} from ${example_rel}"
    printf 'Please edit %s before deploying.\n' "${env_rel}"
    exit 0
  fi

  HIP_CONFIGURATION_FILE="${env_rel}"
  hip_log_info "loading configuration from ${env_rel}"
  set -a
  # shellcheck disable=SC1090
  . "${env_file}"
  set +a

  HIP_DEPLOY_TARGET="${target}"
}

hip_get_git_branch() {
  git -C "${HIP_REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown'
}

hip_get_git_commit() {
  git -C "${HIP_REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || printf 'unknown'
}

hip_confirm_or_abort() {
  local message="$1"
  if [ "${HIP_CONFIRM_DEPLOYMENT}" != "true" ]; then
    hip_log_info "confirmation disabled (HIP_CONFIRM_DEPLOYMENT=${HIP_CONFIRM_DEPLOYMENT})"
    return 0
  fi

  if [ ! -t 0 ]; then
    hip_log_error "interactive confirmation required but stdin is not a terminal"
    exit 1
  fi

  printf '%b%s%b [y/N]: ' "${C_BOLD}" "${message}" "${C_RESET}"
  read -r answer
  case "${answer}" in
    y|Y|yes|YES)
      hip_log_ok "confirmation accepted"
      ;;
    *)
      hip_log_warn "operation cancelled by user"
      exit 0
      ;;
  esac
}

hip_git_is_clean() {
  git -C "${HIP_REPO_ROOT}" diff --quiet --ignore-submodules -- && \
    git -C "${HIP_REPO_ROOT}" diff --cached --quiet --ignore-submodules --
}

hip_git_check_target_policy() {
  local target="$1"
  if hip_git_is_clean; then
    hip_log_ok "git working tree is clean"
    return 0
  fi

  case "${target}" in
    production)
      hip_log_error "dirty git working tree is not allowed for production deployment"
      git -C "${HIP_REPO_ROOT}" status --short
      exit 1
      ;;
    development)
      hip_log_warn "dirty git working tree detected for development deployment"
      git -C "${HIP_REPO_ROOT}" status --short
      hip_confirm_or_abort "Continue development deployment with uncommitted changes?"
      ;;
  esac
}

hip_git_pull_if_enabled() {
  if [ "${HIP_GIT_PULL}" != "true" ]; then
    hip_log_info "skipping git pull because HIP_GIT_PULL=${HIP_GIT_PULL}"
    return 0
  fi

  if ! hip_git_is_clean; then
    hip_log_warn "skipping git pull because working tree is dirty"
    return 0
  fi

  hip_log_info "running git pull --ff-only ${HIP_GIT_REMOTE} ${HIP_GIT_BRANCH}"
  git -C "${HIP_REPO_ROOT}" fetch "${HIP_GIT_REMOTE}" "${HIP_GIT_BRANCH}"
  git -C "${HIP_REPO_ROOT}" pull --ff-only "${HIP_GIT_REMOTE}" "${HIP_GIT_BRANCH}"
  hip_log_ok "repository updated"
}

hip_validate_paths_and_runtime() {
  local errors=()

  if [ ! -d "${HIP_REPO_ROOT}" ]; then
    errors+=("Repository does not exist: ${HIP_REPO_ROOT}")
  fi

  if ! git -C "${HIP_REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    errors+=("Repository is not a git working tree: ${HIP_REPO_ROOT}")
  fi

  if [ -z "${HIP_CONTAINER_NAME}" ]; then
    errors+=("Configured container is empty in ${HIP_CONFIGURATION_FILE}")
  fi

  if [ -z "${HIP_HA_URL}" ]; then
    errors+=("Configured Home Assistant URL is empty in ${HIP_CONFIGURATION_FILE}")
  fi

  if [ -z "${HIP_HA_TOKEN}" ]; then
    errors+=("HIP_HA_TOKEN is empty in ${HIP_CONFIGURATION_FILE}")
  fi

  if ! docker inspect "${HIP_CONTAINER_NAME}" >/dev/null 2>&1; then
    errors+=("Docker container does not exist: ${HIP_CONTAINER_NAME}")
  fi

  if docker inspect "${HIP_CONTAINER_NAME}" >/dev/null 2>&1; then
    if ! docker exec "${HIP_CONTAINER_NAME}" sh -c "test -d /config" >/dev/null 2>&1; then
      errors+=("Configuration directory does not exist in container ${HIP_CONTAINER_NAME}: /config")
    fi
    if ! docker exec "${HIP_CONTAINER_NAME}" sh -c "test -w /config" >/dev/null 2>&1; then
      errors+=("Configuration directory is not writable in container ${HIP_CONTAINER_NAME}: /config")
    fi
  fi

  if [ "${#errors[@]}" -gt 0 ]; then
    hip_log_error "preflight validation failed"
    local err
    for err in "${errors[@]}"; do
      hip_log_error "- ${err}"
    done
    exit 1
  fi

  hip_log_ok "preflight validation passed"
}

hip_wait_for_home_assistant() {
  local timeout_seconds="${1:-$HIP_WAIT_TIMEOUT}"
  local start
  start="$(date +%s)"

  while true; do
    if curl -fsS -o /dev/null -H "Authorization: Bearer ${HIP_HA_TOKEN}" "${HIP_HA_URL}/api/"; then
      return 0
    fi
    if [ $(( $(date +%s) - start )) -ge "${timeout_seconds}" ]; then
      hip_log_error "timed out waiting for Home Assistant startup after ${timeout_seconds}s"
      return 1
    fi
    sleep 3
  done
}

hip_service_available() {
  local domain="${1%%/*}"
  local service="${1##*/}"
  local payload

  if ! payload="$(curl -fsS -H "Authorization: Bearer ${HIP_HA_TOKEN}" -H "Content-Type: application/json" "${HIP_HA_URL}/api/services" 2>/dev/null)"; then
    return 1
  fi

  printf '%s' "${payload}" | grep -q "\"domain\"[[:space:]]*:[[:space:]]*\"${domain}\"" && \
    printf '%s' "${payload}" | grep -q "\"service\"[[:space:]]*:[[:space:]]*\"${service}\""
}

hip_call_service() {
  local service_path="$1"
  local payload="${2:-{}}"
  local url_with_response="${HIP_HA_URL}/api/services/${service_path}?return_response"
  local url_plain="${HIP_HA_URL}/api/services/${service_path}"
  local response

  if response="$(curl -fsS -H "Authorization: Bearer ${HIP_HA_TOKEN}" -H "Content-Type: application/json" -X POST -d "${payload}" "${url_with_response}" 2>/dev/null)"; then
    printf '%s' "${response}"
    return 0
  fi

  curl -fsS \
    -H "Authorization: Bearer ${HIP_HA_TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST \
    -d "${payload}" \
    "${url_plain}"
}

hip_run_validation_pipeline() {
  HIP_VALIDATE_RESULT=""
  HIP_SMOKE_RESULT=""
  HIP_VALIDATION_STATUS="NOT_RUN"
  HIP_SMOKE_STATUS="NOT_RUN"

  if ! hip_service_available "hip/validate" || ! hip_service_available "hip/run_smoke_tests"; then
    printf 'HIP services not available yet.\nSkipping validation.\n'
    HIP_VALIDATION_STATUS="SKIPPED"
    HIP_SMOKE_STATUS="SKIPPED"
    return 0
  fi

  HIP_VALIDATE_RESULT="$(hip_call_service "hip/validate" '{}')"
  HIP_SMOKE_RESULT="$(hip_call_service "hip/run_smoke_tests" '{}')"

  if printf '%s' "${HIP_VALIDATE_RESULT}" | grep -q '"runtime_healthy"[[:space:]]*:[[:space:]]*true'; then
    HIP_VALIDATION_STATUS="PASS"
  else
    HIP_VALIDATION_STATUS="WARN"
  fi

  if printf '%s' "${HIP_SMOKE_RESULT}" | grep -q '"passed"[[:space:]]*:[[:space:]]*true'; then
    HIP_SMOKE_STATUS="PASS"
  else
    HIP_SMOKE_STATUS="WARN"
  fi
}

hip_restart_container() {
  docker restart "${HIP_CONTAINER_NAME}" >/dev/null
}

hip_ensure_state_directories() {
  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p /config/.storage/hip/backups /config/.storage/hip/reports /config/.storage/hip"
}

hip_backup_current() {
  local target="$1"
  local version="$2"
  local timestamp="$3"
  local backup_path="/config/.storage/hip/backups/${timestamp}_${target}_${version}"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p '${backup_path}/custom_components' '${backup_path}/homeassistant/packages' '${backup_path}/homeassistant/dashboards' '${backup_path}/hip'"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/custom_components/hip ]; then cp -a /config/custom_components/hip '${backup_path}/custom_components/hip'; fi"

  local pkg
  for pkg in hip_core security notifications media cameras device_registry visitor_intelligence test ai; do
    docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/homeassistant/packages/${pkg} ]; then cp -a /config/homeassistant/packages/${pkg} '${backup_path}/homeassistant/packages/${pkg}'; fi"
  done

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -f /config/homeassistant/dashboards/HIP-Dashboard.yaml ]; then cp -a /config/homeassistant/dashboards/HIP-Dashboard.yaml '${backup_path}/homeassistant/dashboards/HIP-Dashboard.yaml'; fi"
  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/hip ]; then cp -a /config/hip/. '${backup_path}/hip/'; fi"

  local metadata_tmp
  metadata_tmp="$(mktemp)"
  cat > "${metadata_tmp}" <<EOF
{
  "backup_created_at": "$(hip_iso_now)",
  "deployment_target": "${target}",
  "version": "${version}"
}
EOF
  docker cp "${metadata_tmp}" "${HIP_CONTAINER_NAME}:${backup_path}/metadata.json" >/dev/null
  rm -f "${metadata_tmp}"

  printf '%s' "${backup_path}"
}

hip_copy_runtime_files() {
  local repo_root="$1"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p /config/custom_components /config/homeassistant/packages /config/homeassistant/dashboards"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/custom_components/hip"
  docker cp "${repo_root}/custom_components/hip" "${HIP_CONTAINER_NAME}:/config/custom_components/hip"

  local pkg
  for pkg in hip_core security notifications media cameras device_registry visitor_intelligence test ai; do
    if [ -d "${repo_root}/homeassistant/packages/${pkg}" ]; then
      docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/homeassistant/packages/${pkg}"
      docker cp "${repo_root}/homeassistant/packages/${pkg}" "${HIP_CONTAINER_NAME}:/config/homeassistant/packages/${pkg}"
    fi
  done

  if [ -f "${repo_root}/homeassistant/dashboards/HIP-Dashboard.yaml" ]; then
    docker cp "${repo_root}/homeassistant/dashboards/HIP-Dashboard.yaml" "${HIP_CONTAINER_NAME}:/config/homeassistant/dashboards/HIP-Dashboard.yaml"
  fi

  if [ -d "${repo_root}/hip" ]; then
    docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/hip && mkdir -p /config/hip"
    docker cp "${repo_root}/hip/." "${HIP_CONTAINER_NAME}:/config/hip"
  fi
}

hip_restore_backup() {
  local backup_path="$1"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ ! -d '${backup_path}' ]; then echo 'ERROR: backup path not found: ${backup_path}' >&2; exit 1; fi"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/custom_components/hip"
  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d '${backup_path}/custom_components/hip' ]; then cp -a '${backup_path}/custom_components/hip' /config/custom_components/hip; fi"

  local pkg
  for pkg in hip_core security notifications media cameras device_registry visitor_intelligence test ai; do
    docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/homeassistant/packages/${pkg}"
    docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d '${backup_path}/homeassistant/packages/${pkg}' ]; then cp -a '${backup_path}/homeassistant/packages/${pkg}' /config/homeassistant/packages/${pkg}; fi"
  done

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -f '${backup_path}/homeassistant/dashboards/HIP-Dashboard.yaml' ]; then cp -a '${backup_path}/homeassistant/dashboards/HIP-Dashboard.yaml' /config/homeassistant/dashboards/HIP-Dashboard.yaml; fi"
  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d '${backup_path}/hip' ]; then rm -rf /config/hip && mkdir -p /config/hip && cp -a '${backup_path}/hip/.' /config/hip/; fi"
}

hip_latest_backup_for_target() {
  local target="$1"
  docker exec "${HIP_CONTAINER_NAME}" sh -c "ls -1dt /config/.storage/hip/backups/*_${target}_* 2>/dev/null | head -n 1"
}

hip_write_status_and_report() {
  local status="$1"
  local version="$2"
  local backup_path="$3"
  local report_content_file="$4"
  local timestamp="$5"

  local report_path="/config/.storage/hip/reports/deployment_${timestamp}.txt"
  docker cp "${report_content_file}" "${HIP_CONTAINER_NAME}:${report_path}" >/dev/null

  local existing_latest=""
  local state_tmp_read
  state_tmp_read="$(mktemp)"
  if docker cp "${HIP_CONTAINER_NAME}:/config/.storage/hip/manager_state.json" "${state_tmp_read}" >/dev/null 2>&1; then
    existing_latest="$(grep -o '"latest_release_url"[[:space:]]*:[[:space:]]*"[^"]*"' "${state_tmp_read}" | head -n1 | sed 's/.*"\([^"]*\)"$/\1/')"
  fi
  rm -f "${state_tmp_read}"

  local state_tmp
  state_tmp="$(mktemp)"
  cat > "${state_tmp}" <<EOF
{
  "update_status": "${status}",
  "in_progress": false,
  "last_deployment": "$(hip_iso_now)",
  "last_deployment_version": "${version}",
  "last_validation": "$(hip_iso_now)",
  "last_report_path": "${report_path}",
  "previous_backup_path": "${backup_path}",
  "latest_release_url": "${existing_latest}"
}
EOF
  docker cp "${state_tmp}" "${HIP_CONTAINER_NAME}:/config/.storage/hip/manager_state.json" >/dev/null
  rm -f "${state_tmp}"

  printf '%s' "${report_path}"
}

hip_print_validation_summary() {
  hip_log_info "Validation: ${HIP_VALIDATION_STATUS}"
}

hip_print_smoke_summary() {
  hip_log_info "Smoke Tests: ${HIP_SMOKE_STATUS}"
}

hip_print_deployment_summary() {
  local duration="$1"
  local report_path="$2"
  local version="$3"

  printf '%b==== HIP Deployment Summary ====%b\n' "${C_BOLD}${C_CYAN}" "${C_RESET}"
  printf '%bHIP Version:%b %s\n' "${C_BOLD}" "${C_RESET}" "${version}"
  printf '%bGit Commit:%b %s\n' "${C_BOLD}" "${C_RESET}" "$(hip_get_git_commit)"
  printf '%bGit Branch:%b %s\n' "${C_BOLD}" "${C_RESET}" "$(hip_get_git_branch)"
  printf '%bDeployment Target:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_DEPLOY_TARGET}"
  printf '%bContainer:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_CONTAINER_NAME}"
  printf '%bRepository:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_REPO_ROOT}"
  printf '%bConfiguration Path:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_CONFIGURATION_FILE}"
  printf '%bValidation:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_VALIDATION_STATUS}"
  printf '%bSmoke Tests:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_SMOKE_STATUS}"
  printf '%bDeployment Duration:%b %s\n' "${C_BOLD}" "${C_RESET}" "${duration}"
  printf '%bReport Location:%b %s\n' "${C_BOLD}" "${C_RESET}" "${report_path}"
}

hip_print_version_info() {
  local target="$1"
  local version="unknown"

  if [ -f "${HIP_REPO_ROOT}/VERSION" ]; then
    version="$(tr -d '[:space:]' < "${HIP_REPO_ROOT}/VERSION")"
  fi

  printf '%bHIP Version:%b %s\n' "${C_BOLD}" "${C_RESET}" "${version}"
  printf '%bGit Commit:%b %s\n' "${C_BOLD}" "${C_RESET}" "$(hip_get_git_commit)"
  printf '%bBranch:%b %s\n' "${C_BOLD}" "${C_RESET}" "$(hip_get_git_branch)"
  printf '%bRepository:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_REPO_ROOT}"
  printf '%bDeployment Target:%b %s\n' "${C_BOLD}" "${C_RESET}" "${target}"
  printf '%bContainer:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_CONTAINER_NAME:-unset}"
  printf '%bHome Assistant URL:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_HA_URL:-unset}"
  printf '%bConfiguration file:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_CONFIGURATION_FILE}"
}

hip_print_dry_run_plan() {
  local target="$1"
  printf '%b==== HIP Dry Run (%s) ====%b\n' "${C_BOLD}${C_CYAN}" "${target}" "${C_RESET}"
  printf '%s\n' "Planned actions:"
  printf '%s\n' "- Validate prerequisites and configuration"
  printf '%s\n' "- Apply git target policy and optional pull"
  printf '%s\n' "- Create HIP backup in container /config/.storage/hip/backups"
  printf '%s\n' "- Copy runtime files from repository to container"
  printf '%s\n' "- Restart container and wait for Home Assistant startup"
  printf '%s\n' "- Run hip.validate and hip.run_smoke_tests when services are available"
  printf '%s\n' "- Write deployment report and summary state"
}

hip_run_doctor() {
  local issues=()
  local config_full_path="${HIP_REPO_ROOT}/${HIP_CONFIGURATION_FILE}"

  printf '%b==== HIP Deployment Doctor ====%b\n' "${C_BOLD}${C_CYAN}" "${C_RESET}"

  printf '%bRepository:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_REPO_ROOT}"
  if [ -d "${HIP_REPO_ROOT}" ] && git -C "${HIP_REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    hip_log_ok "Repository"
  else
    hip_log_error "Repository"
    issues+=("Repository is missing or not a git working tree: ${HIP_REPO_ROOT}")
  fi

  printf '%bGit:%b %s\n' "${C_BOLD}" "${C_RESET}" "$(hip_get_git_commit) @ $(hip_get_git_branch)"
  if hip_has_command git; then
    hip_log_ok "Git"
  else
    hip_log_error "Git"
    issues+=("Git is not installed or not on PATH")
  fi

  printf '%bDocker:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_CONTAINER_NAME:-unset}"
  if hip_has_command docker; then
    hip_log_ok "Docker"
  else
    hip_log_error "Docker"
    issues+=("Docker is not installed or not on PATH")
  fi

  if hip_has_command docker; then
    if [ -n "${HIP_CONTAINER_NAME}" ] && docker inspect "${HIP_CONTAINER_NAME}" >/dev/null 2>&1; then
      hip_log_ok "Container exists"
    else
      hip_log_error "Container exists"
      issues+=("Docker container does not exist: ${HIP_CONTAINER_NAME:-unset}")
    fi
  else
    hip_log_warn "Container exists (skipped: docker unavailable)"
    issues+=("Container check skipped because Docker is unavailable")
  fi

  printf '%bConfiguration path:%b %s\n' "${C_BOLD}" "${C_RESET}" "${config_full_path}"
  if [ -n "${HIP_CONFIGURATION_FILE}" ] && [ -f "${config_full_path}" ]; then
    hip_log_ok "Configuration path"
  else
    hip_log_error "Configuration path"
    issues+=("Configuration file not found: ${config_full_path}")
  fi

  if [ -n "${HIP_HA_TOKEN}" ]; then
    hip_log_ok "Token configured"
  else
    hip_log_error "Token configured"
    issues+=("HIP_HA_TOKEN is empty in ${HIP_CONFIGURATION_FILE}")
  fi

  printf '%bHome Assistant URL:%b %s\n' "${C_BOLD}" "${C_RESET}" "${HIP_HA_URL:-unset}"
  if hip_has_command curl && [ -n "${HIP_HA_URL}" ] && [ -n "${HIP_HA_TOKEN}" ] && \
    curl -fsS -o /dev/null -H "Authorization: Bearer ${HIP_HA_TOKEN}" "${HIP_HA_URL}/api/"; then
    hip_log_ok "Home Assistant reachable"
  else
    hip_log_error "Home Assistant reachable"
    issues+=("Home Assistant API is not reachable at ${HIP_HA_URL:-unset}")
  fi

  if hip_has_command docker && [ -n "${HIP_CONTAINER_NAME}" ] && docker inspect "${HIP_CONTAINER_NAME}" >/dev/null 2>&1; then
    if docker exec "${HIP_CONTAINER_NAME}" sh -c "test -d /config && test -d /config/.storage" >/dev/null 2>&1; then
      hip_log_ok "Runtime directories"
    else
      hip_log_error "Runtime directories"
      issues+=("Runtime directories missing in container ${HIP_CONTAINER_NAME}: /config or /config/.storage")
    fi

    if docker exec "${HIP_CONTAINER_NAME}" sh -c "test -w /config && test -w /config/.storage" >/dev/null 2>&1; then
      hip_log_ok "Permissions"
    else
      hip_log_error "Permissions"
      issues+=("Insufficient write permissions for /config or /config/.storage in container ${HIP_CONTAINER_NAME}")
    fi
  else
    hip_log_warn "Runtime directories (skipped: container unavailable)"
    hip_log_warn "Permissions (skipped: container unavailable)"
    issues+=("Runtime directory checks skipped because container is unavailable")
  fi

  if [ "${#issues[@]}" -eq 0 ]; then
    printf '%bREADY TO DEPLOY%b\n' "${C_BOLD}${C_GREEN}" "${C_RESET}"
    return 0
  fi

  printf '%bFAILED%b\n' "${C_BOLD}${C_RED}" "${C_RESET}"
  local issue
  for issue in "${issues[@]}"; do
    printf ' - %s\n' "${issue}"
  done
  return 1
}
