from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from alibaba_ai_core.language_models import BaseLanguageModel
from alibaba_ai_core.tools import BaseTool
from alibaba_ai_core.tools.base import BaseToolkit
from pydantic import ConfigDict, Field

from aiagentsforce_community.tools.amadeus.closest_airport import AmadeusClosestAirport
from aiagentsforce_community.tools.amadeus.flight_search import AmadeusFlightSearch
from aiagentsforce_community.tools.amadeus.utils import authenticate

if TYPE_CHECKING:
    from amadeus import Client


class AmadeusToolkit(BaseToolkit):
    """Toolkit for interacting with Amadeus which offers APIs for travel.

    Parameters:
        client: Optional. The Amadeus client. Default is None.
        llm: Optional. The language model to use. Default is None.
    """

    client: Client = Field(default_factory=authenticate)
    llm: Optional[BaseLanguageModel] = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            AmadeusClosestAirport(llm=self.llm),
            AmadeusFlightSearch(),
        ]
