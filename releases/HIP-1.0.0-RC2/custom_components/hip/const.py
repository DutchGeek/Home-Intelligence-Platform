from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "hip"
INTEGRATION_VERSION: Final = "2.4.0"
DEFAULT_TITLE: Final = "HIP"
COORDINATOR_NAME: Final = "HIP coordinator"
SCAN_INTERVAL: Final = timedelta(minutes=1)
DEFAULT_DOCUMENTATION_URL: Final = "https://github.com/DutchGeek/Home-Intelligence-Platform"
DEFAULT_PACKAGES_PATH: Final = "homeassistant/packages"
DEFAULT_DASHBOARD_PATH: Final = "homeassistant/dashboards/HIP-Dashboard.yaml"
DEFAULT_RELEASE_NOTES_PATH: Final = "docs/releases"
SUPPORT_BUNDLE_PREFIX: Final = "hip_support_bundle"

CONF_DOCUMENTATION_URL: Final = "documentation_url"
CONF_PACKAGES_PATH: Final = "packages_path"
CONF_DASHBOARD_PATH: Final = "dashboard_path"
CONF_RELEASE_NOTES_PATH: Final = "release_notes_path"

SERVICE_VALIDATE: Final = "validate"
SERVICE_RELOAD: Final = "reload"
SERVICE_HEALTH_CHECK: Final = "health_check"
SERVICE_EXPORT_SUPPORT_BUNDLE: Final = "export_support_bundle"
SERVICE_RUN_SMOKE_TESTS: Final = "run_smoke_tests"
SERVICE_VERSION: Final = "version"
SERVICE_KERNEL_STATUS: Final = "kernel_status"
SERVICE_MODULE_STATUS: Final = "module_status"
SERVICE_EVENT_STATISTICS: Final = "event_statistics"

ATTR_INSTALLED: Final = "installed"
ATTR_ENABLED: Final = "enabled"
ATTR_HEALTHY: Final = "healthy"
ATTR_VERSION: Final = "version"
ATTR_ISSUES: Final = "issues"
ATTR_MODULES: Final = "modules"
ATTR_RUNTIME_STATUS: Final = "runtime_status"
ATTR_INSTALLED_VERSION: Final = "installed_version"
ATTR_REPOSITORY_VERSION: Final = "repository_version"
ATTR_KERNEL_VERSION: Final = "kernel_version"
ATTR_CONTRACT_VERSION: Final = "contract_version"
ATTR_UPGRADE_AVAILABLE: Final = "upgrade_available"
ATTR_MIGRATION_NOTES: Final = "migration_notes"
ATTR_ROLLBACK_AVAILABLE: Final = "rollback_available"
ATTR_SUPPORT_BUNDLE_PATH: Final = "support_bundle_path"
ATTR_SMOKE_TESTS: Final = "smoke_tests"
ATTR_EVENT_TOTAL: Final = "event_total"
ATTR_DAILY_VISITOR_COUNT: Final = "daily_visitor_count"
ATTR_DAILY_NOTIFICATION_COUNT: Final = "daily_notification_count"
ATTR_DAILY_HOMEPOD_COUNT: Final = "daily_homepod_count"
ATTR_DAILY_SNAPSHOT_COUNT: Final = "daily_snapshot_count"
ATTR_LAST_EVENT_AT: Final = "last_event_at"
ATTR_LAST_EVENT_TYPE: Final = "last_event_type"

MODULE_DEFINITIONS: Final = {
    "kernel": {
        "title": "Kernel",
        "paths": ["homeassistant/packages/hip_core", "homeassistant/packages/device_registry"],
        "entities": ["script.hip_event_manager", "script.hip_event_persist", "input_text.hip_last_event_contract_version"],
    },
    "security": {
        "title": "Security",
        "paths": ["homeassistant/packages/security"],
        "entities": ["automation.hip_front_door_event"],
    },
    "media": {
        "title": "Media",
        "paths": ["homeassistant/packages/media"],
        "entities": ["script.hip_homepod_announce"],
    },
    "notifications": {
        "title": "Notifications",
        "paths": ["homeassistant/packages/notifications"],
        "entities": ["script.hip_notify_doorbell"],
    },
    "snapshots": {
        "title": "Snapshots",
        "paths": ["homeassistant/packages/cameras"],
        "entities": ["script.hip_capture_snapshot"],
    },
    "visitor_intelligence": {
        "title": "Visitor Intelligence",
        "paths": ["homeassistant/packages/visitor_intelligence"],
        "entities": ["script.hip_record_visitor_event"],
    },
    "dashboard": {
        "title": "Dashboard",
        "paths": [DEFAULT_DASHBOARD_PATH],
        "entities": [],
    },
    "metrics": {
        "title": "Metrics",
        "paths": ["homeassistant/packages/hip_core"],
        "entities": ["input_number.hip_event_total"],
    },
    "future_ai": {
        "title": "Future AI",
        "paths": ["homeassistant/packages/ai"],
        "entities": [],
    },
}
