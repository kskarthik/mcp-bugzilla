# MCP Server For Bugzilla

Provides a few utilities to interact with a bugzilla instance.

Tools:

- `bug_information`: Get the bug information
- `bug_comments`: Fetches all bug comments (including private comments)
- `add_comment`: Add a bug comment. Default is public. Can be optionally set to private

Prompts:

- `summarize_bug_comments`: Summarize all the comments of a give bug id

# Installation

```
uv sync
uv run server.py
```

Starts the `http` server at `http://127.0.0.1:8000/mcp/`

# Required Client HTTP Headers

- `api_key`: Bugzilla user's API key. To create one, refer the [official doc](https://bugzilla.readthedocs.io/en/latest/api/core/v1/general.html#authentication)

# Environment Variables

`BUGZILLA_SERVER` must be set. Else, The program will exit with a non-success status code.

Example:
```
export BUGZILLA_SERVER='https://bugzilla.opensuse.org'
```

# License

This project is licensed under `AGPLv3`. You can obtain a copy from https://www.gnu.org/licenses/agpl-3.0.txt
