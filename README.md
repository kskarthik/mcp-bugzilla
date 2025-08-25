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

- `api_key`: Bugzilla user's API key

# Environment Variables

`BUGZILLA_SERVER` must be set. Else, The program will exit with non success status code

 Example: `bugzilla.opensuse.org`

# License

This project is licensed under `AGPLv3`
