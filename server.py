"""
This is an MCP server for bugzilla which provides a few helpful
functions to assist the LLMs with required context

Author: Sai Karthik <kskarthik@disroot.org>
License: AGPLv3
"""

import os
import sys
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import PromptError, ToolError, ValidationError
from mcp_utils import Bugzilla, mcp_log
from typing import Any

# sets the bugzilla server
base_url = os.getenv("BUGZILLA_SERVER")

mcp = FastMCP("Bugzilla")

# check for the required headers which contain the api_key & bugzilla_server keys
# these are required by all the tools & prompts to make the api calls
class ValidateHeaders(Middleware):
    """Validate incoming HTTP headers"""

    async def on_request(self, context: MiddlewareContext, call_next):
        mcp_log.info("Validating Headers")

        headers = get_http_headers()

        if "api_key" in headers.keys():

            global bz

            # all the tools & prompts will use this for making api calls
            bz = Bugzilla(
                url=base_url, api_key=headers["api_key"]
            )

            mcp_log.info("Headers Validated")

            result = call_next(context)

            return await result
        else:
            raise ValidationError("`api_key` is header is required")

mcp.add_middleware(ValidateHeaders())

@mcp.tool()
def bug_information(id: int) -> dict[str, Any]:
    """Returns the entire information about a given bugzilla bug id"""

    mcp_log.info("tool: bug_info() is invoked")

    try:
        return bz.bug_info(id)

    except Exception:
        raise ToolError("Failed to fetch bug info")

@mcp.tool()
def bug_comments(id: int):
    """Returns the comments of given bugzilla bug ID"""

    mcp_log.info("tool: bug_comments() is invoked")

    try:
        return bz.bug_comments(id)

    except Exception as e:
        raise ToolError(f"Failed to fetch bug comments\nReason: {e}")

@mcp.prompt()
def summarize_bug_comments(id: int) -> str:
    """Summarizes all the comments of a bug"""

    mcp_log.info("prompt: summarize_bug_comments() is invoked")

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
