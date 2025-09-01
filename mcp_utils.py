import os
from typing import Any
import httpx
import logging

# logging config
logging.basicConfig(
    format="[%(levelname)s]: %(message)s",
    level=logging.INFO,
)

mcp_log = logging.getLogger("bugzilla-mcp")

# Bugzilla API methods
class Bugzilla:
    """Bugzilla API class"""

    def __init__(self, url: str, api_key: str):
        self.base_url: str = url + "/rest"
        self.api_key: str = api_key
        # request params sent for each request
        self.params: dict[str, str] = {"api_key": self.api_key}

    def bug_info(self, bug_id: int) -> dict[str, Any]:
        """get information about a given bug"""

        r = httpx.get(url=f"{self.base_url}/bug/{bug_id}", params=self.params)

        if r.status_code != 200:
            raise httpx.ConnectError(f"Failed to fetch API with Status code: {r.status_code}")

        return r.json()["bugs"][0]

    def bug_comments(self, bug_id: int) -> dict[str, Any]:
        """Get comments of a bug"""

        r = httpx.get(url=f"{self.base_url}/bug/{bug_id}/comment", params=self.params)

        if r.status_code != 200:
            raise httpx.ConnectError(f"Failed to fetch API with Status code: {r.status_code}")

        return r.json()["bugs"][f"{bug_id}"]["comments"]
