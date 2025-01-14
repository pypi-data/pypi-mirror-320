from dataclasses import dataclass
from typing import TypedDict, NotRequired


@dataclass
class ServiceAccountInfo(TypedDict):
    client_email: str
    private_key: str
    token_uri: NotRequired[str]
    project_id: NotRequired[str]
