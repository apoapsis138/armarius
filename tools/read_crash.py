"""Read a crash of the desktop app: what Windows recorded and where it was.

A crash inside Qt leaves no Python error. Windows keeps a minidump in
%LOCALAPPDATA%\\CrashDumps instead, and the app appends the Python stack to
crash.log in the data folder. This prints the two together:

    uv run python tools/read_crash.py              # the newest python.exe dump
    uv run python tools/read_crash.py <file.dmp>   # that dump
    uv run python tools/read_crash.py --all        # every frame, Windows' too

A dump holds each thread's stack but not the heap, so this shows which code
was running and not which object it had. The frames are every value on the
crashed thread's stack that points into a program's code, newest first. Some
are left over from calls already finished, so read them as clues. A name is
the nearest function that program exports, and a large offset after it means
a private function close by.
"""

import argparse
import datetime
import os
import re
import struct
import sys
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import crash_log, paths

_THREAD_LIST, _MODULE_LIST, _EXCEPTION = 3, 4, 6
_MISC_INFO = 15
_RSP = 0x98

EXCEPTIONS = {
    0xC0000005: "access violation: code used memory it doesn't own",
    0xC0000409: "fast fail: the program stopped itself at once",
    0xC00000FD: "stack overflow",
    0xE06D7363: "a C++ exception nobody caught",
}
#: What the first parameter of a fast fail means.
FAST_FAILS = {
    2: "stack buffer overrun",
    5: "invalid argument",
    7: "abort(): a fatal error, often a pure virtual call or a qFatal",
}
#: Windows' and Python's own frames, hidden without --all: they surround
#: every crash and say little about this one.
QUIET = re.compile(
    r"^(ntdll|kernel32|kernelbase|ucrtbase|python\d+|python|user32|win32u|gdi32|"
    r"gdi32full|combase|rpcrt4|oleaut32|oleacc|msctf|uiautomationcore|"
    r"msvcp140|vcruntime140|vcruntime140_1|winmm|userenv|mpr|sechost)\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Module:
    base: int
    size: int
    path: str

    @property
    def name(self) -> str:
        return self.path.replace("\\", "/").rsplit("/", 1)[-1]


@dataclass(frozen=True)
class Crash:
    """What a minidump says about its crash."""

    written: datetime.datetime
    started: datetime.datetime | None
    code: int
    fast_fail: int | None
    address: int
    modules: list[Module]
    #: The values on the crashed thread's stack, from the stack pointer up.
    stack: list[int]


def _local(stamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(stamp, datetime.UTC).astimezone()


def read_dump(data: bytes) -> Crash:
    """Parse a minidump's header, module list, exception and stack; a
    ValueError for a file that isn't one."""
    if data[:4] != b"MDMP":
        raise ValueError("not a minidump")
    count, directory = struct.unpack_from("<II", data, 8)
    stamp = struct.unpack_from("<I", data, 20)[0]
    streams: dict[int, int] = {}
    for i in range(count):
        kind, _size, rva = struct.unpack_from("<III", data, directory + i * 12)
        streams[kind] = rva
    if _EXCEPTION not in streams or _MODULE_LIST not in streams:
        raise ValueError("this dump records no crash")

    at = streams[_EXCEPTION]
    thread = struct.unpack_from("<I", data, at)[0]
    code = struct.unpack_from("<I", data, at + 8)[0]
    address = struct.unpack_from("<Q", data, at + 24)[0]
    parameters = struct.unpack_from("<I", data, at + 32)[0]
    first = struct.unpack_from("<Q", data, at + 40)[0]
    context = struct.unpack_from("<I", data, at + 164)[0]
    pointer = struct.unpack_from("<Q", data, context + _RSP)[0]

    return Crash(
        _local(stamp),
        _started(data, streams),
        code,
        first if code == 0xC0000409 and parameters else None,
        address,
        _modules(data, streams[_MODULE_LIST]),
        _stack(data, streams[_THREAD_LIST], thread, pointer),
    )


def _started(data: bytes, streams: dict[int, int]) -> datetime.datetime | None:
    if _MISC_INFO not in streams:
        return None
    flags, _pid, created = struct.unpack_from("<III", data, streams[_MISC_INFO] + 4)
    return _local(created) if flags & 2 else None


def _modules(data: bytes, at: int) -> list[Module]:
    modules = []
    for i in range(struct.unpack_from("<I", data, at)[0]):
        entry = at + 4 + i * 108
        base, size = struct.unpack_from("<QI", data, entry)
        name = struct.unpack_from("<I", data, entry + 20)[0]
        length = struct.unpack_from("<I", data, name)[0]
        path = data[name + 4 : name + 4 + length].decode("utf-16-le", "replace")
        modules.append(Module(base, size, path))
    return sorted(modules, key=lambda module: module.base)


def _stack(data: bytes, at: int, thread: int, pointer: int) -> list[int]:
    for i in range(struct.unpack_from("<I", data, at)[0]):
        entry = at + 4 + i * 48
        if struct.unpack_from("<I", data, entry)[0] != thread:
            continue
        start, size, rva = struct.unpack_from("<QII", data, entry + 24)
        skip = max(0, pointer - start)
        words = (size - skip) // 8
        return list(struct.unpack_from(f"<{words}Q", data, rva + skip))
    return []


def exports(image: bytes) -> list[tuple[int, str]]:
    """A Windows program's exported functions, (address, name), sorted."""
    header = struct.unpack_from("<I", image, 0x3C)[0]
    sections, _, _, _, optional_size = struct.unpack_from("<HIIIH", image, header + 6)
    optional = header + 24
    table = struct.unpack_from("<I", image, optional + 112)[0]
    if table == 0:
        return []
    spans = []
    for i in range(sections):
        size, address, _raw, pointer = struct.unpack_from(
            "<IIII", image, optional + optional_size + i * 40 + 8
        )
        spans.append((address, size, pointer))

    def offset(rva: int) -> int:
        for address, size, pointer in spans:
            if address <= rva < address + size:
                return rva - address + pointer
        raise ValueError(f"address {rva:#x} is in no section")

    named, functions, names, ordinals = struct.unpack_from(
        "<IIII", image, offset(table) + 24
    )
    found = []
    for i in range(named):
        name = struct.unpack_from("<I", image, offset(names) + i * 4)[0]
        ordinal = struct.unpack_from("<H", image, offset(ordinals) + i * 2)[0]
        address = struct.unpack_from("<I", image, offset(functions) + ordinal * 4)[0]
        start = offset(name)
        text = image[start : image.index(b"\0", start)].decode("ascii", "replace")
        found.append((address, text))
    return sorted(found)


def tidy(name: str) -> str:
    """A C++ export's name as written in the code, where it can be read
    off: ??1QObject@@... is QObject::~QObject."""
    destructor = re.match(r"\?\?1(\w+)@@", name)
    if destructor:
        return f"{destructor[1]}::~{destructor[1]}"
    method = re.match(r"\?(\w+)@([\w@]+?)@@", name)
    if not method:
        return name
    return "::".join([*reversed(method[2].split("@")), method[1]])


class Namer:
    """Names addresses by the programs in a dump, reading each program
    once. A program no longer on disk is named by its offset only."""

    def __init__(self, modules: list[Module]) -> None:
        self.modules = modules
        self.bases = [module.base for module in modules]
        self.tables: dict[str, tuple[list[int], list[str]]] = {}

    def module(self, address: int) -> Module | None:
        index = bisect_right(self.bases, address) - 1
        if index < 0:
            return None
        found = self.modules[index]
        return found if address < found.base + found.size else None

    def _table(self, module: Module) -> tuple[list[int], list[str]]:
        if module.path not in self.tables:
            try:
                found = exports(Path(module.path).read_bytes())
            except OSError, ValueError, struct.error:
                found = []
            self.tables[module.path] = (
                [address for address, _ in found],
                [tidy(name) for _, name in found],
            )
        return self.tables[module.path]

    def name(self, module: Module, address: int) -> str:
        offset = address - module.base
        starts, names = self._table(module)
        index = bisect_right(starts, offset) - 1
        if index < 0:
            return f"{module.name}+{offset:#x}"
        return f"{module.name}!{names[index]}+{offset - starts[index]:#x}"


def frames(crash: Crash, *, everything: bool = False) -> list[str]:
    """The named code addresses on the stack, newest first, with a
    repeat of the line above dropped."""
    namer = Namer(crash.modules)
    lines: list[str] = []
    for value in crash.stack:
        module = namer.module(value)
        # The first page of a program is its header, never code.
        if module is None or value - module.base < 0x1000:
            continue
        if not everything and QUIET.match(module.name):
            continue
        line = namer.name(module, value)
        if not lines or lines[-1] != line:
            lines.append(line)
    return lines


def summary(crash: Crash) -> list[str]:
    """What happened, in words."""
    namer = Namer(crash.modules)
    meaning = EXCEPTIONS.get(crash.code, "see Microsoft's NTSTATUS list")
    module = namer.module(crash.address)
    lines = [
        f"When:    {crash.written:%Y-%m-%d %H:%M:%S}",
        f"Code:    {crash.code:#010x} ({meaning})",
    ]
    if crash.started is not None:
        lines.insert(1, f"Running: {crash.written - crash.started} before it")
    if crash.fast_fail is not None:
        why = FAST_FAILS.get(crash.fast_fail, "unknown")
        lines.append(f"Reason:  {crash.fast_fail} ({why})")
    if module is not None:
        lines.append(f"Stopped: {namer.name(module, crash.address)}")
    return lines


def newest_dump(folder: Path) -> Path | None:
    dumps = list(folder.glob("python*.dmp"))
    return max(dumps, key=lambda path: path.stat().st_mtime) if dumps else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Read a desktop app crash.")
    parser.add_argument("dump", nargs="?", type=Path, help="default: the newest")
    parser.add_argument("--all", action="store_true", help="Windows' frames too")
    args = parser.parse_args()

    folder = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashDumps"
    dump = args.dump or newest_dump(folder)
    if dump is None:
        print(f"No python dump in {folder}.")
        return 1
    try:
        crash = read_dump(dump.read_bytes())
    except (OSError, ValueError, struct.error) as problem:
        print(f"Can't read {dump}: {problem}")
        return 1

    print(dump)
    print("\n".join(summary(crash)))
    print("\nCode on the stack, newest first:")
    for line in frames(crash, everything=args.all):
        print(f"  {line}")

    paths.use_data_dir(paths.data_dir())
    log = crash_log.log_path()
    written = log.read_text(encoding="utf-8") if log.exists() else ""
    print(f"\n{log}:")
    print(written.strip()[-4000:] if written.strip() else "  (empty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
