import logging
from dataclasses import dataclass

import requests
from pydantic import BaseModel

from graph_sitter.testing.constants import GET_CODEMODS_URL_SUFFIX, UPDATE_CODEMOD_DIFF_URL_SUFFIX

logger = logging.getLogger(__name__)


class CodemodAPI:
    def __init__(self, api_key: str | None = None, modal_prefix: str = "https://codegen-sh"):
        self.api_key = api_key
        self.modal_prefix = modal_prefix
        self.get_codemods_url = f"{self.modal_prefix}--{GET_CODEMODS_URL_SUFFIX}"
        self.update_diff_url = f"{self.modal_prefix}--{UPDATE_CODEMOD_DIFF_URL_SUFFIX}"

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _make_request(self, url: str, input_data: dict) -> requests.Response:
        """Helper method to make HTTP requests with common headers and error handling"""
        try:
            response = requests.post(
                url,
                json={"input": input_data},
                headers=self._get_headers(),
            )
            if response.status_code != 200:
                logger.error(f"Error making request: {response.status_code} {response.text}")
                raise Exception(f"Error making request: {response.status_code} {response.text}")
            return response
        except requests.RequestException as e:
            logger.error(f"Error making request: {e}")
            raise e

    def get_verified_codemods(self, repo_id: int, codemod_id: int | None = None, base_commit: str | None = None) -> dict[str, dict]:
        """Get verified codemods for a given repo"""
        input_data = {"repo_id": repo_id}
        if codemod_id:
            input_data["codemod_id"] = codemod_id
        if base_commit:
            input_data["base_commit"] = base_commit

        response = self._make_request(self.get_codemods_url, input_data)
        return response.json()

    def update_snapshot(self, repo_app_id: int, diff: str) -> bool:
        """Send snapshot data to external DB via API
        Returns True if successful, False otherwise
        """
        try:
            self._make_request(self.update_diff_url, {"repo_app_id": repo_app_id, "new_diff": diff})
            return True
        except Exception:
            return False


@dataclass
class SkillTestConfig:
    codemod_id: str | None
    repo_id: str | None
    base_commit: str | None
    api_key: str | None

    @classmethod
    def from_metafunc(cls, metafunc) -> "SkillTestConfig":
        return cls(
            codemod_id=metafunc.config.getoption("--codemod-id"),
            repo_id=metafunc.config.getoption("--repo-id"),
            base_commit=metafunc.config.getoption("--base-commit"),
            api_key=metafunc.config.getoption("--cli-api-key"),
        )


class UpdateDiffInput(BaseModel):
    repo_app_id: int
    new_diff: str
