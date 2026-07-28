# Pooly — Home Assistant Integration

[![HACS Custom][hacs-badge]](https://hacs.xyz)

A [HACS](https://hacs.xyz) custom integration that connects your [Pooly](https://github.com/walshy828/pooly) pool management app to Home Assistant.

---

## What you get

### Sensors

| Entity | Type | Description |
|--------|------|-------------|
| Pool Open | `binary_sensor` | `on` when the pool is open for the season |
| Health Score | `sensor` | 1–10 pool health score |
| Urgent Maintenance Count | `sensor` | Number of urgent/overdue tasks |
| *Task* (×12) | `sensor` | Per-task state: `urgent` / `overdue` / `due_soon` / `good` |

Pool temperature and pump state are deliberately **not** exposed as entities. That data originates
in Home Assistant and is pushed *up* to Pooly (see below), so mirroring it back would duplicate
entities you already have.

### Buttons

Every maintenance task gets a **Dismiss** button, named `<Task> — Dismiss`, which snoozes the
reminder in Pooly and refreshes the sensors immediately:

🔬 Test Water Chemistry · 🧪 Add Chlorine · ⚡ Shock Pool · ☀️ Check CYA Level ·
🔧 Clean Filter Cartridge · ♻️ Backwash / Deep Clean Filter · 🧹 Clean Skimmer Basket ·
🗑️ Empty Pump Basket · 🤖 Run Pool Robot · 🌊 Vacuum Pool · 💧 Check Water Level ·
🖌️ Brush Pool Walls

**Why is there no "Mark Complete" button?**

Completing a task means recording what you actually did, which belongs in the Pooly app rather than
a stateless button press. Tasks reset automatically when you log the matching journal entry — a
water test resets **Test Water Chemistry** (and **Check CYA Level**, if CYA was measured), a
chlorine addition resets **Add Chlorine**, a shock treatment resets **Shock Pool**, and so on.

Dismiss from HA to quiet a reminder; open Pooly to actually complete the task.

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

In your `.env` on the Pooly server, set `HA_PUSH_MODE=true` so Pooly doesn't also try to pull the same data from HA. See the [Pooly README](https://github.com/walshy828/pooly) for details.

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

### Example: push pump energy

```yaml
automation:
  - alias: "Push pump energy to Pooly"
    trigger:
      - platform: state
        entity_id: sensor.pool_pump_energy
    action:
      - service: pooly.push_sensor
        data:
          sensor_type: pump_energy
          value: "{{ states('sensor.pool_pump_energy') | float }}"
          unit: kWh
          entity_id: sensor.pool_pump_energy
```

Valid `sensor_type` values: `pool_temp`, `pump_state`, `pump_energy`

---

## Automation ideas

- Alert when a maintenance task becomes `urgent`
- Turn on a notification light when `Urgent Maintenance Count` > 0
- Dashboard card showing all 12 task sensor states at a glance
- Notify household members when the pool health score drops below 6
- Auto-dismiss tasks when the pool is closed for the season

---

## Polling interval

The coordinator polls `/api/ha/status` and `/api/ha/maintenance` every **5 minutes**. Pressing a button triggers an immediate refresh after the API call completes.

---

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
