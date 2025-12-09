# Disabled Features

This document tracks features that are still present in the codebase but are currently hidden/disabled from the user interface.

## Dashboard Layout Preset Dropdown

**Status:** Hidden (code preserved)

**Location:** `src/templates/dashboard.html`

**Description:** A dropdown menu in the navigation bar that allows users to quickly switch between predefined layout presets. The feature includes:

### Available Presets:
- **Dense (3 columns)** - 3 charts per row, less scrolling
- **Ultra Dense (4 columns)** - 4 charts per row, minimal scrolling
- **All Sensors (3 col)** - All 11 charts in compact 3-column layout
- **Full Dashboard** - All sections, default layout
- **Mission Overview** - Essential monitoring sections
- **Environmental Focus** - BME280 deep dive
- **Navigation Focus** - MPU6050 inertial data
- **Analysis Mode** - Post-mission review
- **Compact** - Minimal monitoring
- **Wide Charts** - Full-width charts

### Additional Features:
- Grid column selector (1-4 columns)
- Toggle sections visibility
- Custom layout creation and saving

### How to Re-enable:
In `src/templates/dashboard.html`, find the CSS rule:
```css
.layout-selector {
  display: none !important; /* DISABLED - see Disabled_Features.md */
  ...
}
```
Remove or comment out the `display: none !important;` line.

### Reason for Disabling:
The sections toggle bar now provides simpler, more direct control over section visibility and column layout, making the dropdown menu redundant.
