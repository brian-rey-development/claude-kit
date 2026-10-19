"""Derives a Claude Code theme from a kit theme's palette, so a new theme starts consistent everywhere."""

from __future__ import annotations

from claude_kit.color import lighten, mix
from claude_kit.jsonfile import JsonObject


def derive(data: JsonObject) -> JsonObject:
    p, t = data["palette"], data["terminal"]
    bg, ansi = t["background"], t["ansi"]
    subtle = mix(p["caption"], bg, 0.65)
    return {
        "name": data["name"],
        "base": data["appearance"],
        "overrides": {
            "claude": p["brand"],
            "claudeShimmer": lighten(p["brand"]),
            "clawd_body": p["icon"],
            "clawd_background": t["selection"],
            "text": t["foreground"],
            "inactive": p["caption"],
            "inactiveShimmer": p["detail"],
            "subtle": subtle,
            "suggestion": p["accent_soft"],
            "permission": p["accent"],
            "permissionShimmer": p["accent_soft"],
            "remember": p["merged"],
            "success": p["ok"],
            "error": p["danger"],
            "warning": p["warn"],
            "warningShimmer": lighten(p["warn"]),
            "merged": p["merged"],
            "promptBorder": subtle,
            "promptBorderShimmer": p["accent"],
            "planMode": p["accent_soft"],
            "autoAccept": p["accent"],
            "bashBorder": p["brand"],
            "ide": p["accent_soft"],
            "fastMode": p["warn"],
            "fastModeShimmer": lighten(p["warn"]),
            "diffAdded": mix(p["ok"], bg, 0.22),
            "diffRemoved": mix(p["danger"], bg, 0.22),
            "diffAddedDimmed": mix(p["ok"], bg, 0.12),
            "diffRemovedDimmed": mix(p["danger"], bg, 0.12),
            "diffAddedWord": mix(p["ok"], bg, 0.45),
            "diffRemovedWord": mix(p["danger"], bg, 0.45),
            "userMessageBackground": mix(t["foreground"], bg, 0.06),
            "userMessageBackgroundHover": mix(t["foreground"], bg, 0.1),
            "bashMessageBackgroundColor": mix(p["brand"], bg, 0.08),
            "memoryBackgroundColor": mix(p["merged"], bg, 0.08),
            "selectionBg": t["selection"],
            "rate_limit_fill": p["accent"],
            "rate_limit_empty": p["track"],
            "briefLabelYou": p["accent"],
            "briefLabelClaude": p["brand"],
            "red_FOR_SUBAGENTS_ONLY": ansi[1],
            "blue_FOR_SUBAGENTS_ONLY": ansi[4],
            "green_FOR_SUBAGENTS_ONLY": ansi[2],
            "yellow_FOR_SUBAGENTS_ONLY": ansi[3],
            "purple_FOR_SUBAGENTS_ONLY": ansi[5],
            "orange_FOR_SUBAGENTS_ONLY": p["warn"],
            "pink_FOR_SUBAGENTS_ONLY": ansi[13],
            "cyan_FOR_SUBAGENTS_ONLY": ansi[6],
        },
    }
