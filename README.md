# advanced-QODE
Building Next Level DevSecOps Assessment based on 9 core pillars of SDLC

## Project Structure

### Core Architecture
- `utils.py` - Shared utilities (data loading, NaN checking, predecessor handling)
- `builders.py` - Abstract interfaces for diagram builders and exporters
- `interfaces.py` - Interface definitions
- `diagram_builders.py` - Concrete implementations: PeopleDiagramBuilder, TechnologyDiagramBuilder, ProcessNetworkDiagramBuilder
- `build_diagrams.py` - Command-line runner for selected or all diagrams

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the diagram builders:
   ```bash
   python build_diagrams.py
   ```

4. Run only a specific diagram:
   ```bash
   python build_diagrams.py --people
   python build_diagrams.py --technology
   python build_diagrams.py --network
   ```

5. Use a different data file:
   ```bash
   python build_diagrams.py --data-file=my_data.xlsm
   ```

## Output

The scripts generate Graphviz DOT files that can be visualized at https://dreampuf.github.io/GraphvizOnline/

- `Diagram_People_New` - Role-based dependency diagram
- `Diagram_Network_New` - Process network with critical paths
- `Diagram_Technology_New` - Tool-based dependency diagram
