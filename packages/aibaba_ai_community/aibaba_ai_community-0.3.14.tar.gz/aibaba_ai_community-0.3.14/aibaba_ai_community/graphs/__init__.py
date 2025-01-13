"""**Graphs** provide a natural language interface to graph databases."""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.graphs.arangodb_graph import (
        ArangoGraph,
    )
    from aiagentsforce_community.graphs.falkordb_graph import (
        FalkorDBGraph,
    )
    from aiagentsforce_community.graphs.gremlin_graph import (
        GremlinGraph,
    )
    from aiagentsforce_community.graphs.hugegraph import (
        HugeGraph,
    )
    from aiagentsforce_community.graphs.kuzu_graph import (
        KuzuGraph,
    )
    from aiagentsforce_community.graphs.memgraph_graph import (
        MemgraphGraph,
    )
    from aiagentsforce_community.graphs.nebula_graph import (
        NebulaGraph,
    )
    from aiagentsforce_community.graphs.neo4j_graph import (
        Neo4jGraph,
    )
    from aiagentsforce_community.graphs.neptune_graph import (
        BaseNeptuneGraph,
        NeptuneAnalyticsGraph,
        NeptuneGraph,
    )
    from aiagentsforce_community.graphs.neptune_rdf_graph import (
        NeptuneRdfGraph,
    )
    from aiagentsforce_community.graphs.networkx_graph import (
        NetworkxEntityGraph,
    )
    from aiagentsforce_community.graphs.ontotext_graphdb_graph import (
        OntotextGraphDBGraph,
    )
    from aiagentsforce_community.graphs.rdf_graph import (
        RdfGraph,
    )
    from aiagentsforce_community.graphs.tigergraph_graph import (
        TigerGraph,
    )

__all__ = [
    "ArangoGraph",
    "FalkorDBGraph",
    "GremlinGraph",
    "HugeGraph",
    "KuzuGraph",
    "BaseNeptuneGraph",
    "MemgraphGraph",
    "NebulaGraph",
    "Neo4jGraph",
    "NeptuneGraph",
    "NeptuneRdfGraph",
    "NeptuneAnalyticsGraph",
    "NetworkxEntityGraph",
    "OntotextGraphDBGraph",
    "RdfGraph",
    "TigerGraph",
]

_module_lookup = {
    "ArangoGraph": "aiagentsforce_community.graphs.arangodb_graph",
    "FalkorDBGraph": "aiagentsforce_community.graphs.falkordb_graph",
    "GremlinGraph": "aiagentsforce_community.graphs.gremlin_graph",
    "HugeGraph": "aiagentsforce_community.graphs.hugegraph",
    "KuzuGraph": "aiagentsforce_community.graphs.kuzu_graph",
    "MemgraphGraph": "aiagentsforce_community.graphs.memgraph_graph",
    "NebulaGraph": "aiagentsforce_community.graphs.nebula_graph",
    "Neo4jGraph": "aiagentsforce_community.graphs.neo4j_graph",
    "BaseNeptuneGraph": "aiagentsforce_community.graphs.neptune_graph",
    "NeptuneAnalyticsGraph": "aiagentsforce_community.graphs.neptune_graph",
    "NeptuneGraph": "aiagentsforce_community.graphs.neptune_graph",
    "NeptuneRdfGraph": "aiagentsforce_community.graphs.neptune_rdf_graph",
    "NetworkxEntityGraph": "aiagentsforce_community.graphs.networkx_graph",
    "OntotextGraphDBGraph": "aiagentsforce_community.graphs.ontotext_graphdb_graph",
    "RdfGraph": "aiagentsforce_community.graphs.rdf_graph",
    "TigerGraph": "aiagentsforce_community.graphs.tigergraph_graph",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
