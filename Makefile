install:
	uv init
	uv add regex
	uv add pydantic
	uv add pygame

run:
	uv run parsing.py
