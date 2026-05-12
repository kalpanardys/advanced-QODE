# 🧩 DQODE Diagram Generation Tool

A Python-based tool to generate **People**, **Technology**, and **Process Network** diagrams from structured Excel input data using Graphviz.

---

## 🚀 Overview

This project reads workflow data from an Excel file and generates diagram representations in **Graphviz DOT format**.

It supports:

* 👥 People Interaction Diagram
* 🛠️ Technology Interaction Diagram
* 🔄 Process Network Diagram (with critical path analysis)

---

## 🏗️ Architecture

```
Excel Input
   ↓
utils.py (data processing)
   ↓
diagram_generator.py (core logic)
   ↓
main.py (execution control)
   ↓
DOT Files (output)
   ↓
Graphviz (visualization)
```

---

## 📁 Project Structure

```
.
├── main.py                        # Entry point (execution controller)
├── diagram_generator.py          # Core logic (builders + exporter)
├── utils.py                      # Reusable helper functions
├── interfaces.py                 # Abstract base classes (contracts)
├── test_diagram_generation.py    # Unit tests
├── sample_questions.xlsm         # Input file
├── requirements.txt              # Dependencies
├── Diagram_*                     # Output files (generated)
```

---

## 📌 Input File

* File: `sample_questions.xlsm`
* Sheet: `Q_Stories`
* Only rows with `"Yes / No" = Yes` are processed

---

## ⚙️ Setup

### 1. Create virtual environment

```
python -m venv venv
```

### 2. Activate environment

**Windows:**

```
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Usage

### Run all diagrams

```
python main.py
```

---

### Run specific diagram

```
python main.py people
python main.py technology
python main.py process
```

---

## 📤 Output

Generated files:

```
Diagram_People_New
Diagram_Technology_New
Diagram_Network_New
```

These are **Graphviz DOT files**.

---

## 📊 Visualization

To view diagrams:

1. Open: https://dreampuf.github.io/GraphvizOnline/
2. Copy content from output file
3. Paste into the editor
4. View rendered diagram

---

## 🧠 Key Concepts

* **Graph Builders** → Create nodes and edges from data
* **Graph Exporter** → Saves graph in DOT format
* **Utils** → Shared reusable logic
* **Interfaces** → Enforce structure across components
* **Tests** → Validate correctness

---

## 🧪 Running Tests

```
python -m unittest test_diagram_generation.py
```

---

## 📦 Dependencies

* pandas
* networkx
* matplotlib
* pydot
* scikit-image
* openpyxl

---

## 💡 Notes

* Output is text-based (DOT format)
* Can be extended to export PNG/SVG
* Graph objects can also be used in-memory (no file required)

---

## 👨‍💻 Author

Kalpana Reddy

---

## 📌 Future Enhancements

* Direct PNG/SVG export
* API integration
* Interactive UI
* Workflow automation integration

---
