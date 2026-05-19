#!/usr/bin/env python3
"""Generate an MP3 audio overview with Edge TTS."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import edge_tts


async def synthesize(input_text: Path, output_audio: Path, voice: str) -> None:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    text = input_text.read_text(encoding="utf-8")
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+0%", volume="+0%")
    await communicate.save(str(output_audio))


def main() -> int:
    input_text = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("audio_script.txt")
    output_audio = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("audio/topic_overview.mp3")
    voice = sys.argv[3] if len(sys.argv) > 3 else "zh-CN-XiaoxiaoNeural"
    asyncio.run(synthesize(input_text, output_audio, voice))
    print(f"Wrote {output_audio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

