# Settlers III MapGen — v1.7 DEV_11

Final feature DEV planned before v1.7 RC.

## Changes
- Terrain ID24 (Herbe sèche / Dry grass) joins the Grass analytical family instead of Other terrain.
- Terrain Families chart: Grass = Green Grass ID16 + Dry Grass ID24, stacked with legend/tooltips.
- Contextual tooltip IDs added where semantically useful: terrain, object, resource; global mining includes both mineral resource ID and terrain IDs of the hovered open/snow segment.
- Statistics report remains fully FR/EN and is explicitly treated as a user-facing translated surface despite its debug-oriented content.
- Stats schema v7.
- TODO updated with DE/ES, exactly two configurable proximity radii, histogram/radial-profile/chart-variant ideas, future native-corpus boxplots, and uncertain long-range ideas.

## Intentionally unchanged
- Generation engine and protected v1.5 files.
- Graph↔Map coupling.
- Massif/lake/river tooltip detail level.
- Generic nearby Trees/Stones/Fish tooltip IDs.
- Proximity radii remain fixed at 50/100 for this release.
