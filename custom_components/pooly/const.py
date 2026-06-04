DOMAIN = "pooly"

CONF_HOST = "host"
CONF_PORT = "port"
DEFAULT_PORT = 8000
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

API_STATUS = "/api/ha/status"
API_MAINTENANCE = "/api/ha/maintenance"
API_MAINTENANCE_TASK = "/api/ha/maintenance/{task_type}"
API_COMPLETE_TASK = "/api/ha/maintenance/{task_type}/complete"
API_DISMISS_TASK = "/api/ha/maintenance/{task_type}/dismiss"
API_SENSOR_PUSH = "/api/ha/sensor"

TASK_TYPES = [
    "test_water",
    "add_chlorine",
    "clean_cartridge",
    "shock_pool",
    "clean_skimmer",
    "robot_run",
    "vacuum",
    "empty_basket",
    "add_water",
    "brush_walls",
    "check_cya",
    "backwash",
]

# These tasks require logging a full journal entry in the Pooly app to complete.
# They auto-complete when the matching entry (measurement / chemical / shock) is saved.
# HA can only dismiss them — no "Mark Complete" button is created.
POOLY_APP_ONLY_TASKS = {
    "test_water",
    "add_chlorine",
    "check_cya",
    "shock_pool",
}

MAINTENANCE_STATES = ["urgent", "overdue", "due_soon", "good"]

STATE_ICONS = {
    "urgent": "mdi:alert-circle",
    "overdue": "mdi:alert",
    "due_soon": "mdi:clock-alert",
    "good": "mdi:check-circle",
}
