"""
Demo script for the retrieval layer.
Takes user queries and returns dependencies.
"""

import networkx as nx
from query_processor import QueryProcessor
from graph_retriever import GraphRetriever
from fallback_retriever import FallbackRetriever
from response_formatter import ResponseFormatter


def create_sample_graph():
    """Create a sample dependency graph for demonstration."""
    G = nx.DiGraph()

    # Add nodes with metadata
    nodes = [
        ("Deployment", {"type": "process"}),
        ("Jenkins", {"type": "tool"}),
        ("DevOps Team", {"type": "role"}),
        ("Security Review", {"type": "process"}),
        ("GitHub", {"type": "tool"}),
        ("QA Engineer", {"type": "role"}),
        ("Testing", {"type": "process"}),
        ("Docker", {"type": "tool"}),
    ]

    for node, attrs in nodes:
        G.add_node(node, **attrs)

    # Add edges with labels
    edges = [
        ("Deployment", "Jenkins", {"label": "uses"}),
        ("Jenkins", "DevOps Team", {"label": "owned_by"}),
        ("DevOps Team", "Security Review", {"label": "reviews"}),
        ("GitHub", "Deployment", {"label": "triggers"}),
        ("Testing", "QA Engineer", {"label": "owned_by"}),
        ("QA Engineer", "Deployment", {"label": "approves"}),
        ("Docker", "Jenkins", {"label": "integrates"}),
    ]

    for src, tgt, attrs in edges:
        G.add_edge(src, tgt, **attrs)

    return G


def process_query(query, graph, processor, retriever, fallback, formatter):
    """Process a single user query and return formatted response."""
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print(f"{'='*70}\n")

    # 1. Extract entities from query
    print("[1] ENTITY EXTRACTION")
    entities = processor.extract_entities(query)
    print(f"    Pillar:   {entities['pillar']}")
    print(f"    Role:     {entities['role']}")
    print(f"    Tool:     {entities['tool']}")
    print(f"    Process:  {entities['process']}")
    print(f"    Intent:   {entities['intent']}\n")

    # 2. Determine starting entity for graph traversal
    print("[2] SELECTING START ENTITY FOR GRAPH TRAVERSAL")
    start_entity = entities["process"] or entities["role"] or entities["tool"]
    print(f"    Start entity: {start_entity}\n")

    # 3. Retrieve from graph
    print("[3] GRAPH TRAVERSAL")
    if start_entity and start_entity in graph:
        retrieval_result = retriever.traverse(start_entity, depth=2)
        print(f"    Status: Found {len(retrieval_result['related_nodes'])} related nodes")
        print(f"    Paths: {len(retrieval_result['paths'])} dependency paths\n")
    else:
        print(f"    Status: '{start_entity}' not in graph, using fallback\n")
        retrieval_result = fallback.get_fallback(query, [entities.get("process")])

    # 4. Format response
    print("[4] FORMATTED RESPONSE")
    response = formatter.format(retrieval_result)

    print(f"    Summary:")
    print(f"      {response['summary']}\n")

    print(f"    Dependencies:")
    for dep in response["dependencies"][:3]:  # Show first 3
        print(f"      • {dep}")
    if len(response["dependencies"]) > 3:
        print(f"      ... and {len(response['dependencies']) - 3} more\n")
    else:
        print()

    print(f"    Risks:")
    for risk in response["risks"]:
        print(f"      • {risk}")
    print()

    print(f"    Recommendations:")
    for rec in response["recommendations"]:
        print(f"      • {rec}")
    print()

    return response


def main():
    """Main demo function with interactive query input."""
    print("\n" + "=" * 70)
    print("AGENTIC AI PROCESS INTELLIGENCE PLATFORM - RETRIEVAL LAYER DEMO")
    print("=" * 70)

    # Initialize components
    print("\n[SETUP] Initializing retrieval components...")
    processor = QueryProcessor()
    graph = create_sample_graph()
    retriever = GraphRetriever(graph)
    fallback = FallbackRetriever()
    formatter = ResponseFormatter()
    print("[SETUP] Ready!\n")

    # Display available entities in the graph
    print("Available entities in the graph:")
    nodes_by_type = {}
    for node, attrs in graph.nodes(data=True):
        node_type = attrs.get("type", "unknown")
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)

    for node_type, nodes in sorted(nodes_by_type.items()):
        print(f"  [{node_type.upper()}]: {', '.join(sorted(nodes))}")

    print("\n" + "=" * 70)
    print("Enter your queries one by one (type 'quit' or 'exit' to end)")
    print("=" * 70 + "\n")

    # Interactive query loop
    query_count = 0
    while True:
        try:
            query = input(f"\n[Query #{query_count + 1}] Enter your query: ").strip()

            # Check for exit commands
            if query.lower() in ["quit", "exit", "q"]:
                print("\n" + "=" * 70)
                print("DEMO ENDED")
                print("=" * 70 + "\n")
                break

            # Skip empty queries
            if not query:
                print("Please enter a valid query.")
                continue

            # Process the query
            query_count += 1
            process_query(query, graph, processor, retriever, fallback, formatter)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("DEMO INTERRUPTED")
            print("=" * 70 + "\n")
            break
        except Exception as e:
            print(f"\nError processing query: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
