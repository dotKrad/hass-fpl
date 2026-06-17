<img width="200" alt="Florida_Power_ _Light_Logo svg" src="https://github.com/user-attachments/assets/a1a8e044-7e88-43fd-ae91-eb0336d7fb40" />

---

## Features

This integration connects your Florida Power & Light (FPL) account to Home Assistant, providing real-time energy monitoring and billing insights.

### 📊 Energy Dashboard Integration

Seamlessly integrates with Home Assistant's **Energy Dashboard** with hourly usage statistics, allowing you to visualize your electricity consumption patterns over time.

### 💰 Billing & Cost Tracking

| Sensor | Description |
|--------|-------------|
| Projected Bill | Estimated bill for the current billing period |
| Bill to Date | Current charges accumulated so far |
| Daily Average | Average daily cost |
| Budget Billing | Support for budget billing customers (projected budget bill, deferred amount) |

### ⚡ Usage Monitoring

| Sensor | Description |
|--------|-------------|
| Daily Usage | Daily kWh consumption and cost |
| Hourly Usage | Hour-by-hour breakdown of usage and cost |
| Projected kWh | Estimated total kWh for the billing period |
| Bill to Date kWh | Total kWh consumed so far |

### ☀️ Solar / Net Metering Support

For customers with solar panels:
- **Net Received kWh** – Energy received from the grid
- **Net Delivered kWh** – Energy sent back to the grid

### 📅 Billing Cycle Information

- Current & next bill dates
- Service days in billing period
- Days elapsed / remaining

### 🏠 Appliance-Level Breakdown

See estimated usage and cost by appliance category:

| Category | | |
|----------|----------|----------|
| 🌡️ Cooling | 🚿 Water Heater | 👕 Laundry |
| 🧊 Refrigeration | 🏊 Pool | 💡 Lighting |
| 📺 Entertainment | 🍳 Cooking | 📦 Miscellaneous |

### 🌎 Supported Regions

- **FPL Main Region** (Full feature support)
- **FPL Northwest Region** (Core billing features)

---

## Installation

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dotKrad&repository=hass-fpl&category=integration)

**Or manually add via HACS:**

1. Open **HACS** in your Home Assistant
2. Click the **⋮** menu (top right) → **Custom repositories**
3. Add `https://github.com/dotKrad/hass-fpl` with category **Integration**
4. Search for **"FPL"** and click **Download**
5. Restart Home Assistant

### Option 2: Manual Installation

1. Download the `custom_components/fpl` folder from this repository
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

### Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"FPL"**
4. Enter your FPL account credentials

### Energy Dashboard

Hourly data for the Energy Dashboard comes from **external statistics**, not the Hourly Usage sensors (those stay Unknown and are for debugging only).

1. Go to **Settings** → **Dashboards** → **Energy** → **Configuration**.
2. Under grid consumption, pick the **statistics** entries (chart icon), not the sensor entities (lightning icon):
   - `FPL <account> Hourly Usage` → statistic ID `fpl:<account>_hourly_usage`
   - `FPL <account> Hourly Cost` → statistic ID `fpl:<account>_hourly_cost`
3. Replace `<account>` with your FPL account number. On first setup, wait a few minutes for the integration to backfill hourly data before expecting charts to populate.

---

## Development

This repo uses `uv` for Python package dependencies. 

1. Install `uv` following these [instructions](https://docs.astral.sh/uv/getting-started/installation/).
2. Run `uv venv`
3. Run `uv sync --dev`
4. Run `./scripts/develop`. This will start Home Assistant locally.
5. Access Home Assistant at [http://localhost:8123](http://localhost:8123)
6. If asked, complete the first-time setup (create a local account and password).
7. Go to **Settings** → **Devices & Services** → **Add Integration**, and create a new FPL integration.
8. Make changes to the source code and restart `./scripts/develop` to take effect.

### Reset local dev

To wipe your local Home Assistant instance and start over (e.g. you forgot the password):

1. Stop `./scripts/develop` (Ctrl+C in the terminal where it is running).
2. Delete the config directory: `rm -rf config`
3. Run `./scripts/develop` again and complete first-time setup at [http://localhost:8123](http://localhost:8123).

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)


