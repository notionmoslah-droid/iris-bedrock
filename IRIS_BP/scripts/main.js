import { world, system } from "@minecraft/server";
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import { loadLibrary, addPack, removePack } from "./library.js";
import { analyzePack } from "./analyzer.js";

function showMessage(player, message) {
    player.sendMessage("§b[LIRS]§r " + message);
}

function openMainMenu(player) {
    const packs = loadLibrary();
    const form = new ActionFormData()
        .title("LIRS 0.2.0")
        .body("Lightweight Iris Resource System\n\nRegistered packs: " + packs.length + "\n\nChoose an option:")
        .button("Shader Library")
        .button("Add Resource Pack")
        .button("Diagnostics")
        .button("About LIRS");

    form.show(player).then(response => {
        if (response.canceled) return;
        switch (response.selection) {
            case 0: openLibrary(player); break;
            case 1: openAddPack(player); break;
            case 2: openDiagnostics(player); break;
            case 3: openAbout(player); break;
        }
    }).catch(error => console.warn("[LIRS] Main menu error: " + error));
}

function openLibrary(player) {
    const packs = loadLibrary();
    const form = new ActionFormData()
        .title("LIRS Shader Library")
        .body("Registered resource packs: " + packs.length)
        .button("Back to Main Menu");

    for (const pack of packs) form.button(pack.name);

    form.show(player).then(response => {
        if (response.canceled) return;
        if (response.selection === 0) {
            openMainMenu(player);
            return;
        }
        const index = response.selection - 1;
        if (index >= 0 && index < packs.length) openPackDetails(player, index);
    }).catch(error => console.warn("[LIRS] Library error: " + error));
}

function openAddPack(player) {
    const form = new ModalFormData()
        .title("Register Resource Pack")
        .textField("Pack name", "Example: My Visual Pack")
        .textField("Notes or source", "Optional description")
        .toggle("Textures indicator", false)
        .toggle("PBR indicator", false)
        .toggle("Vibrant Visuals indicator", false)
        .toggle("Render Controllers indicator", false);

    form.show(player).then(response => {
        if (response.canceled) return;
        const values = response.formValues;
        const name = String(values[0] ?? "").trim();
        const source = String(values[1] ?? "").trim();

        if (!name) {
            showMessage(player, "Pack name cannot be empty.");
            return;
        }

        const pack = {
            name,
            source,
            textures: values[2] === true,
            pbrIndicators: values[3] === true,
            vibrantVisuals: values[4] === true,
            renderControllers: values[5] === true,
            createdAt: Date.now()
        };

        try {
            if (!addPack(pack)) {
                showMessage(player, "A pack with this name already exists.");
                return;
            }
            showMessage(player, "Pack registered successfully!");
            openLibrary(player);
        } catch (error) {
            showMessage(player, "Storage error: " + error.message);
        }
    }).catch(error => console.warn("[LIRS] Add pack error: " + error));
}

function openPackDetails(player, index) {
    const packs = loadLibrary();
    const pack = packs[index];
    if (!pack) {
        openLibrary(player);
        return;
    }

    const report = analyzePack(pack);
    const form = new ActionFormData()
        .title(pack.name)
        .body("Source / Notes: " + (pack.source || "Not specified") +
            "\n\nClassification: " + report.classification +
            "\nConfidence: " + report.confidence + "\n\nChoose an option:")
        .button("Run Compatibility Analysis")
        .button("Remove from LIRS Library")
        .button("Back");

    form.show(player).then(response => {
        if (response.canceled) return;
        switch (response.selection) {
            case 0: showAnalysis(player, pack); break;
            case 1:
                if (removePack(index)) showMessage(player, "Pack removed from LIRS.");
                openLibrary(player);
                break;
            case 2: openLibrary(player); break;
        }
    }).catch(error => console.warn("[LIRS] Pack details error: " + error));
}

function showAnalysis(player, pack) {
    const report = analyzePack(pack);
    const f = report.features;
    const form = new ActionFormData()
        .title("Compatibility Report")
        .body("Pack: " + report.name +
            "\n\nClassification: " + report.classification +
            "\nConfidence: " + report.confidence +
            "\n\nTextures: " + f.textures +
            "\nPBR indicators: " + f.pbrIndicators +
            "\nVibrant Visuals: " + f.vibrantVisuals +
            "\nRender Controllers: " + f.renderControllers +
            "\n\nWarnings:\n- " + report.warnings.join("\n- "))
        .button("Back");

    form.show(player).then(() => openLibrary(player))
        .catch(error => console.warn("[LIRS] Analysis error: " + error));
}

function openDiagnostics(player) {
    const packs = loadLibrary();
    const stored = world.getDynamicProperty("lirs_packs_v1");
    showMessage(player, "Diagnostics complete.\nRegistered packs: " + packs.length +
        "\nLibrary storage: " + (typeof stored === "string" ? "Available" : "Empty"));
}

function openAbout(player) {
    const form = new ActionFormData()
        .title("About LIRS")
        .body("LIRS 0.2.0\n\nLightweight Iris Resource System\n\n" +
            "Resource pack registration\nMetadata compatibility analysis\n" +
            "Persistent in-world library\n\nLIRS does not directly render shaders.")
        .button("Back");
    form.show(player).then(() => openMainMenu(player))
        .catch(error => console.warn("[LIRS] About error: " + error));
}

world.afterEvents.itemUse.subscribe(event => {
    if (!event.itemStack || event.itemStack.typeId !== "minecraft:compass") return;
    if (event.source.typeId !== "minecraft:player") return;
    system.run(() => openMainMenu(event.source));
});

console.warn("[LIRS] Version 0.2.0 loaded.");
