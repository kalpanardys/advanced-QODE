# 🧩 Advanced QODE

Advanced QODE is an AI-assisted knowledge graph and retrieval system for exploring enterprise workflow relationships such as people, tools, roles, processes, and pillars. It combines graph-based reasoning with semantic retrieval and LLM-generated answers to help users analyze questions like “what if Jira fails?”

---

## 🚀 Overview

The project builds a structured knowledge graph from workflow data and then answers natural-language questions using:

- Graph-based evidence extraction
- Semantic vector retrieval
- LLM response generation
- Report export to Word and PowerPoint

The main workflow is demonstrated in [test_llm_rag.py](test_llm_rag.py).

---

## ✨ Key Features

- Builds role, tool, process, and pillar graphs
- Creates a unified dependency graph
- Retrieves relevant evidence from both graph and semantic layers
- Generates human-readable answers through an LLM
- Exports analysis results as Word and PowerPoint reports

---

## 🧠 How It Works

1. The system loads structured data from the Excel-based input source.
2. Graph builders create different relationship views.
3. A hybrid retriever combines graph reasoning with semantic matching.
4. The LLM receives the evidence and generates an answer.
5. The result is exported into report files.

---

## ⚙️ Setup

### 1. Create a virtual environment

Windows:

```powershell
python -m venv dqode_env
.\dqode_env\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv dqode_env
source dqode_env/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the LLM RAG Example

Run the main example script:

```bash
python test_llm_rag.py
```

When prompted, enter a question such as:

```text
what if jira fails?
```

The script will:

- detect the relevant entity
- print graph-based evidence
- print semantic evidence
- generate an LLM response
- create Word and PowerPoint reports

---

## 📤 Output Files

After running the script, the following files are generated:

- DQODE_Analysis.docx
- DQODE_Analysis.pptx

---

## 📁 Project Structure

```text
.
├── test_llm_rag.py              # Main LLM + graph + retrieval workflow
├── graph_builder.py             # Builds graph structures
├── hybrid_retriever.py          # Combines graph and semantic retrieval
├── llm_client.py                # LLM interface
├── query_processor_enhanced.py  # Entity and query processing
├── export_report.py             # Report export logic
├── requirements.txt             # Python dependencies
└── sample_questions.xlsm        # Input workbook used by the workflow
```

---

## 📦 Dependencies

The project uses libraries such as:

- pandas
- openpyxl
- networkx
- sentence-transformers or compatible embedding support
- PyPDF or related document-processing libraries if used by the workflow
- python-pptx and python-docx for report export

---

## 💡 Notes

- The example script is intended for demonstration and analysis workflows.
- The output may include warnings from Excel parsing libraries when reading the workbook.
- The quality of results depends on the available data and the configured LLM/embedding setup.

---

## 👨‍💻 Author

Kalpana Reddy
