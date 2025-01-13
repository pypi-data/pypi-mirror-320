"""**Docstores** are classes to store and load Documents.

The **Docstore** is a simplified version of the Document Loader.

**Class hierarchy:**

.. code-block::

    Docstore --> <name> # Examples: InMemoryDocstore, Wikipedia

**Main helpers:**

.. code-block::

    Document, AddableMixin
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.docstore.arbitrary_fn import (
        DocstoreFn,
    )
    from aiagentsforce_community.docstore.in_memory import (
        InMemoryDocstore,
    )
    from aiagentsforce_community.docstore.wikipedia import (
        Wikipedia,
    )

_module_lookup = {
    "DocstoreFn": "aiagentsforce_community.docstore.arbitrary_fn",
    "InMemoryDocstore": "aiagentsforce_community.docstore.in_memory",
    "Wikipedia": "aiagentsforce_community.docstore.wikipedia",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = ["DocstoreFn", "InMemoryDocstore", "Wikipedia"]
