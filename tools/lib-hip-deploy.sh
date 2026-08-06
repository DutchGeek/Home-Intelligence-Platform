#!/usr/bin/env bash
set -euo pipefail

HIP_REPO_ROOT="${HIP_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
HIP_HA_URL="${HIP_HA_URL:-http://localhost:8123}"
HIP_HA_TOKEN="${HIP_HA_TOKEN:-}"
HIP_WAIT_TIMEOUT="${HIP_WAIT_TIMEOUT:-300}"
HIP_GIT_REMOTE="${HIP_GIT_REMOTE:-origin}"
HIP_GIT_BRANCH="${HIP_GIT_BRANCH:-main}"
HIP_GIT_PULL="${HIP_GIT_PULL:-true}"
HIP_REQUIRE_CLEAN_TREE="${HIP_REQUIRE_CLEAN_TREE:-true}"
HIP_CONFIRM_DEPLOYMENT="${HIP_CONFIRM_DEPLOYMENT:-true}"

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

hip_require_token() {
  if [ -z "$HIP_HA_TOKEN" ]; then
    hip_log_error "HIP_HA_TOKEN is required to execute hip.validate and hip.run_smoke_tests"
    exit 1
  fi
}

hip_target_defaults() {
  local target="$1"
  case "$target" in
    development)
      HIP_CONTAINER_NAME="${HIP_CONTAINER_NAME:-hip-dev}"
      ;;
    production)
      HIP_CONTAINER_NAME="${HIP_CONTAINER_NAME:-homeassistant}"
      ;;
    *)
      hip_log_error "unknown deployment target: $target"
      exit 1
      ;;
  esac
}

hip_load_configuration() {
  local target="$1"
  local env_file

  case "$target" in
    development)
      env_file="${HIP_REPO_ROOT}/config/dev.env"
      ;;
    production)
      env_file="${HIP_REPO_ROOT}/config/prod.env"
      ;;
    *)
      hip_log_error "unsupported deployment target for config loading: $target"
      exit 1
      ;;
  esac

  if [ -f "$env_file" ]; then
    hip_log_info "loading configuration from $env_file"
    set -a
    # shellcheck disable=SC1090
    . "$env_file"
    set +a
  else
    hip_log_warn "config file not found, continuing with environment defaults: $env_file"
  fi

  HIP_DEPLOY_TARGET="$target"
  hip_target_defaults "$target"
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

hip_wait_for_home_assistant() {
  local timeout_seconds="${1:-$HIP_WAIT_TIMEOUT}"
  local start
  start="$(date +%s)"

  while true; do
    if curl -fsS -o /dev/null -H "Authorization: Bearer ${HIP_HA_TOKEN}" "${HIP_HA_URL}/api/"; then
      return 0
    fi
    if [ $(( $(date +%s) - start )) -ge "$timeout_seconds" ]; then
      hip_log_error "timed out waiting for Home Assistant startup after ${timeout_seconds}s"
      return 1
    fi
    sleep 3
  done
}

hip_call_service() {
  local service_path="$1"
  local payload="${2:-{}}"
  local url_with_response="${HIP_HA_URL}/api/services/${service_path}?return_response"
  local url_plain="${HIP_HA_URL}/api/services/${service_path}"

  if response="$(curl -fsS -H "Authorization: Bearer ${HIP_HA_TOKEN}" -H "Content-Type: application/json" -X POST -d "$payload" "$url_with_response" 2>/dev/null)"; then
    printf '%s' "$response"
    return 0
  fi

  curl -fsS \
    -H "Authorization: Bearer ${HIP_HA_TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST \
    -d "$payload" \
    "$url_plain"
}

hip_restart_container() {
  docker restart "${HIP_CONTAINER_NAME}" >/dev/null
}

hip_ensure_state_directories() {
  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p /config/.storage/hip/backups /config/.storage/hip/reports /config/.storage/hip"
}

hip_git_require_clean_or_exit() {
  if ! git -C "${HIP_REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    hip_log_error "HIP_REPO_ROOT is not a git repository: ${HIP_REPO_ROOT}"
    exit 1
  fi

  if git -C "${HIP_REPO_ROOT}" diff --quiet --ignore-submodules -- && git -C "${HIP_REPO_ROOT}" diff --cached --quiet --ignore-submodules --; then
    hip_log_ok "git working tree is clean"
    return 0
  fi

  if [ "${HIP_REQUIRE_CLEAN_TREE}" = "true" ]; then
    hip_log_error "git working tree is dirty; commit/stash changes or set HIP_REQUIRE_CLEAN_TREE=false"
    git -C "${HIP_REPO_ROOT}" status --short
    exit 1
  fi

  hip_log_warn "git working tree is dirty; continuing because HIP_REQUIRE_CLEAN_TREE=false"
  git -C "${HIP_REPO_ROOT}" status --short
}

