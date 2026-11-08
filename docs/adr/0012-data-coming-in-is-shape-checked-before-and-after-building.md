---
status: accepted
---

# Data coming in is shape-checked before and after building

A saga file, an import, a Remote seat's change and the snapshot a player's app receives all become records through each record's own `from_dict`. Those quietly migrate older saves (renamed keys, text that became a list) and pass values through unchecked, so data of the wrong shape either failed deep inside a constructor as a TypeError (caught, which also hid real bugs) or loaded and crashed a sheet later.

So data coming in is checked in two passes against the dataclasses' own annotations (`shapes.py`):

- **Before building, containers only:** a dict where a record belongs, a list where a list does, a plain value where one does, and every field a record can't do without. This is what a `from_dict` needs in order not to fail on the wrong kind of thing. Older shapes a `from_dict` still migrates are listed in `shapes.LEGACY`. The only one found in every real save, pack and test saga was Secrets kept as one piece of text.
- **After building, every value against its type:** an int stands for a float, None only where a field allows it, and a bool is not an int.

Data from the network is checked strictly: an unknown key or an older shape is refused, as the same version of the app wrote it (the handshake refuses a version mismatch). Files are not checked strictly, as a newer copy of the app may have written keys this one keeps but doesn't know. A refusal is a ValueError naming the field ("characters[mag1].background: expected a record"). It costs about 16 ms on the largest save (The Limits of Magic, 2.5 MB, against about 30 ms to read it), so every load is checked.

## Considered options

- **One pass on the raw data, typed fully:** it would have to know every migration each `from_dict` makes, or refuse sound older saves.
- **One pass after building:** too late for a list where a record belongs, which already fails inside `from_dict`.
- **A validation library (pydantic and the like):** a second description of every record beside the dataclasses, and a dependency; the annotations already say what each field holds.
