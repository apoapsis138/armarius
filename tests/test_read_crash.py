"""tools/read_crash.py on a small minidump and program built by hand."""

from __future__ import annotations

import os
import struct

import pytest
import read_crash


def _dump(*, code: int = 0xC0000409, stack: tuple[int, ...] = ()) -> bytes:
    """A minidump of the three streams the tool reads: one program at
    0x1000000 and one thread, whose stack is `stack`."""
    path = "C:/x/Qt6Core.dll".encode("utf-16-le")
    directory = 32
    modules = directory + 36
    name = modules + 4 + 108
    exception = name + 4 + len(path)
    context = exception + 168
    threads = context + 0x100
    words = threads + 4 + 48
    head = b"MDMP" + struct.pack("<IIIIIQ", 0, 3, directory, 0, 1000, 0)
    table = struct.pack("<III", 4, 112, modules)
    table += struct.pack("<III", 6, 168, exception)
    table += struct.pack("<III", 3, 52, threads)
    module = struct.pack("<I", 1)
    module += struct.pack("<QIII", 0x1000000, 0x10000, 0, 0)
    module += struct.pack("<I", name).ljust(88, b"\0")
    names = struct.pack("<I", len(path)) + path
    record = struct.pack("<II", 7, 0) + struct.pack("<IIQQ", code, 0, 0, 0x1002000)
    record += struct.pack("<II", 1, 0) + struct.pack("<Q", 7)
    record = record.ljust(160, b"\0") + struct.pack("<II", 0x100, context)
    registers = bytearray(0x100)
    struct.pack_into("<Q", registers, read_crash._RSP, 0x5000)
    thread = struct.pack("<I", 1) + struct.pack("<I", 7).ljust(24, b"\0")
    thread += struct.pack("<QII", 0x5000, len(stack) * 8, words).ljust(24, b"\0")
    body = struct.pack(f"<{len(stack)}Q", *stack)
    return head + table + module + names + record + bytes(registers) + thread + body


def _program() -> bytes:
    """A program with one section and two named exports."""
    image = bytearray(0x400)
    struct.pack_into("<I", image, 0x3C, 0x80)
    optional_size = 240
    struct.pack_into("<HIIIH", image, 0x86, 1, 0, 0, 0, optional_size)
    struct.pack_into("<I", image, 0x98 + 112, 0x2000)
    # One section: 0x2000 in memory is 0x200 in the file.
    struct.pack_into(
        "<IIII", image, 0x98 + optional_size + 8, 0x200, 0x2000, 0x200, 0x200
    )
    struct.pack_into("<IIII", image, 0x200 + 24, 2, 0x2040, 0x2050, 0x2060)
    struct.pack_into("<II", image, 0x240, 0x1000, 0x1800)
    struct.pack_into("<II", image, 0x250, 0x2070, 0x2090)
    struct.pack_into("<HH", image, 0x260, 0, 1)
    image[0x270 : 0x270 + 22] = b"??1QObject@@UEAA@XZ\0\0\0"
    image[0x290 : 0x290 + 10] = b"plain\0\0\0\0\0"
    return bytes(image)


def test_a_dump_gives_its_code_time_reason_and_stack():
    crash = read_crash.read_dump(_dump(stack=(0x1002000, 5)))
    assert crash.code == 0xC0000409
    assert crash.fast_fail == 7
    assert crash.written.timestamp() == 1000
    assert crash.stack == [0x1002000, 5]
    assert crash.modules[0].name == "Qt6Core.dll"


@pytest.mark.parametrize("data", [b"nothing like a dump", b""])
def test_a_file_that_isnt_a_dump_is_refused(data):
    with pytest.raises(ValueError, match="not a minidump"):
        read_crash.read_dump(data)


def test_the_summary_says_what_a_fast_fail_means():
    lines = read_crash.summary(read_crash.read_dump(_dump()))
    assert any("fast fail" in line for line in lines)
    assert any("abort()" in line for line in lines)


def test_only_code_addresses_become_frames_and_a_repeat_is_dropped():
    crash = read_crash.read_dump(_dump(stack=(0x1001000, 0x1001000, 5, 0x1000010)))
    assert read_crash.frames(crash) == ["Qt6Core.dll+0x1000"]


def test_exports_are_read_and_sorted():
    assert read_crash.exports(_program()) == [
        (0x1000, "??1QObject@@UEAA@XZ"),
        (0x1800, "plain"),
    ]


def test_a_frame_is_named_by_the_export_before_it(tmp_path):
    program = tmp_path / "Qt6Core.dll"
    program.write_bytes(_program())
    module = read_crash.Module(0x1000000, 0x10000, str(program))
    namer = read_crash.Namer([module])
    assert namer.name(module, 0x1001010) == "Qt6Core.dll!QObject::~QObject+0x10"


@pytest.mark.parametrize(
    ("name", "shown"),
    [
        ("??1QObject@@UEAA@XZ", "QObject::~QObject"),
        ("?event@QWidget@@MEAA_NPEAVQEvent@@@Z", "QWidget::event"),
        (
            "?invalidate@Object@Shiboken@@YAXPEAUSbkObject@@@Z",
            "Shiboken::Object::invalidate",
        ),
        ("SbkDeallocWrapper", "SbkDeallocWrapper"),
    ],
)
def test_a_cpp_name_is_tidied(name, shown):
    assert read_crash.tidy(name) == shown


def test_the_newest_dump_is_found(tmp_path):
    assert read_crash.newest_dump(tmp_path) is None
    old, new = tmp_path / "python.exe.1.dmp", tmp_path / "python.exe.2.dmp"
    old.write_bytes(b"")
    new.write_bytes(b"")
    (tmp_path / "other.exe.3.dmp").write_bytes(b"")
    os.utime(old, (1, 1))
    assert read_crash.newest_dump(tmp_path) == new
