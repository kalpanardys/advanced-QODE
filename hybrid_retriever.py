from faiss_store import FAISSStore
from graph_retriever import GraphRetriever


class HybridRetriever:

    def __init__(self, graph):

        self.graph_retriever = GraphRetriever(graph)

        self.vector_store = FAISSStore()

        self.vector_store.build_index()

    def retrieve(self, query, entity):

        graph_results = self.graph_retriever.get_top_paths(
            start_entity=entity,
            depth=4,
            top_paths=5
        )

        vector_results = self.vector_store.search(
            query,
            top_k=5
        )

        return {
            "graph": graph_results,
            "vector": vector_results
        }