# MCP Server For Bugzilla

Provides a few utilities to interact with a bugzilla instance.

Tools:

- Get Bug Information
- Get Bug comments

Prompts:

- summarize_bug_comments

# Installation

```
uv sync
uv run server.py
```

Starts the http server at `localhost:8000/mcp`

# Required Client HTTP Headers

- `api_key`: Bugzilla user API key
- `bugzilla_server`: Bugzilla instance (eg: bugzilla.opensuse.org)

# License

This project is licensed under `AGPLv3`
