# Development

```
uv sync
```

We use ruff linter.
```
uvx ruff check
```

# Run

```
uv run metacycle-hello
```

# Upload to PyPI and then run as as a tool

Update version number in `pyproject.toml`

This is how end users will run the server in a single line.

```
rm -r dist/
uv build
uv publish --token $TOKEN
```

Open another terminal (wait a moment for PyPI to be updated):
```
uvx --from metacycle-core@latest metacycle-hello
```