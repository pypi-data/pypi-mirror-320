import logging
from typing import Any, Dict, List, Literal, Optional, Set, Tuple
from pathlib import Path
import pandas as pd

from tigergraphx.config import (
    TigerGraphConnectionConfig,
    GraphSchema,
    LoadingJobConfig,
    NodeSpec,
    NeighborSpec,
)

from tigergraphx.core.graph_context import GraphContext
from tigergraphx.core.managers import (
    SchemaManager,
    DataManager,
    NodeManager,
    EdgeManager,
    QueryManager,
    StatisticsManager,
    VectorManager,
)

logger = logging.getLogger(__name__)


class BaseGraph:
    def __init__(
        self,
        graph_schema: GraphSchema | Dict | str | Path,
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
        drop_existing_graph: bool = False,
    ):
        # Initialize the graph context with the provided schema and connection config
        self._context = GraphContext(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
        )

        # Extract graph name, node types, and edge types from the graph schema
        self.name = self._context.graph_schema.graph_name
        self.node_types = set(self._context.graph_schema.nodes.keys())
        self.edge_types = set(self._context.graph_schema.edges.keys())

        # If there's only one node or edge type, set it as a default type
        self.node_type = (
            next(iter(self.node_types)) if len(self.node_types) == 1 else ""
        )
        self.edge_type = (
            next(iter(self.edge_types)) if len(self.edge_types) == 1 else ""
        )

        # Initialize managers for handling different aspects of the graph
        self._schema_manager = SchemaManager(self._context)
        self._data_manager = DataManager(self._context)
        self._node_manager = NodeManager(self._context)
        self._edge_manager = EdgeManager(self._context)
        self._statistics_manager = StatisticsManager(self._context)
        self._query_manager = QueryManager(self._context)
        self._vector_manager = VectorManager(self._context)

        # Create the schema, drop the graph first if drop_existing_graph is True
        logger.info(f"Creating schema for graph {self.name}...")
        self._schema_manager.create_schema(drop_existing_graph=drop_existing_graph)
        logger.info("Schema created successfully.")

    @classmethod
    def from_db(
        cls,
        graph_name: str,
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
    ):
        """
        Retrieve an existing graph schema from TigerGraph and initialize a BaseGraph.
        """
        # Retrieve schema using SchemaManager
        graph_schema = SchemaManager.get_schema_from_db(
            graph_name, tigergraph_connection_config
        )

        # Initialize the graph with the retrieved schema
        return cls(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
        )

    @property
    def nodes(self):
        """Return a NodeView instance."""
        from tigergraphx.core.view.node_view import NodeView

        return NodeView(self)

    # ------------------------------ Schema Operations ------------------------------
    def get_schema(self, format: Literal["json", "dict"] = "dict") -> str | Dict:
        return self._schema_manager.get_schema(format)

    def create_schema(self, drop_existing_graph=False) -> bool:
        return self._schema_manager.create_schema(drop_existing_graph)

    def drop_graph(self) -> None:
        return self._schema_manager.drop_graph()

    # ------------------------------ Data Loading Operations ------------------------------
    def load_data(self, loading_job_config: LoadingJobConfig | Dict | str | Path):
        return self._data_manager.load_data(loading_job_config)

    # ------------------------------ Node Operations ------------------------------
    def _add_node(self, node_id: str, node_type: str, **attr):
        return self._node_manager.add_node(node_id, node_type, **attr)

    def _add_nodes_from(
        self,
        nodes_for_adding: List[str] | List[Tuple[str, Dict[str, Any]]],
        node_type: str,
        **attr,
    ):
        return self._node_manager.add_nodes_from(nodes_for_adding, node_type, **attr)

    def _remove_node(self, node_id: str, node_type: str) -> bool:
        return self._node_manager.remove_node(node_id, node_type)

    def _has_node(self, node_id: str, node_type: str) -> bool:
        return self._node_manager.has_node(node_id, node_type)

    def _get_node_data(self, node_id: str, node_type: str) -> Dict | None:
        return self._node_manager.get_node_data(node_id, node_type)

    def _get_node_edges(
        self,
        node_id: str,
        node_type: str,
        edge_types: List | str,
    ) -> List:
        return self._node_manager.get_node_edges(node_id, node_type, edge_types)

    def clear(self) -> bool:
        return self._node_manager.clear()

    # ------------------------------ Edge Operations ------------------------------
    def _add_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        return self._edge_manager.add_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type, **attr
        )

    def _add_edges_from(
        self,
        ebunch_to_add: List[Tuple[str, str]] | List[Tuple[str, str, Dict[str, Any]]],
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        return self._edge_manager.add_edges_from(
            ebunch_to_add, src_node_type, edge_type, tgt_node_type, **attr
        )

    def _has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> bool:
        return self._edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

    def _get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Dict | None:
        return self._edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

    # ------------------------------ Statistics Operations ------------------------------
    def _degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        return self._statistics_manager.degree(node_id, node_type, edge_types)

    # ------------------------------ Statistics Operations ------------------------------
    def _number_of_nodes(self, node_type: Optional[str | list] = None) -> int:
        """Return the number of nodes for the given node type(s)."""
        return self._statistics_manager.number_of_nodes(node_type)

    def _number_of_edges(self, edge_type: Optional[str] = None) -> int:
        """Return the number of edges for the given edge type(s)."""
        return self._statistics_manager.number_of_edges(edge_type)

    # ------------------------------ Query Operations ------------------------------
    def run_query(self, query_name: str, params: Dict = {}):
        return self._query_manager.run_query(query_name, params)

    def _get_nodes(
        self,
        node_type: str = "",
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._query_manager.get_nodes(
            node_type, filter_expression, return_attributes, limit
        )

    def _get_nodes_from_spec(self, spec: NodeSpec) -> pd.DataFrame | None:
        return self._query_manager.get_nodes_from_spec(spec)

    def _get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._query_manager.get_neighbors(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    def _get_neighbors_from_spec(self, spec: NeighborSpec) -> pd.DataFrame | None:
        return self._query_manager.get_neighbors_from_spec(spec)

    # ------------------------------ Vector Operations ------------------------------
    def _upsert(
        self,
        data: Dict | List[Dict],
        node_type: str,
    ):
        return self._vector_manager.upsert(data, node_type)

    def _fetch_node(
        self, node_id: str, vector_attribute_name: str, node_type: str
    ) -> Optional[List[float]]:
        return self._vector_manager.fetch_node(
            node_id, vector_attribute_name, node_type
        )

    def _fetch_nodes(
        self, node_ids: List[str], vector_attribute_name: str, node_type: str
    ) -> Dict[str, List[float]]:
        return self._vector_manager.fetch_nodes(
            node_ids, vector_attribute_name, node_type
        )

    def _search(
        self,
        data: List[float],
        vector_attribute_name: str,
        node_type: str,
        limit: int = 10,
        return_attributes: Optional[str | List[str]] = None,
        candidate_ids: Optional[Set[str]] = None,
    ) -> List[Dict]:
        return self._vector_manager.search(
            data=data,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
            candidate_ids=candidate_ids,
        )

    def _search_multi_vector_attributes(
        self,
        data: List[float],
        vector_attribute_names: List[str],
        node_types: List[str],
        limit: int = 10,
        return_attributes_list: Optional[List[List[str]]] = None,
    ) -> List[Dict]:
        return self._vector_manager.search_multi_vector_attributes(
            data=data,
            vector_attribute_names=vector_attribute_names,
            node_types=node_types,
            limit=limit,
            return_attributes_list=return_attributes_list,
        )

    def _search_top_k_similar_nodes(
        self,
        node_id: str,
        vector_attribute_name: str,
        node_type: str = "",
        limit: int = 5,
        return_attributes: Optional[List[str]] = None,
    ) -> List[Dict]:
        return self._vector_manager.search_top_k_similar_nodes(
            node_id=node_id,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
        )
