"""
Enhanced demo script using real Excel data and built graphs.
"""

from entity_loader import EntityLoader
from graph_builder import GraphBuilder
from query_processor_enhanced import EnhancedQueryProcessor
from graph_retriever import GraphRetriever
from fallback_retriever import FallbackRetriever
from response_formatter import ResponseFormatter
from impact_analyzer import analyze_impact
from bottleneck_detector import detect_bottlenecks
from graph_reasoner import rank_paths, generate_reasoning
from entity_resolver import resolve_entity, validate_graph
from export_manager import export_to_word, export_to_ppt

def process_query(query, processor, retriever, fallback, formatter):
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

    # Resolver debug: resolve each extracted entity to graph nodes
    graph = retriever.graph
    pillar_res = resolve_entity(graph, "pillar", entities.get("pillar"))
    role_res = resolve_entity(graph, "role", entities.get("role"))
    tool_res = resolve_entity(graph, "tool", entities.get("tool"))
    process_res = resolve_entity(graph, "process", entities.get("process"))

    print("[1.a] RESOLVER DEBUG")
    for etype, original, res in [
        ("Pillar", entities.get("pillar"), pillar_res),
        ("Role", entities.get("role"), role_res),
        ("Tool", entities.get("tool"), tool_res),
        ("Process", entities.get("process"), process_res),
    ]:
        print(f"    Extracted: {original} -> Resolved: {res.get('resolved')} (score={res.get('score')}) type={res.get('node_type')}")
    print()

    # 2. Determine starting entity for graph traversal
    print("[2] SELECTING START ENTITY FOR GRAPH TRAVERSAL")
    # If pillar was provided, traversal must start from pillar node
    pillar = entities.get("pillar")
    start_entity = None
    if pillar:
        if pillar_res.get("resolved"):
            start_entity = pillar_res.get("resolved")
        else:
            print(f"    Pillar '{pillar}' extracted but no matching pillar node found in graph.")
            print("    No matching graph entity found.")
            return {"summary": "No matching graph entity found."}
    else:
        # fallback priority: process -> role -> tool
        if process_res.get("resolved"):
            start_entity = process_res.get("resolved")
        elif role_res.get("resolved"):
            start_entity = role_res.get("resolved")
        elif tool_res.get("resolved"):
            start_entity = tool_res.get("resolved")

    print(f"    Start entity: {start_entity}")
    print(f"    Pillar:       {pillar}\n")

    # 3. Retrieve from graph (ranked paths)
    print("[3] GRAPH TRAVERSAL")
    graph = retriever.graph
    if not start_entity:
        print("    No resolved start entity; aborting traversal.")
        print("    No matching graph entity found.")
        return {"summary": "No matching graph entity found."}

    if start_entity and start_entity in graph:
        retrieval_result = retriever.get_top_paths(start_entity=start_entity, depth=4, top_paths=5)
        print(f"    Status: Found {len(retrieval_result['related_nodes'])} related nodes")
        print(f"    Total discovered paths: {retrieval_result['metadata'].get('path_count',0)}")
        print(f"    Returned top paths: {len(retrieval_result['paths'])}\n")
    elif pillar:
        retrieval_result = retriever.get_top_paths(pillar=pillar, depth=4, top_paths=5)
        if retrieval_result.get("start_entity"):
            print(f"    Resolved pillar to start entity: {retrieval_result['start_entity']}")
            print(f"    Returned top paths: {len(retrieval_result['paths'])}\n")
        else:
            print(f"    Could not resolve pillar '{pillar}', using fallback\n")
            retrieval_result = fallback.get_fallback(query, [entities.get("process")])
    else:
        print(f"    Status: '{start_entity or pillar}' not resolvable in graph, using fallback\n")
        retrieval_result = fallback.get_fallback(query, [entities.get("process")])

    # 4. Format response
    print("[4] EXECUTIVE SUMMARY")
    response = formatter.format(retrieval_result)

    print(f"    Summary:")
    print(f"      {response['summary']}\n")

    # Show top dependency paths
    print("[5] IMPACTED ENTITIES")

    impacted_nodes = set()

    for p in retrieval_result.get("paths", []):
      path = p.get("path") if isinstance(p, dict) else p

      for node in path[1:]:
        impacted_nodes.add(node)

    for node in sorted(impacted_nodes):
        print(f"    - {node}")

    print()

    # Impact analysis
    print("[6] IMPACT ANALYSIS")
    try:
        impact = analyze_impact(graph, retrieval_result.get("start_entity"), max_depth=4, top_paths=5)
        for level in ["high", "medium", "low"]:
            items = impact.get("impact", {}).get(level, [])
            if items:
                print(f"    {level.title()} Impact:")
                for node, cnt in items:
                    print(f"      - {node} (in {cnt} path(s))")
        print()
    except Exception as e:
        print(f"    Impact analysis failed: {e}\n")

    # Critical Dependencies
    print("[7] KEY DEPENDENCIES")
    try:
      paths_for_bottleneck = [p.get("path") for p in retrieval_result.get("paths", [])]
      bn = detect_bottlenecks(graph, paths=paths_for_bottleneck, top_n=5)

      for b in bn.get("bottlenecks", []):
        print(f"    - {b['node']}")

      print()
    except Exception as e:
      print(f"    Dependency analysis failed: {e}\n")

    # Graph reasoning / recommendations
    print("[8] GRAPH REASONING")
    try:
        reasoning = retrieval_result.get("reasoning") or generate_reasoning(graph, retrieval_result.get("start_entity"), retrieval_result.get("paths", []))
        print(f"    {reasoning}\n")
    except Exception as e:
        print(f"    Graph reasoning failed: {e}\n")

    print("[9] RECOMMENDATIONS")
    # Use formatter recommendations + simple graph-driven recommendations
    for rec in response.get("recommendations", []):
        print(f"      • {rec}")
    print()

    response["impacted_entities"] = sorted(list(impacted_nodes))
 
    export_to_word(
      query=query,
      result=response,
      filename="impact_report.docx"
    )

    export_to_ppt(
      query=query,
      result=response,
      filename="impact_report.pptx"
    )

    return response


