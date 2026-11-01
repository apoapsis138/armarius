"""The bundled typefaces (SIL Open Font License, NOTICE.md): EB Garamond
for headings, in small caps, and prose; Uncial Antiqua for one decorative
flourish. Labels, numbers and tables use the system's own UI font.
"""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"

#: The families the style sheets name, once registered.
SERIF = "EB Garamond"
DISPLAY = "Uncial Antiqua"
#: Labels, numbers and tables: Windows's own UI face, else the system's.
UI = "Segoe UI"

#: The bundled typefaces' files, by family name.
FONTS: dict[str, tuple[Path, ...]] = {
    SERIF: (
        ASSETS / "fonts" / "EBGaramond-wght.ttf",
        ASSETS / "fonts" / "EBGaramond-Italic-wght.ttf",
    ),
    DISPLAY: (ASSETS / "fonts" / "UncialAntiqua-Regular.ttf",),
}
