import json
import logging
import os
from pathlib import Path
from typing import Any, ClassVar
from uuid import UUID

import google.auth.transport.requests
import httpx
from google.auth import default
from google.auth.transport import requests
from google.oauth2 import service_account
from httpx import HTTPStatusError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from crow_client.models.app import (
    CrowDeploymentConfig,
    Stage,
)
from crow_client.utils.module_utils import (
    OrganizationSelector,
    fetch_environment_function_docstring,
)

logger = logging.getLogger(__name__)


FILE_UPLOAD_IGNORE_PARTS = {
    ".ruff_cache",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
}


class RestClientError(Exception):
    """Base exception for REST client errors."""


class JobFetchError(RestClientError):
    """Raised when there's an error fetching a job."""


class JobCreationError(RestClientError):
    """Raised when there's an error creating a job."""


class InvalidTaskDescriptionError(Exception):
    """Raised when the task description is invalid or empty."""


class RestClient:
    REQUEST_TIMEOUT: ClassVar[float] = 30.0  # sec
    MAX_RETRY_ATTEMPTS: ClassVar[int] = 3
    RETRY_MULTIPLIER: ClassVar[int] = 1
    MAX_RETRY_WAIT: ClassVar[int] = 10

    def __init__(self, stage: Stage = Stage.DEV):
        self.base_url = stage.value
        self.auth_jwt = self._run_auth()
        self.organizations = self._fetch_my_orgs()

    def _run_auth(self) -> str:
        # Service accounts cannot route through the same auth flow as user accounts
        # this path is almost exclusively used by CI
        service_account_json = os.getenv("SERVICE_ACCOUNT_JSON")
        if service_account_json is not None:
            service_account_info = json.loads(service_account_json)
            credentials = service_account.IDTokenCredentials.from_service_account_info(
                service_account_info,
                target_audience=self.base_url,
            )

            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            return credentials.token

        credentials, _ = default()
        auth_req = requests.Request()
        credentials.refresh(auth_req)
        return credentials.id_token

    def _check_job(self, name: str, organization: str) -> dict[str, Any]:
        try:
            with self.get_client() as client:
                response = client.get(
                    f"/check-crow/crow/{name}/organization/{organization}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise JobFetchError(f"Error checking job: {e!s}") from e

    def _fetch_my_orgs(self) -> list[str]:
        with self.get_client() as client:
            response = client.get("/my-organizations")
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _validate_module_path(path: Path) -> None:
        """
        Validates that the given path exists and is a directory.

        Args:
            path: Path to validate

        Raises:
            JobFetchError: If the path is not a directory
        """
        if not path.is_dir():
            raise JobFetchError(f"Path {path} is not a directory")

    @staticmethod
    def _validate_files(files: list, path: str | os.PathLike) -> None:
        """
        Validates that files were found in the given path.

        Args:
            files: List of collected files
            path: Path that was searched for files

        Raises:
            JobFetchError: If no files were found
        """
        if not files:
            raise JobFetchError(f"No files found in {path}")

    def get_client(self, content_type: str | None = "application/json") -> httpx.Client:
        """Get HTTP client with Google credentials from ADC.

        Args:
            content_type: Optional content type header. Set to None for multipart uploads.
        """
        headers = {"Authorization": f"Bearer {self.auth_jwt}"}
        if content_type:
            headers["Content-Type"] = content_type

        return httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.REQUEST_TIMEOUT,
        )

    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, max=MAX_RETRY_WAIT),
    )
    def get_job(self, job_id: str | None = None, history: bool = False):
        """Get details for a specific crow job."""
        try:
            job_id = job_id or self.trajectory_id
            with self.get_client() as client:
                response = client.get(
                    f"/crow-job/{job_id}", params={"history": history}
                )
                response.raise_for_status()
                return response.json()
        except ValueError as e:
            raise ValueError("Invalid job ID format. Must be a valid UUID.") from e
        except Exception as e:
            raise JobFetchError(f"Error getting job: {e!s}") from e

    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, max=MAX_RETRY_WAIT),
    )
    def create_job(self, data: dict):
        """Create a new crow job."""
        try:
            with self.get_client() as client:
                response = client.post("/crow-job", json=data)
                response.raise_for_status()
                self.trajectory_id = response.json()
                return self.trajectory_id
        except Exception as e:
            raise JobFetchError(f"Error getting job: {e!s}") from e

    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, max=MAX_RETRY_WAIT),
    )
    def get_build_status(self, build_id: UUID | None = None) -> dict[str, Any]:
        """Get the status of a build."""
        with self.get_client() as client:
            build_id = build_id or self.build_id
            response = client.get(f"/build-crow/{build_id}")
            response.raise_for_status()
            return response.json()

    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, max=MAX_RETRY_WAIT),
    )
    def create_crow(
        self,
        config: CrowDeploymentConfig,
    ) -> dict[str, Any]:
        """Creates a crow deployment from the environment and environment files.

        Args:
            config: Configuration object containing all necessary parameters for crow deployment.

        Returns:
            A response object containing metadata of the build.
        """
        selected_org = OrganizationSelector.select_organization(self.organizations)
        if selected_org is None:
            return {
                "status": "cancelled",
                "message": "Organization selection cancelled",
            }
        task_description: str = fetch_environment_function_docstring(
            config.environment, config.path, "from_task"
        )
        if not task_description or not task_description.strip():
            raise InvalidTaskDescriptionError(
                "Task description cannot be None or empty. Ensure your from_task environment function has a valid docstring."
            )

        try:
            module_name = config.path.name

            try:
                job_status = self._check_job(module_name, selected_org)
                if job_status["exists"]:
                    if config.force:
                        logger.warning(
                            f"Overwriting existing deployment '{job_status['name']}"
                        )
                    else:
                        user_response = input(
                            f"A deployment named '{module_name}' already exists. Do you want to proceed? [y/N]: "
                        )
                        if user_response.lower() != "y":
                            logger.info("Deployment cancelled.")
                            return {
                                "status": "cancelled",
                                "message": "User cancelled deployment",
                            }
            except Exception:
                logger.warning("Unable to check for existing deployment, proceeding.")

            files = []
            for file_path in config.path.rglob("*"):
                if any(
                    ignore in file_path.parts for ignore in FILE_UPLOAD_IGNORE_PARTS
                ):
                    continue

                if file_path.is_file():
                    relative_path = (
                        f"{module_name}/{file_path.relative_to(config.path)}"
                    )
                    files.append((
                        "files",
                        (
                            relative_path,
                            file_path.read_bytes(),
                            "application/octet-stream",
                        ),
                    ))

            self._validate_files(files, config.path)

            logger.debug(f"Sending files: {[f[1][0] for f in files]}")

            data = {
                "agent": config.agent,
                "organization": selected_org,
                "environment": config.environment,
                "python_version": config.python_version,
                "task_description": task_description,
                "environment_variables": json.dumps(config.environment_variables)
                if config.environment_variables
                else None,
                "container_config": config.container_config.model_dump_json()
                if config.container_config
                else None,
                "timeout": config.timeout,
                "storage_dir": config.storage_location,
                "frame_paths": json.dumps([
                    fp.model_dump() for fp in config.frame_paths
                ])
                if config.frame_paths
                else None,
            }

            with self.get_client(content_type=None) as client:
                response = client.post(
                    "/build-crow",
                    data=data,
                    files=files,
                    headers={"Accept": "application/json"},
                    params={"internal-deps": config.requires_aviary_internal},
                )
            try:
                response.raise_for_status()
                build_context = response.json()
                self.build_id = build_context["build_id"]
            except HTTPStatusError as e:
                error_detail = response.json()
                error_message = error_detail.get("detail", str(e))
                raise JobFetchError(f"Server validation error: {error_message}") from e
        except Exception as e:
            raise JobFetchError(f"Error generating docker image: {e!s}") from e
        return build_context
