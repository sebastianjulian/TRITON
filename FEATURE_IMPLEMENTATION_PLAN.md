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
| 7 | 13 | 3D Orientation | Medium | ✅ Completed |
| 8 | 10 | Configuration UI | Medium | ✅ Completed |
| 9 | 12 | Export Formats | Medium | ⬜ Not Started |
| 10 | 15 | Alerts System | High | ⬜ Not Started |
| 11 | 18 | Layout Presets | Medium | ✅ Completed |

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

### Feature 18: Dashboard Layout Presets
**File**: `src/templates/dashboard.html`

**Overview**: Add a layout preset selector that allows users to quickly switch between predefined layouts optimized for different mission scenarios, plus custom layout saving.

**Predefined Presets**:

| Preset | Description | Visible Sections | Grid |
|--------|-------------|------------------|------|
| **Full Dashboard** | All sections (default) | All 9 sections | 2-col |
| **Mission Overview** | Essential monitoring | mission-control, bme280, mpu6050, statistics | 2-col |
| **Environmental Focus** | BME280 deep dive for depth/pressure | mission-control, bme280, correlation, statistics | 2-col |
| **Navigation Focus** | MPU6050 inertial navigation | mission-control, mpu6050, correlation, statistics | 2-col |
| **Analysis Mode** | Post-mission review | mission-compare, mission-replay, statistics, downloads | 2-col |
| **Compact** | Minimal live monitoring | mission-control, statistics | 1-col |
| **Wide Charts** | Full-width charts for presentations | bme280, mpu6050 | 1-col |

**Implementation Steps**:

1. **CSS Styles** (after theme selector styles ~line 801):
   - `.layout-selector` - Fixed position dropdown (right: 170px, next to theme selector)
   - `.layout-dropdown`, `.layout-dropdown-btn`, `.layout-options` - Mirror theme selector pattern
   - `.layout-button` with `.active` state
   - `section.hidden-section` - Smooth hide with opacity/max-height transitions
   - `.grid-1col`, `.grid-3col` - Additional grid classes
   - Mobile responsive adjustments

2. **HTML Structure** (inside `.main-nav` after theme-selector ~line 2189):
   ```html
   <div class="layout-selector">
     <div class="layout-dropdown">
       <button class="layout-dropdown-btn">
         <span class="layout-current">Full Dashboard</span>
         <span class="layout-dropdown-arrow">&#9660;</span>
       </button>
       <div class="layout-options">
         <!-- 7 layout buttons with data-layout attributes -->
         <!-- Custom layouts section with save/delete controls -->
       </div>
     </div>
   </div>
   ```

3. **LayoutManager JavaScript Class** (after ThemeManager ~line 5683):
   - Store preset definitions with sections, gridColumns, chartAspectRatio
   - `applyLayout(layoutName)` - Show/hide sections, update grid, resize charts
   - `updateNavLinks()` - Hide nav links for hidden sections
   - LocalStorage persistence (`triton-layout` key)
   - Dropdown toggle and click-outside-to-close behavior

4. **Custom Layout Saving**:
   - `saveCustomLayout(name)` - Save current visible sections as custom layout
   - `deleteCustomLayout(layoutKey)` - Remove custom layout
   - Store in localStorage (`triton-custom-layouts` key)
   - Custom layouts appear in dropdown with star icon

5. **Initialize in window.onload** (~line 5704):
   - Add `new LayoutManager()` after ThemeManager initialization

**localStorage Keys**:
- `triton-layout` - Current layout preset name
- `triton-custom-layouts` - JSON object of custom layout definitions

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
[x] Feature 10: Configuration UI (Completed Dec 2024)
[ ] Feature 12: Export Formats
[x] Feature 13: 3D Orientation (Completed Dec 2024)
[ ] Feature 15: Alerts System
[x] Feature 18: Layout Presets (Completed Dec 2024)
```

---

*Last updated: December 2024*
*Plan approved by user, ready for implementation*
