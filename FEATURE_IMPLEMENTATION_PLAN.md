# TRITON Feature Implementation Plan

> **Purpose**: This document preserves the feature implementation plan for the TRITON submarine dashboard. Reference this file when continuing development after context resets.

---

## Quick Reference

**Project**: TRITON - Autonomous submarine navigation system
**Main Files**:
- Backend: `src/app.py` (Flask server)
- Dashboard: `src/templates/dashboard.html` (Chart.js visualization)
- Homepage: `src/templates/index.html`

**Current State**: Planning complete, implementation not started.

---

## Features to Implement (10 Total)

### Priority Order (Recommended)

| Order | Feature # | Name | Complexity | Status |
|-------|-----------|------|------------|--------|
| 1 | 2 | Chart Interactivity | Low | ✅ Completed |
| 2 | 6 | Extended Statistics | Low | ✅ Completed |
| 3 | 7 | Time Range Filtering | Medium | ✅ Completed |
| 4 | 8 | Multi-Metric Correlation | Medium | ✅ Completed |
| 5 | 16 | Mission Comparison | Medium | ✅ Completed |
| 6 | 17 | Mission Replay | Medium | ✅ Completed |
| 7 | 13 | 3D Orientation | Medium | ⬜ Not Started |
| 8 | 10 | Configuration UI | Medium | ⬜ Not Started |
| 9 | 12 | Export Formats | Medium | ⬜ Not Started |
| 10 | 15 | Alerts System | High | ⬜ Not Started |

---

## Feature Details

### Feature 2: Chart Interactivity Enhancements
**File**: `src/templates/dashboard.html`

**What to add**:
- Zoom (mouse wheel, drag-to-zoom) and pan (Ctrl+drag)
- Tooltips with exact values and timestamps
- Reset zoom button on each chart

**Dependencies to add** (after Chart.js import):
```html
<script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1"></script>
```

