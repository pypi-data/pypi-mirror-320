from __future__ import annotations

import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BaseRepoConfig(BaseModel):
    """Base version of RepoConfig that does not depend on the db."""

    name: str = ""
    respect_gitignore: bool = True
