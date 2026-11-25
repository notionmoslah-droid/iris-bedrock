import { world } from "@minecraft/server";

const PROPERTY_KEY = "lirs_packs_v1";
const MAX_LIBRARY_SIZE = 28000;

export function loadLibrary() {
    const raw = world.getDynamicProperty(PROPERTY_KEY);
    if (typeof raw !== "string" || raw.length === 0) return [];
    try {
        const data = JSON.parse(raw);
        return Array.isArray(data) ? data : [];
    } catch {
        console.warn("[LIRS] Library data is invalid.");
        return [];
    }
}

export function saveLibrary(packs) {
    if (!Array.isArray(packs)) throw new Error("Library must be an array.");
    const raw = JSON.stringify(packs);
    if (raw.length > MAX_LIBRARY_SIZE) throw new Error("LIRS library storage limit reached.");
    world.setDynamicProperty(PROPERTY_KEY, raw);
}

export function addPack(pack) {
    const packs = loadLibrary();
    const duplicate = packs.some(item =>
        typeof item.name === "string" && item.name.toLowerCase() === pack.name.toLowerCase()
    );
    if (duplicate) return false;
    packs.push(pack);
    saveLibrary(packs);
    return true;
}

export function removePack(index) {
    const packs = loadLibrary();
    if (!Number.isInteger(index) || index < 0 || index >= packs.length) return false;
    packs.splice(index, 1);
    saveLibrary(packs);
    return true;
}