**Chart options to add**:
```javascript
plugins: {
  zoom: {
    pan: { enabled: true, mode: 'xy', modifierKey: 'ctrl' },
    zoom: {
      wheel: { enabled: true },
      drag: { enabled: true, backgroundColor: 'rgba(0,170,255,0.2)' },
      mode: 'xy'
    }
  },
  tooltip: {
    callbacks: {
      title: (ctx) => `Time: ${ctx[0].label.toFixed(2)}s`,
      label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(3)}`
    }
  }
}
```

---

### Feature 6: Extended Statistics Panel
**File**: `src/templates/dashboard.html`

**What to add**:
- Expand table headers: Min, Max, Avg, Median, StdDev, 25%, 75%, 95%, Rate/s
- Stats meta display: point count, sample rate (Hz), last update time
- New `computeExtendedStats(values, elapsedTimes)` function

**Key calculations**:
- Median: middle value of sorted array
- Std Dev: `sqrt(sum((x - mean)²) / n)`
- Percentiles: linear interpolation
- Rate of change: linear regression slope of last 5 points

---

### Feature 7: Custom Time Range Filtering
**File**: `src/templates/dashboard.html`

**What to add**:
- Preset buttons: All, Last 30s, Last 1min, Last 5min, Custom
- Custom range inputs (from/to seconds)
- `filterDataByTimeRange(history, filter)` function
- Store full data in `fullHistory`, display filtered
- "Export Filtered Data" button

---

### Feature 8: Multi-Metric Correlation View
**File**: `src/templates/dashboard.html`

**What to add**:
- New section with dual Y-axis chart
- Two multi-select dropdowns (left axis, right axis)
- Left axis = solid lines, Right axis = dashed lines
- Color palette for multiple datasets

---

### Feature 10: Configuration UI Panel
**Files**: `src/app.py`, `src/templates/dashboard.html`

**Backend endpoints**:
- `GET/POST /config` - Get/update configuration
- `POST /config/reset` - Reset to defaults
- `GET /config/profiles` - List profiles
- `GET/POST/DELETE /config/profiles/<name>` - Manage profiles

**New directory**: `config/` for storing `triton_config.json`

**Configurable values**:
- Sea level pressure (calibration)
- Transmission thresholds
- Update frequency
- History length

---

### Feature 12: Multiple Export Formats
**Files**: `src/app.py`, `src/templates/dashboard.html`

**Install dependencies**:
```bash
pip install openpyxl reportlab
```

**Backend endpoints**:
- `GET /export/json` - JSON with metadata
- `GET /export/excel` - .xlsx with multiple sheets
- `GET /export/pdf` - Formatted PDF report

**Query params**: `?start=<seconds>&end=<seconds>` for time range

---

### Feature 13: 3D Orientation Visualization
**File**: `src/templates/dashboard.html`

**CDN dependencies**:
```html
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
```

**What to add**:
- `OrientationVisualization` class (Three.js scene, submarine model)
- `GyroIntegrator` class (integrate angular velocities)
- Pitch/Roll/Yaw numeric display
- Reset orientation button

**Submarine model**:
- Hull: CapsuleGeometry
- Conning tower: CylinderGeometry
- Propeller: ConeGeometry

---

### Feature 15: Real-Time Alerts System
**Files**: `src/app.py`, `src/templates/dashboard.html`

**Backend endpoints**:
- `GET/POST /alerts/config`
- `POST /alerts/definitions`
- `PUT/DELETE /alerts/definitions/<id>`
- `GET/DELETE /alerts/history`
- `GET /alerts/active`
- `POST /alerts/acknowledge/<id>`

**Alert structure**:
```javascript
{
  id: "uuid",
  name: "High Temperature",
  metric: "Temp_BME280 [°C]",
  condition: "gt", // gt, lt, gte, lte, eq
  threshold: 30,
  type: "warning", // or "critical"
  enabled: true
}
```

**Features**:
- Visual banner (yellow warning, red critical with flash)
- Browser notifications (Notification API)
- Sound alerts (optional)
- Alert history log

---

### Feature 16: Mission Comparison Dashboard
**Files**: `src/app.py`, `src/templates/dashboard.html`

**Backend endpoints**:
- `GET /api/missions/list` - List CSV files from logs/ and logs/previous_data/
- `GET /api/missions/load/<filename>` - Parse CSV and return as JSON

**Frontend**:
- Two mission selection dropdowns
- Side-by-side comparison chart
- Delta chart (Mission 1 - Mission 2)
- Statistics comparison table

---

### Feature 17: Mission Replay/Playback Mode
**File**: `src/templates/dashboard.html`

**Uses endpoints from Feature 16**

**What to add**:
- `PlaybackController` class
- Transport controls: Play, Pause, Stop
- Speed selector: 0.5x, 1x, 2x, 5x, 10x
- Seek slider
- Loop toggle
- Mode indicator (LIVE vs PLAYBACK)
- Return to Live button

---

## Dependencies Summary

### Python Packages
```bash
pip install openpyxl reportlab
# Optional for Feature 19: pip install flask-socketio
```

### CDN Libraries
| Library | Version | Features |
|---------|---------|----------|
| chartjs-plugin-zoom | 2.0.1 | 2, 7, 8 |
| Hammer.js | 2.0.8 | 2 |
| Three.js | 0.160.0 | 13 |

---

## Implementation Notes

### File Structure After Implementation
```
TRITON/
├── src/
│   ├── app.py              # + config, export, alerts, missions endpoints
│   ├── templates/
│   │   ├── dashboard.html  # + all frontend features
│   │   └── index.html      # (reference only)
│   └── ...
├── config/                  # NEW - configuration storage
│   ├── triton_config.json
│   ├── alerts.json
│   └── profile_*.json
├── logs/
│   ├── sensor_data_*.csv
│   └── previous_data/
└── FEATURE_IMPLEMENTATION_PLAN.md  # THIS FILE
```

### Sensor Data Labels (for reference)
```
Elapsed [s], Temp_BME280 [°C], Hum [%], Press [hPa], Alt [m],
Acc x [m/s²], Acc y [m/s²], Acc z [m/s²],
Gyro x [°/s], Gyro y [°/s], Gyro z [°/s], Temp_MPU [°C]
```

---

## Detailed Plan File

For the complete detailed implementation plan with code examples, see:
`C:\Users\sebi\.claude\plans\humming-wibbling-pike.md`

---

## Progress Tracking

Update this section as features are completed:

```
[x] Feature 2: Chart Interactivity (Completed Dec 2024)
[x] Feature 6: Extended Statistics (Completed Dec 2024)
[x] Feature 7: Time Range Filtering (Completed Dec 2024)
[x] Feature 8: Multi-Metric Correlation (Completed Dec 2024)
[x] Feature 16: Mission Comparison (Completed Dec 2024)
[x] Feature 17: Mission Replay (Completed Dec 2024)
[ ] Feature 10: Configuration UI
[ ] Feature 12: Export Formats
[ ] Feature 13: 3D Orientation
[ ] Feature 15: Alerts System
```

---

*Last updated: December 2024*
*Plan approved by user, ready for implementation*
