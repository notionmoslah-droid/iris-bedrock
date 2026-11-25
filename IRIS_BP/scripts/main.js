
import { world, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

function openLIRS(player) {
    const menu = new ActionFormData()
        .title("LIRS Shader Manager")
        .body(
            "Welcome to LIRS 0.1.0\n\n" +
            "Lightweight Iris Resource System\n\n" +
            "Choose an option:"
        )
        .button("Shader Library")
        .button("Compatibility")
        .button("About LIRS");

    menu.show(player).then((response) => {
        if (response.canceled) return;

        switch (response.selection) {
            case 0:
                player.sendMessage(
                    "§b[LIRS]§r Shader library is not connected yet."
                );
                break;

            case 1:
                player.sendMessage(
                    "§b[LIRS]§r Compatibility analyzer integration is pending."
                );
                break;

            case 2:
                player.sendMessage(
                    "§b[LIRS]§r Lightweight Iris Resource System - Version 0.1.0"
                );
                break;
        }
    }).catch((error) => {
        console.warn("LIRS UI Error: " + error);
    });
}

world.afterEvents.itemUse.subscribe((event) => {
    if (event.itemStack.typeId !== "minecraft:compass") {
        return;
    }

    system.run(() => {
        openLIRS(event.source);
    });
});

console.warn("[LIRS] Shader Manager loaded.");
