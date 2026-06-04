DOMAIN = "pooly"

CONF_HOST = "host"
CONF_PORT = "port"
DEFAULT_PORT = 8000
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

API_STATUS = "/api/ha/status"
API_MAINTENANCE = "/api/ha/maintenance"
API_MAINTENANCE_TASK = "/api/ha/maintenance/{task_type}"
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

MAINTENANCE_STATES = ["urgent", "overdue", "due_soon", "good"]

STATE_ICONS = {
    "urgent": "mdi:alert-circle",
    "overdue": "mdi:alert",
    "due_soon": "mdi:clock-alert",
    "good": "mdi:check-circle",
}
