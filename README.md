# sv_code_extractor

Extract SystemVerilog code snippets from LaTeX (Beamer) slide sources.

## Features
- `\begin{lstlisting}[language=Verilog|SystemVerilog]` blocks
- `\begin{minted}{systemverilog}` blocks
- Honors a global `\lstset{language=Verilog}` default
- Skips commented-out environments (`% \begin{lstlisting}...`)
- Annotates each snippet with source line number + frame title

## Usage
```bash
python3 extract_sv.py slides.tex                       # -> slides_snippets.sv
python3 extract_sv.py slides.tex -o out.sv --all       # keep untagged listings too
make SRC=slides.tex OUT=out.sv ARGS=--all
