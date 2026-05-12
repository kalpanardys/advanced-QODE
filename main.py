#!/usr/bin/env python3
"""
Example usage of the new diagram builders.
"""

from diagram_generator import PeopleDiagramBuilder, TechnologyDiagramBuilder, ProcessNetworkDiagramBuilder
import sys

def main():
    mode = "all"

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    print("=" * 60)
    print("QODE Diagram Builders")
    print("=" * 60)
    
    valid_modes = ["all", "people", "technology", "process"]
    if mode not in valid_modes:
     print("Invalid option. Use: all / people / technology / process")
     return
    #people diagram
    if mode in ["all", "people"]:
    
     print("\n1. Building People Diagram...")
     try:
        people_builder = PeopleDiagramBuilder()
        df = people_builder.load_data('sample_questions.xlsm')
        people_graph = people_builder.build_graph(df)
        people_builder.write_output(people_graph, 'Diagram_People_New')
        print("   ✓ People diagram saved as 'Diagram_People_New'")
     except Exception as e:
        print(f"   ✗ Error: {e}")

    # Technology Diagram
    if mode in ["all", "technology"]:
     print("\n2. Building Technology Diagram...")
     try:
        tech_builder = TechnologyDiagramBuilder()
        df = tech_builder.load_data('sample_questions.xlsm')
        tech_graph = tech_builder.build_graph(df)
        tech_builder.write_output(tech_graph, 'Diagram_Technology_New')
        print("   ✓ Technology diagram saved as 'Diagram_Technology_New'")
     except Exception as e:
        print(f"   ✗ Error: {e}")
    
    #Process Network Diagram
    if mode in ["all", "process"]:
     print("\n3. Building Process Network Diagram...")
     try:
        network_builder = ProcessNetworkDiagramBuilder()
        df = network_builder.load_data('sample_questions.xlsm')
        network_graph = network_builder.build_graph(df)
        
        # Find critical paths
        critical_paths = network_builder.find_critical_paths(df)
        print(f"   ✓ Found {len(critical_paths)} critical path(s)")
        
        network_builder.write_output(network_graph, 'Diagram_Network_New')
        print("   ✓ Process network diagram saved as 'Diagram_Network_New'")
     except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Complete! View results in GraphvizOnline:")
    print("https://dreampuf.github.io/GraphvizOnline/")
    print("=" * 60)

if __name__ == "__main__":
    main()