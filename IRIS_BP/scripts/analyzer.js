export function analyzePack(pack) {
    const report = {
        name: pack.name,
        classification: "unknown",
        confidence: "low",
        features: {
            textures: Boolean(pack.textures),
            renderControllers: Boolean(pack.renderControllers),
            pbrIndicators: Boolean(pack.pbrIndicators),
            vibrantVisuals: Boolean(pack.vibrantVisuals)
        },
        warnings: []
    };

    if (pack.pbrIndicators) {
        report.classification = "pbr_indicators_reported";
    } else if (pack.vibrantVisuals) {
        report.classification = "possible_vibrant_visuals";
    } else if (pack.textures) {
        report.classification = "resource_pack_no_pbr_indicator";
    }

    if (!pack.textures) report.warnings.push("No textures indicator was reported.");
    if (!pack.pbrIndicators) report.warnings.push("No PBR indicator was reported.");
    if (!pack.vibrantVisuals) report.warnings.push("No Vibrant Visuals indicator was reported.");

    report.warnings.push("Manual metadata check only; this is not an in-game rendering test.");
    return report;
}
