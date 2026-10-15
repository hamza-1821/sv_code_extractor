#!/usr/bin/env python3
"""Extract SystemVerilog code snippets from LaTeX (Beamer) slide source.

Handles:
  \\begin{lstlisting}[language=Verilog|SystemVerilog|...] ... \\end{lstlisting}
  \\begin{minted}{systemverilog} ... \\end{minted}
Listings with no language are kept only if \\lstset sets a Verilog default
or --all is given. Commented-out environments are skipped.

Usage:
  python extract_sv.py slides.tex                 # -> slides_snippets.sv
  python extract_sv.py slides.tex -o out.sv --all
"""
import argparse
import bisect
import re
import textwrap
from pathlib import Path

SV_RE = re.compile(r"system\s*verilog|verilog|\bsv\b", re.I)
OPTS = r"(?:\[((?:[^\[\]]|\[[^\]]*\])*)\])?"  # [..] allowing one nesting level

LST_RE = re.compile(r"\\begin\{lstlisting\}" + OPTS + r"[ \t]*\n?(.*?)\\end\{lstlisting\}", re.S)
MINTED_RE = re.compile(r"\\begin\{minted\}" + OPTS + r"\{(\w+)\}[ \t]*\n?(.*?)\\end\{minted\}", re.S)
TITLE_RE = re.compile(
    r"\\frametitle\{([^}]*)\}|\\begin\{frame\}(?:<[^>]*>)?(?:\[[^\]]*\])?\{([^}]*)\}")
GLOBAL_LANG_RE = re.compile(r"\\lstset\{[^}]*language\s*=\s*\{?[^,}]*verilog", re.I | re.S)


def is_commented(src, pos):
    line_start = src.rfind("\n", 0, pos) + 1
    return src[line_start:pos].lstrip().startswith("%")


def extract(src, take_untagged):
    default_sv = bool(GLOBAL_LANG_RE.search(src))
    titles = [(m.start(), (m.group(1) or m.group(2) or "").strip())
              for m in TITLE_RE.finditer(src)]
    title_pos = [p for p, _ in titles]

    def title_at(pos):
        i = bisect.bisect_right(title_pos, pos) - 1
        return titles[i][1] if i >= 0 else ""

    found = []
    for m in LST_RE.finditer(src):
        if is_commented(src, m.start()):
            continue
        opts, body = m.group(1) or "", m.group(2)
        if SV_RE.search(opts):
            keep = True
        elif re.search(r"language\s*=", opts):
            keep = False  # explicitly another language
        else:
            keep = default_sv or take_untagged
        if keep:
            found.append((m.start(), body))

    for m in MINTED_RE.finditer(src):
        if is_commented(src, m.start()):
            continue
        if SV_RE.search(m.group(2)):
            found.append((m.start(), m.group(3)))

    found.sort()
    return [(src.count("\n", 0, pos) + 1, title_at(pos), textwrap.dedent(body).strip("\n").rstrip())
            for pos, body in found]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("tex", help="LaTeX source file")
    ap.add_argument("-o", "--output", help="output file (default: <tex>_snippets.sv)")
    ap.add_argument("--all", action="store_true",
                    help="also keep lstlisting blocks that specify no language")
    args = ap.parse_args()

    tex = Path(args.tex)
    src = tex.read_text(encoding="utf-8", errors="replace")
    out = Path(args.output) if args.output else tex.with_name(tex.stem + "_snippets.sv")

    snippets = extract(src, args.all)
    parts = []
    for n, (line, title, code) in enumerate(snippets, 1):
        header = f"// ===== Snippet {n} | line {line}" + (f" | {title}" if title else "") + " ====="
        parts.append(f"{header}\n{code}\n")
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {len(snippets)} snippet(s) to {out}")


if __name__ == "__main__":
    main()
