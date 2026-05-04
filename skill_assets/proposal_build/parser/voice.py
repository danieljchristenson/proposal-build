"""Load voice presets from skill_assets/voice_presets/{name}.md."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import frontmatter


VOICE_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "voice_presets"


class VoiceLoadError(Exception):
    pass


@dataclass(frozen=True)
class VoicePreset:
    name: str
    description: str
    default_case_study: str
    default_pillars: tuple
    default_phases: tuple
    default_after_approval_steps: tuple
    default_sign_off_recap_pattern: str
    voice_rules_md: str   # the prose body — read by the polish chat in Claude Desktop


def load_voice(name: str) -> VoicePreset:
    path = VOICE_DIR / f"{name}.md"
    if not path.exists():
        raise VoiceLoadError(f"Voice preset not found: {name} (looked at {path})")

    post = frontmatter.load(str(path))
    fm = post.metadata

    return VoicePreset(
        name=fm["name"],
        description=fm.get("description", ""),
        default_case_study=fm.get("default_case_study", ""),
        default_pillars=tuple(fm.get("default_pillars", ())),
        default_phases=tuple(fm.get("default_phases", ())),
        default_after_approval_steps=tuple(fm.get("default_after_approval_steps", ())),
        default_sign_off_recap_pattern=fm.get("default_sign_off_recap_pattern", ""),
        voice_rules_md=post.content,
    )
