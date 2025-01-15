# AppOmni ALIGN Tools

Tools for working with ALIGN parser files, including a schema validator/linter.

## Installation

Using Poetry:
```bash
poetry add appomni-align-tools
```

Using pip:
```bash
pip install appomni-align-tools
```

## Tools

### ALIGN Linter

A linter for validating ALIGN parser files. The linter checks for:

- Valid ALIGN commands
- Valid field paths according to the schema
- Valid enum values
- Type compatibility for conversions

#### Usage

Basic usage:
```bash
align-lint path/to/file.conf --schema path/to/schema.json
```

Lint multiple files:
```bash
align-lint path/to/*.conf --schema path/to/schema.json
```

Options:
- `--schema`: Path to JSON schema file (required)
- `--verbose`, `-v`: Enable verbose output

#### GitHub Action

Add this to your repository's workflow file (e.g., `.github/workflows/align-lint.yml`):

```yaml
name: ALIGN Linter

on:
  push:
    paths:
      - '**.conf'
  pull_request:
    paths:
      - '**.conf'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install Poetry
        run: |
          pipx install poetry
          
      - name: Install dependencies
        run: |
          poetry install appomni-align-tools

      - name: Run ALIGN linter
        env:
          SCHEMA_PATH: ${{ inputs.schema-path || 'schemas/ACES.json' }}
        run: |
          poetry run align-lint $(find . -name "*.conf") --schema "$SCHEMA_PATH"
```

#### Supported Commands

The linter validates the following ALIGN commands:
- `append`
- `copy`
- `convert`
- `convert_nested`
- `date`
- `dedupe`
- `del`
- `from_json`
- `http`
- `parse_ip`
- `parse_sql`
- `parse_user_agent`
- `regex_capture`
- `rename`
- `set`
- `split`
- `to_json`
- `translate`

## Development

### Setup

```bash
# Install dependencies
poetry install

# Run tests
pytest tests/
```
### Supporting Changes to Align
Generate new Lexer, Listener, and Parser via ANTLR and push generated files into `align` folder.

```bash
antlr4 -Dlanguage=Python3 -o align Align.g4
```

### Adding New Validations

The linter can be extended by adding new validation methods to the `AlignParserLinter` class in `linter.py`.

## GitHub Annotations

When used in GitHub Actions, the linter will create annotations in pull requests for any issues found, showing:
- The specific line and column where the issue was found
- A description of the error
- The file containing the error

This makes it easy to spot and fix issues directly in the PR interface.