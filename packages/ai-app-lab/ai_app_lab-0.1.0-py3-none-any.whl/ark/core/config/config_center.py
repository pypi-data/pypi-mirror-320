import copy
import logging
import os
from typing import Any, Dict, List, Optional

import aiofiles
import yaml
from pydantic import BaseModel, Field

from ark.core.config.action_config import AtomActionConfig
from ark.core.config.endpoint_config import EndpointConfig
from ark.core.idl.ark_protocol import ArkGroupChatConfig
from ark.core.utils.common import LazyLoadSingleton, Singleton
from ark.core.utils.dict import dict_merge

CONFIG_CENTER_DIR = "CONFIG_CENTER_DIR"
CONFIG_CENTER_NAME = "CONFIG_CENTER_NAME"
ConfEnv = "CONF_ENV"


class Settings(BaseModel, Singleton):
    conf_dir: str
    conf_name: str

    def __init__(self) -> None:
        super().__init__(
            conf_dir=os.getenv(CONFIG_CENTER_DIR, "./"),
            conf_name=os.getenv(CONFIG_CENTER_NAME, "pipeline"),
        )


class PipelineConfig(BaseModel):
    tenant_id: Optional[str] = Field(default="")
    account_id: Optional[str] = Field(default="")
    utm_source: Optional[str] = Field(default="")
    atom_action_config: List[AtomActionConfig] = Field(default_factory=list)
    group_chat_config: Optional[ArkGroupChatConfig] = Field(
        default_factory=ArkGroupChatConfig
    )

    llm_config: Dict[str, EndpointConfig] = Field(default_factory=dict)
    action_config: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def merge_from(self, other: Optional["PipelineConfig"] = None) -> "PipelineConfig":
        other_dict = other.__dict__ if other else {}
        merged_dict = copy.deepcopy(self.__dict__)
        return PipelineConfig(**dict_merge(merged_dict, other_dict))


class ConfigCenter(PipelineConfig, LazyLoadSingleton):
    def __init__(self, settings: Optional[Settings] = None, **kwargs: Any):
        if not kwargs:
            settings = Settings() if settings is None else settings
            conf_path = os.path.join(settings.conf_dir, f"{settings.conf_name}.yaml")

            with open(conf_path, mode="r") as f:
                kwargs = yaml.safe_load(f)
            logging.info(f"loading config:{kwargs}")
        super().__init__(**kwargs)

    @classmethod
    async def async_init(
        cls, settings: Optional[Settings] = None, **kwargs: Any
    ) -> "ConfigCenter":
        if not kwargs:
            settings = Settings() if settings is None else settings
            conf_path = os.path.join(settings.conf_dir, f"{settings.conf_name}.yaml")
            async with aiofiles.open(conf_path, mode="r") as f:
                kwargs = yaml.safe_load(await f.read())
            logging.info(f"loading config:{kwargs}")
        return cls(**kwargs)
