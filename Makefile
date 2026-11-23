install:
	uv init
	uv add regex
	uv add pydantic

run:
	uv run parsing.py
