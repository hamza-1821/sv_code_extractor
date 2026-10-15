PYTHON ?= python3
SRC    ?= slides.tex
OUT    ?= $(basename $(SRC))_snippets.sv
ARGS   ?=

# Words after "clean" (make clean sv|tex|all) select what to delete.
CLEAN_WORDS := $(filter all tex sv,$(MAKECMDGOALS))

.DEFAULT_GOAL := all
.PHONY: all tex sv clean help

# With "make clean ...", the words all/tex/sv are options, not build targets.
ifneq ($(filter clean,$(MAKECMDGOALS)),)
all tex sv: ; @:
else
all: $(OUT) ## Extract SystemVerilog snippets from SRC into OUT (default)
endif

$(OUT): $(SRC) extract_sv.py
	$(PYTHON) extract_sv.py $(SRC) -o $(OUT) $(ARGS)

clean: ## Remove generated/input files (see "Clean options" below)
ifeq ($(CLEAN_WORDS),)
	rm -f $(OUT)
endif
ifneq ($(filter all sv,$(CLEAN_WORDS)),)
	rm -f *.sv
endif
ifneq ($(filter all tex,$(CLEAN_WORDS)),)
	rm -f *.tex
endif

help: ## Show this help
	@echo "Extract SystemVerilog code snippets from LaTeX slides."
	@echo
	@echo "Usage: make [target] [VARIABLE=value ...]"
	@echo
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*## ' $(firstword $(MAKEFILE_LIST)) | \
		awk 'BEGIN {FS = ":.*## "} {printf "  %-8s %s\n", $$1, $$2}'
	@echo
	@echo "Clean options:"
	@echo "  make clean       Remove OUT only"
	@echo "  make clean sv    Remove all *.sv files"
	@echo "  make clean tex   Remove all *.tex files"
	@echo "  make clean all   Remove all *.tex and *.sv files"
	@echo
	@echo "Variables:"
	@echo "  SRC=file.tex   Input LaTeX file         (default: $(SRC))"
	@echo "  OUT=file.sv    Output file              (default: <SRC>_snippets.sv)"
	@echo "  ARGS=--all     Extra script arguments; --all also keeps"
	@echo "                 listings with no language tag"
	@echo "  PYTHON=python  Python interpreter       (default: $(PYTHON))"
	@echo
	@echo "Examples:"
	@echo "  make"
	@echo "  make SRC=lecture3.tex"
	@echo "  make ARGS=--all"
	@echo "  make clean all"
