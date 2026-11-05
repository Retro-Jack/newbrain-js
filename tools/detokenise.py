#!/usr/bin/env python3
"""Detokenise a NewBrain BASIC tape file back to readable source.

    tools/detokenise.py tapes/Games/BreakOut.bas

Nothing else reads these tapes -- MAME loads them, it does not decode them --
so this was written from the Grundy Software Technical Manual plus the files
themselves. Three things have to be got right.

CONTAINER. A tape file is a run of blocks, exactly as src/tape.js splits them:
a 00, a two byte little-endian count, that many data bytes, a type byte, a two
byte checksum, and a nine byte trailer the writer lays down and nobody reads.
Block one holds the tape name; the program is every block after it.

REVERSAL. Each block's payload is stored BYTE-REVERSED, and the blocks stay
in file order. So reverse each payload on its own and concatenate; reversing
the whole stream instead looks right line for line, but silently splices
every line that straddles a block boundary onto the wrong neighbour. That bug
invented 200-odd "damaged" lines before a run under the emulator showed a
supposedly broken program working perfectly.

TWO TOKEN SETS. Keywords are single bytes 128-187, and the same value means
two different things: set 1 for the keyword that OPENS a statement, set 2 for
every keyword after it. 140 is NEXT at the start of a statement and "=" inside
one. A statement opens at the start of a line, after ":" and after THEN.

Bytes above 187 are not tokens at all -- they are text with bit 7 set, the
alternate half of the character set, so they mask back to ordinary letters.
"""
import re
import sys

SET1 = {
    128: "LET", 129: "LIST", 130: "NEW", 131: "PRINT", 132: "RUN",
    133: "GOTO", 134: "GOTO", 135: "GOSUB", 136: "GOSUB", 137: "IF",
    138: "INPUT", 139: "FOR", 140: "NEXT", 141: "RETURN", 142: "REM",
    143: "END", 144: "STOP", 145: "DIM", 146: "ON", 147: "OPTION",
    148: "SAVE", 149: "LOAD", 150: "RANDOMIZE", 151: "OPEN", 152: "CLOSE",
    153: "?", 154: "RET", 155: "RESTORE", 156: "READ", 157: "DATA",
    158: "POKE", 159: "CALL", 160: "CONTINUE", 161: "DEF", 162: "CLEAR",
    163: "MERGE", 164: "VERIFY", 165: "GET", 166: "RESUME", 167: "DELETE",
    168: "PUT", 169: "LINPUT", 170: "REPORT", 171: "CONT", 172: "RESERVE",
}
SET2 = {
    128: "NOT", 129: "+", 130: "-", 131: "*", 132: "/", 133: "^", 134: "&",
    135: "AND", 136: "OR", 137: "<>", 138: "<=", 139: ">=", 140: "=",
    141: ">", 142: "<", 143: "RND", 144: "PI", 145: "POS", 146: "ABS",
    147: "ATN", 148: "COS", 149: "EXP", 150: "INT", 151: "LOG", 152: "SGN",
    153: "SIN", 154: "SQR", 155: "TAN", 156: "TRUE", 157: "FALSE",
    158: "ASC", 159: "LEN", 160: "VAL", 161: "NUM", 162: "ASN", 163: "ACS",
    164: "PEEK", 165: "ERRNO", 166: "INSTR", 167: "ERRLIN", 168: "TOP",
    169: "FREE", 170: "CHR$", 171: "STR$", 172: "RIGHT$", 173: "FILES",
    174: "LEFT$", 175: "MID$", 176: "BASE", 177: "IN#", 178: "OUT#",
    179: "#", 180: "THEN", 181: "THEN", 182: "TO", 183: "STEP", 184: "FN",
    185: "TAB", 186: "ERROR", 187: "BREAK",
}


def _ch(b):
    """One data byte as text. The character set's top half is the same
    letters with bit 7 set; anything still unprintable is a graphics or
    control code and shows as a dot."""
    c = b & 0x7F
    return chr(c) if 32 <= c < 127 else '.'


def blocks(raw):
    """Split a tape file into (type, data) blocks."""
    out, p = [], 0
    while p + 3 <= len(raw) and raw[p] == 0x00:
        count = raw[p + 1] | (raw[p + 2] << 8)
        end = p + 3 + count
        if end + 3 > len(raw):
            break
        out.append((raw[end], raw[p + 3:end]))
        p = end + 3 + 9
    return out


def header(blks):
    """The tape name, from block one."""
    if not blks:
        return None
    name = bytes(blks[0][1])
    if name and all(32 <= b < 127 for b in name):
        return name.decode('ascii')
    return None


def detok_line(raw):
    """One restored line, bytes -> text."""
    out, initial, i = [], True, 0
    while i < len(raw) and raw[i:i + 1].isdigit():
        out.append(chr(raw[i]))
        i += 1
    out.append(' ')
    while i < len(raw) and raw[i] == 0x20:
        i += 1
    literal = False       # inside a quoted string
    rest_literal = False  # REM and DATA swallow the remainder
    while i < len(raw):
        b = raw[i]
        if rest_literal or literal:
            if not rest_literal and b == 0x22:
                literal = False
                out.append('"')
            else:
                out.append(_ch(b))
            i += 1
            continue
        if b == 0x22:
            literal = True
            out.append('"')
            i += 1
            continue
        if b >= 188:
            out.append(_ch(b))
            initial = False
            i += 1
            continue
        if b >= 128:
            kw = (SET1 if initial else SET2).get(b) or SET2.get(b, f"<{b}>")
            out.append(kw)
            if kw in ("REM", "DATA"):
                rest_literal = True
            initial = kw == "THEN"
            i += 1
            continue
        if b == 0x3A:     # ":" opens a new statement
            out.append(':')
            initial = True
            i += 1
            continue
        out.append(chr(b) if 32 <= b < 127 else '.')
        if b != 0x20:
            initial = False
        i += 1
    return ''.join(out).rstrip()


def detokenise(data):
    """-> (tape name, [lines]). Empty list means it is not BASIC."""
    blks = blocks(data)
    body = (b"".join(bytes(b[1])[::-1] for b in blks[1:]) if blks
            else data[::-1])
    lines, first = [], True
    for chunk in body.split(b'\r'):
        c = chunk.lstrip(b'\x00 ')
        if not c or not c[0:1].isdigit():
            first = False
            continue
        # Some tapes carry a short trailer after the last line; reversed, it
        # lands in front of the program and can mimic a line. No token exists
        # above 187, so a leading chunk holding one is not BASIC.
        if first and any(b > 187 for b in c):
            first = False
            continue
        first = False
        lines.append((int(re.match(rb'\d+', c).group()), detok_line(c)))
    lines.sort(key=lambda t: t[0])
    return header(blks), [t[1] for t in lines]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for path in sys.argv[1:]:
        name, lines = detokenise(open(path, 'rb').read())
        print(f"===== {path}   [tape name: {name}]   {len(lines)} lines")
        print("\n".join(lines))
