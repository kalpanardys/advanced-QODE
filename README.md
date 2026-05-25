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
   python build_diagrams.py --mode people
   python build_diagrams.py --mode technology
   python build_diagrams.py --mode process
   ```

5. Use a different data file:
   ```bash
   python build_diagrams.py --data-file=my_data.xlsm
   ```

6. Run query-driven analysis and export the result:
   ```bash
   python build_diagrams.py --mode analyze --query "Show me the Confluence tool path" --output-file report.docx
   python build_diagrams.py --query "Show me the Business role path" --output-file report.pdf --export-format pdf
   ```

7. Include a human-friendly narrative summary (LLM-style) in the export:
   ```bash
   python build_diagrams.py --mode analyze --query "Show me the Jira tool flow" --output-file result.txt --narrative
   ```

8. Show aggregated token usage from saved history:
   ```bash
   python build_diagrams.py --show-token-dashboard
   ```

7. View saved query history:
   ```bash
   python build_diagrams.py --show-history
   ```

## Output

The scripts generate Graphviz DOT files that can be visualized at https://dreampuf.github.io/GraphvizOnline/

- `Diagram_People_New` - Role-based dependency diagram
- `Diagram_Network_New` - Process network with critical paths
- `Diagram_Technology_New` - Tool-based dependency diagram
