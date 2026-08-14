.PHONY: install dataset train test serve benchmark

install:
	pip install -r requirements-dev.txt -e .

dataset:
	python scripts/build_dataset.py

train:
	python scripts/train.py

test:
	pytest

serve:
	uvicorn app:app --host 0.0.0.0 --port 8000

benchmark:
	python scripts/benchmark_api.py
