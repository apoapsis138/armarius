"""The Scriptorum palettes as a Qt style sheet."""

from __future__ import annotations

from ...style.palettes import Palette, wash_style


def style_sheet(p: Palette, serif: str) -> str:
    """The whole window's Qt style sheet in palette `p`; `serif` is the
    headings' family (EB Garamond). The data font is the application's,
    not set here: a style sheet's font would override every
    widget's own (the fixed-pitch lists, the Arts' italic serif names)."""
    return f"""
    QWidget {{
        background: transparent;
        color: {p["foreground"]};
    }}
    QMenu, QDialog {{
        background: {p["background"]};
    }}
    QToolTip {{
        background: {p["surface"]};
        color: {p["foreground"]};
        border: 1px solid {p["accent"]};
        border-radius: 0px;
        padding: 3px 7px;
        font-family: "{serif}";
        font-size: 11pt;
    }}
    QComboBox QAbstractItemView {{
        background: {p["surface"]};
        border: 1px solid {p["label"]};
        outline: none;
        font-family: "{serif}";
        font-size: 12.5pt;
        font-style: normal;
        padding: 6px 0;
    }}
    QMenu::item:selected {{
        background: {wash_style(p)};
        color: {p["foreground"]};
    }}
    QSplitter::handle {{ background: {p["rule"]}; }}
    QCheckBox::indicator {{
        width: 13px;
        height: 13px;
        border: 1px solid {p["label"]};
        border-radius: 2px;
        background: {p["background"]};
    }}
    QCheckBox::indicator:checked {{
        background: {p["primary"]};
        border-color: {p["primary"]};
    }}
    QTreeWidget, QListWidget {{
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        outline: none;
    }}
    QTreeWidget::item, QListWidget::item {{ padding: 3px 4px; }}
    QTreeWidget::item:selected, QListWidget::item:selected {{
        background: {wash_style(p)};
        color: {p["foreground"]};
        border-left: 2px solid {p["primary"]};
    }}
    QTabWidget::pane {{
        border: none;
        border-top: 1px solid {p["rule"]};
    }}
    QTabBar::tab {{
        font-family: "{serif}";
        font-size: 13pt;
        background: transparent;
        color: {p["label"]};
        padding: 4px 12px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {p["heading"]};
        border-bottom: 2px solid {p["heading"]};
    }}
    QTabBar::tab:hover {{ color: {p["foreground"]}; }}
    QLabel#sectionTitle {{
        font-family: "{serif}";
        font-size: 14pt;
        font-weight: 600;
        color: {p["foreground"]};
        border-bottom: 1px solid {p["rule"]};
        padding-bottom: 2px;
    }}
    QLabel#sheetName {{
        font-family: "{serif}";
        font-size: 24pt;
        color: {p["foreground"]};
    }}
    QFrame#details {{
        background: {p["panel"]};
        border-radius: 4px;
    }}
    QFrame#details QLabel {{ background: transparent; }}
    QPushButton#crumb {{
        font-family: "{serif}";
        font-size: 12.5pt;
        color: {p["label"]};
        background: transparent;
        border: none;
        padding: 2px 4px;
    }}
    QPushButton#crumb:hover {{ color: {p["heading"]}; }}
    QPushButton#crumb:disabled {{ color: {p["foreground"]}; }}
    QComboBox {{
        background: transparent;
        border: none;
        font-family: "{serif}";
        font-size: 12.5pt;
        font-style: italic;
        padding: 3px 30px 7px 6px;
    }}
    QComboBox::drop-down {{ width: 0; border: none; }}
    QComboBox#quiet {{ font-size: 11pt; padding: 1px 30px 6px 4px; }}
    QAbstractSpinBox {{
        background: transparent;
        border: none;
        font-family: "{serif}";
        font-size: 12.5pt;
        font-style: italic;
        padding: 3px 2px 7px 6px;
    }}
    QAbstractSpinBox QLineEdit {{ background: transparent; border: none; padding: 0; }}
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
        width: 16px;
        border: none;
    }}
    QAbstractSpinBox::up-arrow, QAbstractSpinBox::down-arrow {{ image: none; }}
    QLineEdit, QPlainTextEdit {{
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        border-radius: 3px;
        padding: 3px 6px;
        selection-background-color: {p["selection"]};
        selection-color: {p["foreground"]};
    }}
    QLineEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {p["accent"]};
    }}
    QPushButton {{
        font-family: "{serif}";
        font-size: 11pt;
        color: {p["label"]};
        background: transparent;
        border: 1px solid transparent;
        border-right-color: {p["button-shadow"]};
        border-bottom-color: {p["button-shadow"]};
        border-radius: 4px;
        padding: 2px 8px;
    }}
    QPushButton:hover {{
        color: {p["heading"]};
        background: {p["panel"]};
    }}
    QPushButton:disabled {{
        color: {p["dim"]};
        border-color: transparent;
    }}
    QDialog QPushButton {{ font-size: 12pt; padding: 3px 14px; }}
    QDialog QPushButton:default {{ color: {p["heading"]}; }}
    QPushButton#picker {{
        color: {p["foreground"]};
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        border-radius: 3px;
    }}
    QPushButton#picker:hover {{ border: 1px solid {p["accent"]}; }}
    QScrollArea {{ border: none; }}
    QScrollBar:vertical {{ background: transparent; width: 14px; }}
    QScrollBar::handle:vertical {{ background: {p["rule"]}; min-height: 36px; }}
    QScrollBar:horizontal {{ background: transparent; height: 14px; }}
    QScrollBar::handle:horizontal {{ background: {p["rule"]}; min-width: 36px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    QTableCornerButton::section {{ background: {p["surface"]}; border: none; }}
    """
