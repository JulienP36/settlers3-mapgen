# v1.8 DEV_2_R5_R4

Windows recovery build rebuilt directly from DEV_2_R4.

- Removed the experimental header PanedWindow/reparenting approach from R5/R5_R2/R5_R3.
- Header uses only the proven direct-grid responsive layout from R4.
- Session / Comparison uses a stable two-row layout at every width.
- History selector nominal width increased to 40 characters.
- Generation action buttons use tighter regular spacing at the left.
- Modifiers selector uses the same themed image-select menubutton styling.
- Viewer View / Heatmap selectors keep the compact content-based sizing validated during R5 testing.
- Manual header splitters remain deferred until the header is constructed natively around pane parents from startup.
