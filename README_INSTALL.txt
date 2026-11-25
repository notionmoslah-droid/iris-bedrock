# LIRS 0.2.0 — package contents and installation

## Files
- `IRIS_BP/manifest.json` — Bedrock behavior-pack manifest.
- `IRIS_BP/scripts/main.js` — in-game menu and compass entry point.
- `IRIS_BP/scripts/library.js` — saves the registered pack list in world Dynamic Properties.
- `IRIS_BP/scripts/analyzer.js` — analyzes manually entered compatibility indicators.

## Import into Minecraft Bedrock
1. Extract this ZIP.
2. Open the `IRIS_BP` folder. It must directly contain `manifest.json` and the `scripts` folder.
3. To import as a pack, use the included `LIRS-0.2.0.mcpack` file (it is also at the ZIP root).
4. Open the `.mcpack` file with Minecraft and wait for the import confirmation.
5. In the target world settings, enable the LIRS behavior pack.
6. Enter the world and use a compass to open the LIRS menu.

## Important limitations
This is an early in-game manager, not a shader renderer. It does not scan arbitrary folders on the phone, install resource packs automatically, or create Java-style dynamic shadows. The compatibility report uses indicators entered by the player and is not proof that a pack will render.

The manifest targets Bedrock 1.21.0+ and declares `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Actual API availability depends on the installed Minecraft version.
