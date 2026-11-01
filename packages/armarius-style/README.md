# armarius-style

The Scriptorum look of Armarius, as its own package, so that Armarius and
*Armarius: A Solo Saga Assistant* look like one family. It holds no Armarius
code and needs no Armarius installed.

| Module | Holds | Needs |
| --- | --- | --- |
| `armarius_style.palettes` | Palettes, pigments, tinctures | nothing |
| `armarius_style.fonts` | The bundled fonts' files and family names | nothing |
| `armarius_style.terminal` | `SCRIPTORUM`, `SCRIPTORUM_DARK`, `APP_CSS` | `terminal` extra |
| `armarius_style.desktop` | Style sheet, paper, ornaments, illumination, gilding, window frame, page pieces | `desktop` extra |

```python
# Textual
from armarius_style.terminal import (
    APP_CSS,
    SCRIPTORUM,
    SCRIPTORUM_DARK,
    app_variable_defaults,
)


class MyApp(App):
    CSS = APP_CSS

    def get_theme_variable_defaults(self) -> dict[str, str]:
        return app_variable_defaults(self.current_theme)

    def on_mount(self) -> None:
        self.register_theme(SCRIPTORUM)
        self.register_theme(SCRIPTORUM_DARK)
        self.theme = "scriptorum"
```

```python
# PySide6
from armarius_style import fonts, palettes
from armarius_style.desktop.fonts import register_fonts
from armarius_style.desktop.sheet import style_sheet

register_fonts()
app.setStyleSheet(style_sheet(palettes.SCRIPTORUM, fonts.SERIF))
```

A front-end keeps its own choice of theme; nothing here reads or writes
settings. `APP_CSS` styles Armarius's `FieldsDialog` and `FocusableSection`
by name, so a selector for a widget an app doesn't have simply matches
nothing.
