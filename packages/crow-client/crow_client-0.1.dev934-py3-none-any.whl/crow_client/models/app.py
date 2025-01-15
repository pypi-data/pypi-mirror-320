import os
import re
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Self

from ldp.agent import Agent
from ldp.alg.callbacks import Callback
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_CROW_JOB_RUN_TIMEOUT = 60 * 60 * 24  # 24 hours in sec
MIN_CROW_JOB_RUN_TIMEOUT = 0  # sec


class PythonVersion(StrEnum):
    V3_11 = "3.11"
    V3_12 = "3.12"


class Stage(StrEnum):
    DEV = "https://dev.api.scicraft.ai"
    PROD = "https://api.scicraft.ai"
    LOCAL = "http://localhost:8080"
    LOCAL_DOCKER = "http://host.docker.internal:8080"

    @classmethod
    def from_string(cls, stage: str) -> "Stage":
        """Convert a case-insensitive string to Stage enum."""
        try:
            return cls[stage.upper()]
        except KeyError as e:
            raise ValueError(
                f"Invalid stage: {stage}. Must be one of: {', '.join(cls.__members__)}"
            ) from e


class Step(StrEnum):
    BEFORE_TRANSITION = Callback.before_transition.__name__
    AFTER_AGENT_INIT_STATE = Callback.after_agent_init_state.__name__
    AFTER_AGENT_GET_ASV = Callback.after_agent_get_asv.__name__
    AFTER_ENV_RESET = Callback.after_env_reset.__name__
    AFTER_ENV_STEP = Callback.after_env_step.__name__
    AFTER_TRANSITION = Callback.after_transition.__name__


class FramePathContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF_LINK = "pdf_link"


class FramePath(BaseModel):
    path: str = Field(
        description="List of JSON path strings (e.g. 'input.data.frame') indicating where to find important frame data. None implies all data is important and the UI will render the full environment frame as is."
    )
    type: FramePathContentType = Field(
        default=FramePathContentType.JSON,
        description="Content type of the data at this path",
    )
    is_iterable: bool = Field(
        default=False,
        description="Content of the JSON path will be iterable, this key tell us if the rendering component should create multiple components for a single key",
    )


class DockerContainerConfiguration(BaseModel):
    cpu: str = Field(description="CPU allotment for the container")
    memory: str = Field(description="Memory allotment for the container")

    MINIMUM_MEMORY: ClassVar[int] = 2
    MAXIMUM_MEMORY: ClassVar[int] = 32

    @field_validator("cpu")
    @classmethod
    # The python library only supports 1, 2, 4, 8 CPUs
    # https://cloud.google.com/run/docs/reference/rpc/google.cloud.run.v2#resourcerequirements
    def validate_cpu(cls, v: str) -> str:
        valid_cpus = {"1", "2", "4", "8"}
        if v not in valid_cpus:
            raise ValueError("CPU must be one of: 1, 2, 4, or 8")
        return v

    @field_validator("memory")
    @classmethod
    def validate_memory(cls, v: str) -> str:
        # https://regex101.com/r/4kWjKw/1
        match = re.match(r"^(\d+)Gi$", v)

        if not match:
            raise ValueError("Memory must be in Gi format (e.g., '2Gi')")

        value = int(match.group(1))

        # GCP Cloud Run has min 512Mi and max 32Gi (32768Mi)
        # https://cloud.google.com/run/docs/configuring/services/memory-limits
        # due to the above mentioned restriction in the python client, we must
        # stay between 2Gi and 32Gi
        if value < cls.MINIMUM_MEMORY:
            raise ValueError("Memory must be at least 2Gi")
        if value > cls.MAXIMUM_MEMORY:
            raise ValueError("Memory must not exceed 32Gi")

        return v

    @model_validator(mode="after")
    def validate_cpu_memory_ratio(self) -> Self:
        cpu = int(self.cpu)

        match = re.match(r"^(\d+)Gi$", self.memory)
        if match is None:
            raise ValueError("Memory must be in Gi format (e.g., '2Gi')")

        memory_gi = int(match.group(1))
        memory_mb = memory_gi * 1024

        min_cpu_requirements = {
            2048: 1,  # 2Gi requires 1 CPU
            4096: 2,  # 4Gi requires 2 CPU
            8192: 4,  # 8Gi requires 4 CPU
            24576: 8,  # 24Gi requires 8 CPU
        }

        for mem_threshold, cpu_required in min_cpu_requirements.items():
            if memory_mb <= mem_threshold:
                if cpu < cpu_required:
                    raise ValueError(
                        f"For {self.memory} of memory, minimum required CPU is {cpu_required} CPU. Got {cpu} CPU"
                    )
                break

        return self


class CrowDeploymentConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,  # Allows for agent: Agent | str
    )

    path: str | os.PathLike = Field(
        description="The path to your python module. Can be either a string path or Path object. "
        "This path should be the root directory of your module. "
        "This path either must include a pyproject.toml with UV tooling, or a requirements.txt for dependency resolution."
    )

    environment: str = Field(
        description="Your environment path, should be a module reference. "
        "example: dummy_env.env.DummyEnv"
    )

    environment_variables: dict[str, str] | None = Field(
        default=None,
        description="Any key value pair of environment variables your environment needs to function.",
    )

    container_config: DockerContainerConfiguration | None = Field(
        default=None, description="The configuration for the cloud run container."
    )

    python_version: PythonVersion = Field(
        default=PythonVersion.V3_12,
        description="The python version your docker image should build with.",
    )

    agent: Agent | str = Field(
        default="ldp.agent.SimpleAgent",
        description="Your desired agent path, should be a module reference and a fully qualified name. "
        "example: ldp.agent.SimpleAgent",
    )

    requires_aviary_internal: bool = Field(
        default=False,
        description="Indicates your project requires aviary-internal to function. "
        "This is only necessary for envs within aviary-internal.",
    )

    timeout: int | None = Field(
        default=600,
        description="The amount of time in seconds your crow will run on a task before it terminates.",
        ge=MIN_CROW_JOB_RUN_TIMEOUT,
        le=MAX_CROW_JOB_RUN_TIMEOUT,
    )

    force: bool = Field(
        default=False,
        description="If true, immediately overwrite any existing job with the same name.",
    )

    storage_location: str = Field(
        default="storage",
        description="The location the container will use to mount a locally accessible GCS folder as a volume. "
        "This location can be used to store and fetch files safely without GCS apis or direct access.",
    )

    frame_paths: list[FramePath] | None = Field(
        default=None,
        description="List of FramePath which indicates where to find important frame data, and how to render it.",
    )

    @field_validator("path")
    @classmethod
    def validate_module_path(cls, value: str | os.PathLike) -> str | os.PathLike:
        path = Path(value)

        if not path.exists():
            raise ValueError(f"Module path {path} does not exist")
        if not path.is_dir():
            raise ValueError(f"Module path {path} is not a directory")

        if (
            not (path / "pyproject.toml").exists()
            and not (path / "requirements.txt").exists()
        ):
            raise ValueError(
                f"Module path {path} must contain either pyproject.toml or requirements.txt"
            )
        return value

    @field_validator("environment")
    @classmethod
    def validate_environment_path(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Environment path cannot be empty")
        if not all(part.isidentifier() for part in value.split(".")):
            raise ValueError(f"Invalid environment path format: {value}")
        return value

    @field_validator("agent")
    @classmethod
    def validate_agent_path(cls, value: Agent | str) -> Agent | str:
        if isinstance(value, Agent):
            return value

        if not value or not value.strip():
            raise ValueError("Agent path cannot be empty")
        if not all(part.isidentifier() for part in value.split(".")):
            raise ValueError(f"Invalid agent path format: {value}")
        return value
