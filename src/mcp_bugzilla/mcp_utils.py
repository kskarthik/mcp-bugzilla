"""
This is an MCP server for bugzilla which provides a few helpful
functions to assist the LLMs with required context

Author: Sai Karthik <kskarthik@disroot.org>
License: Apache 2.0
"""

import logging
import os
from typing import Any

import httpx


# logging config
class ColorFormatter(logging.Formatter):
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    CYAN = "\x1b[36;20m"
    BLUE = "\x1b[34;20m"
    GREEN = "\x1b[32;20m"

    FORMAT = "[%(levelname)s]: %(message)s"

    def format(self, record):
        log_fmt = self.FORMAT
        if isinstance(record.msg, str):
            if "[LLM-REQ]" in record.msg:
                log_fmt = self.CYAN + self.FORMAT + self.RESET
            elif "[LLM-RES]" in record.msg:
                log_fmt = self.CYAN + self.FORMAT + self.RESET
            elif "[BZ-REQ]" in record.msg:
                log_fmt = self.GREEN + self.FORMAT + self.RESET
            elif "[BZ-RES]" in record.msg:
                log_fmt = self.GREEN + self.FORMAT + self.RESET

        if record.levelno >= logging.ERROR:
            log_fmt = self.RED + self.FORMAT + self.RESET

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())

mcp_log = logging.getLogger("bugzilla-mcp")
mcp_log.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
mcp_log.addHandler(handler)
mcp_log.propagate = False  # Prevent double logging if root logger is configured


# Bugzilla API methods
class Bugzilla:
    """Bugzilla API class"""

    def __init__(self, url: str, api_key: str):
        self.api_url: str = url + "/rest"
        self.base_url: str = url
        self.api_key: str = api_key
        # request params sent for each request
        self.params: dict[str, Any] = {"api_key": self.api_key}

    def bug_info(self, bug_id: int) -> dict[str, Any]:
        """get information about a given bug"""
        url = f"{self.api_url}/bug/{bug_id}"
        mcp_log.info(f"[BZ-REQ] GET {url} params={self.params}")

        r = httpx.get(url=url, params=self.params)

        if r.status_code != 200:
            mcp_log.error(f"[BZ-RES] Failed: {r.status_code} {r.text}")
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        data = r.json()["bugs"][0]
        mcp_log.info(f"[BZ-RES] Found bug {bug_id}")
        mcp_log.debug(f"[BZ-RES] {data}")
        return data

    def bug_comments(self, bug_id: int) -> dict[str, Any]:
        """Get comments of a bug"""
        url = f"{self.api_url}/bug/{bug_id}/comment"
        mcp_log.info(f"[BZ-REQ] GET {url} params={self.params}")

        r = httpx.get(url=url, params=self.params)

        if r.status_code != 200:
            mcp_log.error(f"[BZ-RES] Failed: {r.status_code} {r.text}")
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        data = r.json()["bugs"][f"{bug_id}"]["comments"]
        mcp_log.info(f"[BZ-RES] Found {len(data)} comments")
        mcp_log.debug(f"[BZ-RES] {data}")
        return data

    def add_comment(
        self, bug_id: int, comment: str, is_private: bool
    ) -> dict[str, int]:
        """Add a comment to bug, which can optionally be private"""

        c = {"comment": comment, "is_private": is_private}
        url = f"{self.api_url}/bug/{bug_id}/comment"
        mcp_log.info(f"[BZ-REQ] POST {url} params={self.params} json={c}")

        r = httpx.post(url=url, params=self.params, json=c)

        if r.status_code != 201:
            mcp_log.error(f"[BZ-RES] Failed: {r.status_code} {r.text}")
            raise httpx.TransportError(
                f"Failed to fetch API with Status code: {r.status_code}"
            )

        data = r.json()
        mcp_log.info("[BZ-RES] Comment added successfully")
        mcp_log.debug(f"[BZ-RES] {data}")
        return data