hip_git_pull_if_enabled() {
  if [ "${HIP_GIT_PULL}" != "true" ]; then
    hip_log_info "skipping git pull because HIP_GIT_PULL=${HIP_GIT_PULL}"
    return 0
  fi

  hip_log_info "updating repository with git pull --ff-only ${HIP_GIT_REMOTE} ${HIP_GIT_BRANCH}"
  git -C "${HIP_REPO_ROOT}" fetch "${HIP_GIT_REMOTE}" "${HIP_GIT_BRANCH}"
  git -C "${HIP_REPO_ROOT}" pull --ff-only "${HIP_GIT_REMOTE}" "${HIP_GIT_BRANCH}"
  hip_log_ok "repository updated"
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

  printf '%b%s%b [y/N]: ' "${C_BOLD}" "$message" "${C_RESET}"
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

hip_backup_current() {
  local target="$1"
  local version="$2"
  local timestamp="$3"
  local backup_path="/config/.storage/hip/backups/${timestamp}_${target}_${version}"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p '${backup_path}/custom_components' '${backup_path}/homeassistant/packages' '${backup_path}/homeassistant/dashboards' '${backup_path}/hip'"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/custom_components/hip ]; then cp -a /config/custom_components/hip '${backup_path}/custom_components/hip'; fi"

  for pkg in hip_core security notifications media cameras device_registry visitor_intelligence test ai; do
    docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/homeassistant/packages/${pkg} ]; then cp -a /config/homeassistant/packages/${pkg} '${backup_path}/homeassistant/packages/${pkg}'; fi"
  done

  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -f /config/homeassistant/dashboards/HIP-Dashboard.yaml ]; then cp -a /config/homeassistant/dashboards/HIP-Dashboard.yaml '${backup_path}/homeassistant/dashboards/HIP-Dashboard.yaml'; fi"
  docker exec "${HIP_CONTAINER_NAME}" sh -c "if [ -d /config/hip ]; then cp -a /config/hip/. '${backup_path}/hip/'; fi"

  local metadata_tmp
  metadata_tmp="$(mktemp)"
  cat > "$metadata_tmp" <<EOF
{
  "backup_created_at": "$(hip_iso_now)",
  "deployment_target": "${target}",
  "version": "${version}"
}
EOF
  docker cp "$metadata_tmp" "${HIP_CONTAINER_NAME}:${backup_path}/metadata.json" >/dev/null
  rm -f "$metadata_tmp"

  printf '%s' "$backup_path"
}

hip_copy_runtime_files() {
  local repo_root="$1"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "mkdir -p /config/custom_components /config/homeassistant/packages /config/homeassistant/dashboards"

  docker exec "${HIP_CONTAINER_NAME}" sh -c "rm -rf /config/custom_components/hip"
  docker cp "${repo_root}/custom_components/hip" "${HIP_CONTAINER_NAME}:/config/custom_components/hip"

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
  docker cp "$report_content_file" "${HIP_CONTAINER_NAME}:${report_path}" >/dev/null

  local existing_latest=""
  local state_tmp_read
  state_tmp_read="$(mktemp)"
  if docker cp "${HIP_CONTAINER_NAME}:/config/.storage/hip/manager_state.json" "${state_tmp_read}" >/dev/null 2>&1; then
    existing_latest="$(grep -o '"latest_release_url"[[:space:]]*:[[:space:]]*"[^"]*"' "${state_tmp_read}" | head -n1 | sed 's/.*"\([^"]*\)"$/\1/')"
  fi
  rm -f "${state_tmp_read}"

  local state_tmp
  state_tmp="$(mktemp)"
  cat > "$state_tmp" <<EOF
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
  docker cp "$state_tmp" "${HIP_CONTAINER_NAME}:/config/.storage/hip/manager_state.json" >/dev/null
  rm -f "$state_tmp"

  printf '%s' "$report_path"
}

hip_print_validation_summary() {
  local payload="$1"
  local installation="FAIL"
  local configuration="FAIL"
  local runtime="FAIL"

  if printf '%s' "$payload" | grep -q '"installation_valid"[[:space:]]*:[[:space:]]*true'; then
    installation="PASS"
  fi
  if printf '%s' "$payload" | grep -q '"configuration_valid"[[:space:]]*:[[:space:]]*true'; then
    configuration="PASS"
  fi
  if printf '%s' "$payload" | grep -q '"runtime_healthy"[[:space:]]*:[[:space:]]*true'; then
    runtime="PASS"
  fi

  hip_log_info "Validation summary: installation=${installation}, configuration=${configuration}, runtime=${runtime}"
}

hip_print_smoke_summary() {
  local payload="$1"
  local passed="FAIL"
  local true_count false_count

  if printf '%s' "$payload" | grep -q '"passed"[[:space:]]*:[[:space:]]*true'; then
    passed="PASS"
  fi

  true_count="$(printf '%s' "$payload" | grep -o ': true' | wc -l | tr -d ' ')"
  false_count="$(printf '%s' "$payload" | grep -o ': false' | wc -l | tr -d ' ')"

  hip_log_info "Smoke test summary: overall=${passed}, true=${true_count}, false=${false_count}"
}
