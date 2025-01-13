"""Base class for Amadeus tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from alibaba_ai_core.tools import BaseTool
from pydantic import Field

from aiagentsforce_community.tools.amadeus.utils import authenticate

if TYPE_CHECKING:
    from amadeus import Client


class AmadeusBaseTool(BaseTool):  # type: ignore[override]
    """Base Tool for Amadeus."""

    client: Client = Field(default_factory=authenticate)
