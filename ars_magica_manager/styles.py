"""App-wide CSS: the styling that uses the app's own theme variables
(themes.py: $field-background, $heading, $label, $rule...), and that
restyles Textual's widgets everywhere. The app sets it as App.CSS.

It lives here, not in a widget's DEFAULT_CSS, because a widget's CSS must
also parse in a bare test App, which doesn't define the app's variables.
"""

APP_CSS = """
/* STORY-1011: a text field is a well with a background of its own, so it
   shows where to type even on a dialog (dialogs and compact fields are
   both $surface otherwise); the one being typed in lifts. Compact fields
   get a column of padding so text doesn't touch the well's edge. */
Input, TextArea, Select > SelectCurrent, FieldsDialog .fd-picker {
    background: $field-background;
}

Input:focus, TextArea:focus, Select:focus > SelectCurrent {
    background: $field-background-focus;
    background-tint: transparent;
}

Input.-textual-compact, Select.-textual-compact > SelectCurrent {
    padding: 0 1;
}

/* STORY-1013: placeholder text readable on a well (Textual's
   $text-disabled isn't), in italics so it doesn't pass for a value. A
   Select with nothing chosen shows its prompt the same way. */
Input > .input--placeholder, Input > .input--suggestion {
    color: $placeholder;
    text-style: italic;
}

SelectCurrent Static#label {
    color: $placeholder;
}

SelectCurrent.-has-value Static#label {
    color: $foreground;
}

/* STORY-1012: a ladder of emphasis. The entity's name and dialog titles
   are headings; every section title is bold under a faint rule (the
   focused section's rule is $primary, FocusableSection); the active tab is
   bold and the others recede; form labels recede so values stand out. */
ModalDialog .dialog-title {
    color: $heading;
    border-bottom: solid $rule;
    margin-bottom: 1;
}

#char-top-panel FocusableSection:first-of-type > CollapsibleTitle,
#lab-top-panel FocusableSection:first-of-type > CollapsibleTitle,
#fam-top-panel FocusableSection:first-of-type > CollapsibleTitle {
    color: $heading;
}

/* ...but a focused title is drawn on the $primary cursor bar, where the
   heading colour can vanish (the light theme's are both cinnabar). */
#char-top-panel FocusableSection:first-of-type > CollapsibleTitle:focus,
#lab-top-panel FocusableSection:first-of-type > CollapsibleTitle:focus,
#fam-top-panel FocusableSection:first-of-type > CollapsibleTitle:focus {
    color: $block-cursor-foreground;
}

FocusableSection {
    border-top: hkey $rule;
}

FocusableSection > CollapsibleTitle {
    text-style: bold;
}

Tabs Tab {
    color: $label;
}

Tabs Tab.-active {
    color: $heading;
    text-style: bold;
}

FieldsDialog .fd-label, FieldsDialog .fd-area-label {
    color: $label;
}

FieldsDialog .fd-hint {
    color: $label;
    text-style: italic;
}
"""