def main():
    """Main enhanced demo using real Excel data."""
    print("\n" + "=" * 70)
    print("AGENTIC AI PROCESS INTELLIGENCE PLATFORM - ENHANCED RETRIEVAL DEMO")
    print("=" * 70)

    # Initialize components with real Excel data
    print("\n[SETUP] Loading entities from Excel file...")
    try:
        loader = EntityLoader("sample_questions.xlsm")
        summary = loader.get_entity_summary()
        print(f"  ✓ Pillars:   {summary['pillar_count']}")
        print(f"  ✓ Roles:     {summary['role_count']}")
        print(f"  ✓ Tools:     {summary['tool_count']}")
        print(f"  ✓ Processes: {summary['process_count']}")
        print(f"  ✓ Total:     {summary['total_entities']} entities\n")
    except Exception as e:
        print(f"  ✗ Error loading entities: {e}\n")
        return

    print("[SETUP] Building dependency graphs from Excel data...")
    try:
        builder = GraphBuilder("sample_questions.xlsm")
        role_graph = builder.build_role_graph()
        tool_graph = builder.build_tool_graph()
        process_graph = builder.build_process_graph()
        unified_graph = builder.build_unified_graph()

        graph_summary = builder.get_graph_summary()
        print(f"  ✓ Role Graph:    {graph_summary['role_graph']['nodes']} nodes, {graph_summary['role_graph']['edges']} edges")
        print(f"  ✓ Tool Graph:    {graph_summary['tool_graph']['nodes']} nodes, {graph_summary['tool_graph']['edges']} edges")
        print(f"  ✓ Process Graph: {graph_summary['process_graph']['nodes']} nodes, {graph_summary['process_graph']['edges']} edges")
        print(f"  ✓ Unified Graph: {len(unified_graph.nodes())} nodes, {len(unified_graph.edges())} edges\n")
        # Validate graph construction and list nodes by type
        vinfo = validate_graph(unified_graph, known_pillars=loader.get_all_entities().get("pillars", []))
        print("[GRAPH VALIDATION]")
        print(f"  Total Nodes: {vinfo['total_nodes']}")
        print(f"  Total Edges: {vinfo['total_edges']}")
        print(f"  Pillar Nodes: {vinfo['pillars']}")
        print(f"  Role Nodes: {vinfo['roles'][:10]}")
        print(f"  Tool Nodes: {vinfo['tools'][:10]}")
        print(f"  Process Nodes: {vinfo['processes'][:10]}\n")
    except Exception as e:
        print(f"  ✗ Error building graphs: {e}\n")
        return

    print("[SETUP] Initializing retrieval components...")
    try:
        processor = EnhancedQueryProcessor("sample_questions.xlsm")
        retriever = GraphRetriever(unified_graph)
        fallback = FallbackRetriever()
        formatter = ResponseFormatter()
        print("[SETUP] Ready!\n")
    except Exception as e:
        print(f"  ✗ Error initializing retrieval: {e}\n")
        return

    # Display available entities
    print("Available entities in the graph:")
    entities = loader.get_all_entities()
    for entity_type, entity_list in entities.items():
        print(f"  [{entity_type.upper()}]: {', '.join(sorted(entity_list)[:5])}")
        if len(entity_list) > 5:
            print(f"    ... and {len(entity_list) - 5} more")

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
            process_query(query, processor, retriever, fallback, formatter)

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
