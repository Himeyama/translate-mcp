# Translate MCP Tool

A translation CLI and MCP (Model Context Protocol) server using OpenAI.

## Setup

1. Install [uv](https://github.com/astral-sh/uv).
2. Create a `.env` file from `.env.example` and set your `OPENAI_API_KEY`.
   ```bash
   cp .env.example .env
   ```
3. Sync dependencies:
   ```bash
   uv sync
   ```

## Usage

### CLI Mode

Translate a file directly via command line:

```bash
uv run translate --input test.txt --from English --to Japanese
```

### MCP Mode

Run the tool as an MCP server:

```bash
uv run translate --mcp
```

When running in MCP mode, you can use the `translate_file` tool with a JSON payload:

```json
{
  "path": "path/to/file.txt",
  "from_lang": "English",
  "to_lang": "Japanese"
}
```

## Error Handling

- **CLI Mode:** Errors are printed to stderr and the program exits with code 1.
- **MCP Mode:** Error messages are returned as part of the tool's response in JSON format.
