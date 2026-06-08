from graph_builder import GraphBuilder
from hybrid_retriever import HybridRetriever
from llm_client import LLMClient

builder = GraphBuilder()

builder.build_role_graph()
builder.build_tool_graph()
builder.build_process_graph()
builder.build_pillar_graph()

graph = builder.build_unified_graph()

retriever = HybridRetriever(graph)

query = "What is impacted if Jira fails?"

results = retriever.retrieve(
    query,
    "Jira"
)

llm = LLMClient()

answer = llm.ask(
    query=query,
    graph_data=results["graph"],
    vector_data=results["vector"]
)

print("\nLLM RESPONSE\n")
print(answer)