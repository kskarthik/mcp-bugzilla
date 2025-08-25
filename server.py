"""
This is an MCP server for bugzilla which provides a few helpful
functions to assist the LLMs with required context

It uses the https://pypi.org/project/python-bugzilla/ library
to retrieve the required info

Author: Sai Karthik <kskarthik@disroot.org>
License: AGPLv3
"""

import logging
import os
import sys
from fastmcp import FastMCP
import bugzilla
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import PromptError, ToolError, ValidationError

# logging config
logging.basicConfig(
    format="[%(levelname)s]: %(message)s",
    level=logging.INFO,
)

log = logging.getLogger("bz-mcp")

# serves as a delimiter when converting the bug comments of an api response as a string
comment_delimiter = "+-+-+"

# sets the bugzilla server
base_url = os.getenv("BUGZILLA_SERVER")

mcp = FastMCP("Bugzilla")

# check for the required headers which contain the api_key & bugzilla_server keys
# these are required by all the tools & prompts to make the api calls
class ValidateHeaders(Middleware):
    """Validate incoming HTTP headers"""

    async def on_request(self, context: MiddlewareContext, call_next):
        log.info("Validating Headers")

        headers = get_http_headers()

        if "api_key" in headers.keys():

            global bz

            # all the tools & prompts will use this for making api calls
            bz = bugzilla.Bugzilla(
                url=base_url, api_key=headers["api_key"]
            )

            log.info("Headers Validated")

            result = call_next(context)

            return await result
        else:
            raise ValidationError("Required headers not set")


mcp.add_middleware(ValidateHeaders())


def bug_comments_string(id: int) -> str:
    """Utility which returns the comments of given bug ID as a string"""
    try:
        bug = bz.getbug(id)
        c = ""
        for comment in bug.getcomments():
            # extract username from the email id
            username = comment["creator"].split("@")[0]

            if "." in username:
                username = username.replace(".", " ")

            c += f"""
            Name: {username.capitalize()}
            Date: {str(comment["time"])}
            Comment: {comment["text"]}
            {comment_delimiter}"""

        return c.strip()
    except Exception:
        raise ToolError


@mcp.tool()
def bug_info(id: int) -> str:
    """Returns the information of a given bug"""

    log.info("tool: bug_info() is invoked")

    try:
        bug = bz.getbug(id)

        return f"""
        Product: {bug.product}
        Component: {bug.component}
        Status: {bug.status}
        Resolution: {bug.resolution}
        Summary: {bug.summary}"""

    except Exception:
        raise ToolError("Failed to fetch bug info")


@mcp.tool()
def bug_comments(id: int) -> str:
    """Returns the comments of given bug ID"""

    log.info("tool: bug_comments() is invoked")

    try:
        return bug_comments_string(id)
    except Exception:
        raise ToolError("Failed to fetch bug comments")


@mcp.prompt()
def summarize_bug_comments(id: int) -> str:
    """Summarizes all the comments of a bug"""

    log.info("prompt: summarize_bug_comments() is invoked")

    comments: str = ""

    try:
        comments = bug_comments_string(id)
        return f"""
    You are an expert in summarizing bugzilla comments.
    Rules to follow:
    - Each comment block below is delimited by "${comment_delimiter}"
    - Each comment block contains the Username:  Date: Comment: fields which are self explanatory
    - Summary must be well structured & eye catching
    - Your entire response must be in GitHub-flavored Markdown. Do not use raw HTML
    - Mention usernames & dates wherever relevant.
    - Date: field must be in human readable format
    - Usernames must be bold italic (***username***) dates must be bold (**date**)
     {comment_delimiter}
     {comments}`;""".strip()
    except Exception:
        raise PromptError("Summarize Comments Failed")

# exit if the env variable is not set
if base_url is None:
        log.critical("env `BUGZILLA_SERVER` must be set. Exiting")
        sys.exit(1)

# start the MCP server
mcp.run(transport="http")
