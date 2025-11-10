# Bugzilla Model context protocol (MCP) Server

This project provides a robust MCP server for seamless interaction with a Bugzilla instance. It exposes a set of powerful tools and prompts, enabling AI models and other clients to efficiently query bug information, manage comments, and leverage Bugzilla's quicksearch capabilities.

## Features

### Tools

The following tools are available to interact with Bugzilla:

-   `bug_info(id: int)`: Retrieves the comprehensive details for a specified Bugzilla bug ID.
    *   **Returns:** A dictionary containing all available information about the bug.
-   `bug_comments(id: int, include_private_comments: bool = False)`: Fetches all comments associated with a given bug ID. By default, private comments are excluded but can be explicitly requested.
    *   **Returns:** A list of comment dictionaries.
-   `add_comment(bug_id: int, comment: str, is_private: bool = False)`: Adds a new comment to a specified bug. Comments are public by default but can be marked as private.
    *   **Returns:** A dictionary containing the ID of the newly created comment.
-   `bugs_quicksearch(query: str, limit: int = 50, offset: int = 0)`: Executes a search for bugs using Bugzilla's powerful [quicksearch syntax](https://bugzilla.readthedocs.io/en/latest/using/finding.html#quicksearch). To optimize token usage and response times, this tool returns a curated subset of essential fields for each bug. Full details for individual bugs can be obtained using the `bug_info` tool. Supports pagination via `limit` and `offset` parameters.
    *   **Returns:** A list of dictionaries, each representing a bug with key details.
-   `learn_quicksearch_syntax()`: Provides access to the official Bugzilla quicksearch syntax documentation, allowing LLMs to learn and formulate effective queries.
    *   **Returns:** The quicksearch documentation content in HTML format.
-   `server_url()`: Returns the base URL of the configured Bugzilla server.
    *   **Returns:** A string representing the base URL.
-   `bug_url(bug_id: int)`: Constructs and returns the direct URL to a specific bug on the Bugzilla server.
    *   **Returns:** A string representing the bug's URL.

### Prompts

Currently, one prompt is available to assist with common tasks:

-   `summarize_bug_comments(id: int)`: Generates a detailed summary of all comments for a given bug ID.
    *   **Returns:** A well-structured, eye-catching summary of the bug's comments, highlighting usernames and dates.

## Getting Started

To set up and run the Bugzilla MCP Server, follow these steps:

## Installation

### Docker / Podman

Official docker repo: https://hub.docker.com/r/kskarthik/mcp-bugzilla/

### From Source

1. Clone this repo

2. **Install dependencies and lock them:**
    ```bash
    uv sync
    ```
3.  **Run the server:**
    ```bash
    uv run server.py
    ```
    This will start the HTTP server at `http://127.0.0.1:8000/mcp/`.

### Required Client HTTP Headers

-   `api_key`: Your Bugzilla user's API key. For instructions on how to generate an API key, please refer to the [official Bugzilla documentation on authentication](https://bugzilla.readthedocs.io/en/latest/api/core/v1/general.html#authentication).

### Environment Variables

The server requires one critical environment variable to be set:

-   `BUGZILLA_SERVER`: The base URL of your Bugzilla instance. If this variable is not set, the program will exit with a non-success status code.

    **Example:**
    ```bash
    export BUGZILLA_SERVER='https://bugzilla.opensuse.org'
    ```

## License

This project is licensed under the `Apache 2.0` License. You can find a copy of the license agreement at [https://www.apache.org/licenses/LICENSE-2.0.txt](https://www.apache.org/licenses/LICENSE-2.0.txt).
