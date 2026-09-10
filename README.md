# Remote MCP Server

A simple remote Model Context Protocol (MCP) server built with [FastMCP](https://github.com/jlowin/fastmcp).

## Features

- **Tools**:
  - `add`: Add two numbers together.
  - `random_number`: Generate a random integer within a specified range.
- **Resources**:
  - `info://server`: Returns server metadata in JSON format.
- **Transport**:
  - HTTP / Streamable HTTP support for remote client integration and testing with MCP Inspector.

## Getting Started

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Installation
```bash
uv sync
```

### Running the Server

#### Run directly with Python:
```bash
uv run python main.py
```

#### Run with FastMCP CLI:
```bash
uv run fastmcp run main.py --transport http --host 0.0.0.0 --port 8080
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```
Connect via `Streamable HTTP` using `http://127.0.0.1:8080/mcp`.
