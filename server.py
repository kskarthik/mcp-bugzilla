"""
This is an MCP server for bugzilla which provides a few helpful
functions to assist the LLMs with required context

Author: Sai Karthik <kskarthik@disroot.org>
License: Apache 2.0
"""

import os
import sys
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import PromptError, ToolError, ValidationError
import httpx
from mcp_utils import Bugzilla, mcp_log
from typing import Any

# sets the bugzilla server
base_url = os.getenv("BUGZILLA_SERVER")

mcp = FastMCP("Bugzilla")


# check for the required headers which contain the api_key header
# required by all the tools & prompts to make the api calls
class ValidateHeaders(Middleware):
    """Validate incoming HTTP headers"""

    async def on_message(self, context: MiddlewareContext, call_next):
        mcp_log.debug("api_key: Checking")

        headers = get_http_headers()
        if "api_key" in headers.keys():
            global bz
            # all the tools & prompts will use this for making api calls
            bz = Bugzilla(url=base_url, api_key=headers["api_key"])

            mcp_log.debug("api_key: Found")

            result = call_next(context)

            return await result
        else:
            raise ValidationError("`api_key` is header is required")


mcp.add_middleware(ValidateHeaders())


@mcp.tool()
def bug_info(id: int) -> dict[str, Any]:
    """Returns the entire information about a given bugzilla bug id"""

    mcp_log.debug("tool: bug_info() is invoked")

    try:
        return bz.bug_info(id)

    except Exception as e:
        raise ToolError(f"Failed to fetch bug info\nReason: {e}")


@mcp.tool()
def bug_comments(id: int, include_private_comments: bool = False):
    """Returns the comments of given bug id
    Private comments are not included by default
    but can be explicitely requested
    """

    mcp_log.debug("tool: bug_comments() is invoked")

    try:
        all_comments = bz.bug_comments(id)

        if include_private_comments:
            return all_comments

        public_comments = []

        for comment in all_comments:
            if not comment["is_private"]:
                public_comments.append(comment)

        return public_comments

    except Exception as e:
        raise ToolError(f"Failed to fetch bug comments\nReason: {e}")


@mcp.tool()
def add_comment(bug_id: int, comment: str, is_private: bool = False) -> dict[str, int]:
    """Add a comment to a bug. It can optionally be private. If success, returns the created comment id."""
    try:
        return bz.add_comment(bug_id, comment, is_private)
    except Exception as e:
        raise ToolError(f"Failed to create a comment\n{e}")


@mcp.tool()
def bugs_quicksearch(query: str, limit: int = 50, offset: int = 0) -> list[Any]:
    """Search bugs using bugzilla's quicksearch syntax

    To reduce the token limit & response time, only returns a subset of fields for each bug

    The user can query full details of each bug using the bug_info tool
    """

    mcp_log.debug("tool: bugs_quicksearch() is invoked")

    tool_params = bz.params
    tool_params["quicksearch"] = query
    tool_params["limit"] = limit
    tool_params["offset"] = offset

    r = httpx.get(f"{bz.api_url}/bug", params=tool_params)

    if r.status_code != 200:
        mcp_log.error(f"{r.json()}")
        raise ToolError(f"Search failed with status code {r.status_code}")

    all_bugs = r.json()["bugs"]

    bugs_with_essential_fields = []

    for bug in all_bugs:
        b = {
            "bug_id": bug["id"],
            "product": bug["product"],
            "component": bug["component"],
            "assigned_to": bug["assigned_to"],
            "status": bug["status"],
            "resolution": bug["resolution"],
            "summary": bug["summary"],
            "last_updated": bug["last_change_time"],
        }

        bugs_with_essential_fields.append(b)

    return bugs_with_essential_fields


@mcp.tool()
def learn_quicksearch_syntax() -> str:
    """Access the documentation of the bugzilla quicksearch syntax.
    LLM can learn using this tool. Response is in HTML"""

    mcp_log.debug("tool: learn_quicksearch_syntax is invoked")

    r = httpx.get(f"{bz.base_url}/page.cgi?id=quicksearch.html")

    if r.status_code != 200:
        raise PromptError(
            f"Failed to fetch bugzilla quicksearch_syntax with status code {r.status_code}"
        )

    return r.text

@mcp.tool()
def server_url() -> str:
    """bugzilla server's base url"""
    return bz.base_url

@mcp.tool()
def bug_url(bug_id: int) -> str:
    """returns the bug url"""
    return f"{bz.base_url}/show_bug.cgi?id={bug_id}"

@mcp.prompt()
def summarize_bug_comments(id: int) -> str:
    """Summarizes all the comments of a bug"""

    mcp_log.debug("prompt: summarize_bug_comments() is invoked")

    try:
        comments = bz.bug_comments(id)

        return f"""
    You are an expert in summarizing bugzilla comments.
    Rules to follow:
    - Comments are in JSON
    - Summary must be well structured & eye catching
    - Mention usernames & dates wherever relevant.
    - date field must be in human readable format
    - Usernames must be bold italic (***username***) dates must be bold (**date**)\n{comments}`;""".strip()

    except Exception as e:
        raise PromptError(f"Summarize Comments Failed\nReason: {e}")


# exit if the env variable is not set
if base_url is None:
    mcp_log.critical("env `BUGZILLA_SERVER` must be set. Exiting")
    sys.exit(1)

# start the MCP server
mcp.run(transport="http")
