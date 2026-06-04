# Pooly — Home Assistant Integration

[![HACS Custom][hacs-badge]](https://hacs.xyz)

A [HACS](https://hacs.xyz) custom integration that connects your [Pooly](https://github.com/walshy828/pooly) pool management app to Home Assistant.

---

## What you get

| Entity | Type | Description |
|--------|------|-------------|
| Pool Open | `binary_sensor` | `on` when the pool is open for the season |
| Pump Running | `binary_sensor` | `on` when the pump is running |
| Health Score | `sensor` | 1–10 pool health score |
| Pool Temperature | `sensor` | Water temperature in °F |
| Urgent Maintenance Count | `sensor` | Number of urgent/overdue tasks |
| *Task* (×12) | `sensor` | Per-task state: `urgent` / `overdue` / `due_soon` / `good` |
| *Task* — Mark Complete (×12) | `button` | Logs the task as done in Pooly |
| *Task* — Dismiss (×12) | `button` | Snoozes the reminder without logging |

The 12 maintenance task sensors cover: Test Water Chemistry, Add Chlorine, Clean Filter Cartridge, Shock Pool, Clean Skimmer Basket, Run Pool Robot, Vacuum Pool, Empty Pump Basket, Check Water Level, Brush Pool Walls, Check CYA Level, and Backwash Filter.

---

## Requirements

- Home Assistant 2024.1 or later
- [HACS](https://hacs.xyz) installed
- Pooly backend running and reachable from Home Assistant on your local network

---

## Installation via HACS

1. Open HACS → **Integrations** → three-dot menu → **Custom repositories**
2. Add `https://github.com/walshy828/pooly_connector` as an **Integration**
3. Search for **Pooly** and install
4. Restart Home Assistant

## Manual installation

Copy the `custom_components/pooly/` folder into your HA `config/custom_components/` directory and restart.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Pooly**
3. Enter your Pooly backend **host** (IP address or hostname) and **port** (default `8000`)

The integration will verify connectivity before saving.

---

## Push sensor data from HA to Pooly

To display your pool thermometer or pump state in Pooly's dashboard, add automations that call the `pooly.push_sensor` service when the relevant entity changes.

### Example: push pool temperature

```yaml
automation:
  - alias: "Push pool temp to Pooly"
    trigger:
      - platform: state
        entity_id: sensor.pool_thermometer
    action:
      - service: pooly.push_sensor
        data:
          sensor_type: pool_temp
          value: "{{ states('sensor.pool_thermometer') | float }}"
          unit: "°F"
          entity_id: sensor.pool_thermometer
```

### Example: push pump state

```yaml
automation:
  - alias: "Push pump state to Pooly"
    trigger:
      - platform: state
        entity_id: switch.pool_pump
    action:
      - service: pooly.push_sensor
        data:
          sensor_type: pump_state
          value: "{{ 1 if is_state('switch.pool_pump', 'on') else 0 }}"
          entity_id: switch.pool_pump
```

Valid `sensor_type` values: `pool_temp`, `pump_state`, `pump_energy`

---

## Automations ideas

- Alert when a maintenance task becomes `urgent`
- Turn on a notification light when `Urgent Maintenance Count` is > 0
- Dashboard card showing all maintenance sensor states at a glance
- Auto-dismiss tasks when the pool is closed for the season

---

## Polling interval

The coordinator polls `/api/ha/status` and `/api/ha/maintenance` every **5 minutes**. Pressing a button triggers an immediate refresh after the API call completes.

---

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
