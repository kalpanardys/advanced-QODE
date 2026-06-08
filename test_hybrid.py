from graph_builder import GraphBuilder
from hybrid_retriever import HybridRetriever

builder = GraphBuilder()

builder.build_role_graph()
builder.build_tool_graph()
builder.build_process_graph()
builder.build_pillar_graph()

graph = builder.build_unified_graph()

retriever = HybridRetriever(graph)

results = retriever.retrieve(
    "What is impacted if Jira fails?",
    "Jira"
)

print("\nVECTOR RESULTS\n")

for r in results["vector"]:
    print(r)
    print("-" * 50)

print("\nGRAPH RESULTS\n")

print(results["graph"])