from graph_builder import GraphBuilder
from hybrid_retriever import HybridRetriever
from llm_client import LLMClient
from query_processor_enhanced import EnhancedQueryProcessor
from export_report import ReportExporter

builder = GraphBuilder()

builder.build_role_graph()
builder.build_tool_graph()
builder.build_process_graph()
builder.build_pillar_graph()

graph = builder.build_unified_graph()

retriever = HybridRetriever(graph)

processor = EnhancedQueryProcessor()

query = input("\nEnter your question: ")

entities = processor.extract_entities(query)

entity = (
    entities.get("tool")
    or entities.get("role")
    or entities.get("process")
    or entities.get("pillar")
)

print("\nDetected Entity:", entity)

if not entity:
    print("\nCould not identify an entity from the question.")
    exit()

results = retriever.retrieve(
    query,
    entity
)

llm = LLMClient()
print("\n" + "=" * 60)
print("GRAPH EVIDENCE")
print("=" * 60)

graph_reasoning = results["graph"].get(
    "reasoning",
    "No graph reasoning available."
)

print(graph_reasoning)
print("\nTOP GRAPH PATHS")

for p in results["graph"]["paths"][:3]:
    print(" -> ".join(p["path"]))

print("\n" + "=" * 60)
print("SEMANTIC EVIDENCE")
print("=" * 60)

for item in results["vector"]:
    print(item)
answer = llm.ask(
    query=query,
    graph_data=results["graph"].get(
      "reasoning",
     "No graph reasoning available."
    ),
    vector_data=results["vector"]
)

print("\nLLM RESPONSE\n")
print(answer)
ReportExporter.export_word(
    query=query,
    entity=entity,
    graph_evidence=results["graph"].get(
     "reasoning",
     "No graph reasoning available."
    ),
    semantic_evidence=results["vector"],
    llm_response=answer
)

ReportExporter.export_ppt(
    query=query,
    entity=entity,
    graph_evidence=results["graph"].get(
    "reasoning",
    "No graph reasoning available."
    ),  
    semantic_evidence=results["vector"],
    llm_response=answer
)