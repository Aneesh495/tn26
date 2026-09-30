.PHONY: all venv install pipeline test dashboard api plots tables lint clean help

PYTHON = .venv/bin/python
PIP = .venv/bin/pip
PYTEST = .venv/bin/pytest
UVICORN = .venv/bin/uvicorn

all: pipeline test

venv:
	uv venv .venv --python 3.11

install:
	uv pip install -e .
	uv pip install httpx

pipeline:
	$(PYTHON) scripts/run_full_pipeline.py

test:
	$(PYTEST) -v

dashboard:
	$(PYTHON) -m tn26.dashboard.app

api:
	$(UVICORN) tn26.api.app:app --host 0.0.0.0 --port 8000 --reload

forensics:
	$(PYTHON) scripts/run_polling_forensics.py

econometrics:
	$(PYTHON) scripts/run_causal_econometrics.py

nlp:
	$(PYTHON) scripts/run_nlp_speech_analysis.py

tables:
	$(PYTHON) scripts/export_academic_tables.py

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

help:
	@echo "Available targets in tn26 Makefile:"
	@echo "  make pipeline     : Execute end-to-end research pipeline"
	@echo "  make test         : Run complete pytest test suite (29 tests)"
	@echo "  make dashboard    : Launch terminal research analytics dashboard"
	@echo "  make api          : Run FastAPI local development server"
	@echo "  make forensics    : Run polling failure statistical autopsy"
	@echo "  make econometrics : Run Synthetic Control & DiD models"
	@echo "  make nlp          : Run speech stylometrics and NLP analysis"
	@echo "  make tables       : Export publication tables in Markdown & LaTeX"
