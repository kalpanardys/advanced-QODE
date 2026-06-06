import networkx as nx
from fuzzy_matcher import best_match
from graph_retriever import GraphRetriever
from impact_analyzer import analyze_impact
from bottleneck_detector import detect_bottlenecks
from graph_reasoner import rank_paths


def create_test_graph():
    G = nx.DiGraph()
    edges = [
        ("Jira", "Confluence"),
        ("Confluence", "Requirements"),
        ("Requirements", "Development"),
        ("Jira", "Defect Management"),
        ("Defect Management", "Testing"),
        ("Testing", "Deployment"),
        ("GitHub", "Deployment"),
    ]
    for src, tgt in edges:
        G.add_node(src)
        G.add_node(tgt)
        G.add_edge(src, tgt)
    return G


def test_fuzzy_matcher():
    candidates = ["GitHub", "GitLab", "Jira"]
    assert best_match("Github", candidates, threshold=70)[0] == "GitHub"
    assert best_match("gitlab", candidates, threshold=70)[0] == "GitLab"


def test_pillar_traversal_and_paths():
    G = create_test_graph()
    retriever = GraphRetriever(G)
    res = retriever.get_top_paths(start_entity="Jira", depth=4, top_paths=3)
    assert res["start_entity"] == "Jira"
    assert res["paths"]


def test_impact_analysis_and_bottlenecks():
    G = create_test_graph()
    impact = analyze_impact(G, "Jira", max_depth=4, top_paths=5)
    assert "paths" in impact
    bn = detect_bottlenecks(G, paths=impact.get("paths", []), top_n=3)
    assert "bottlenecks" in bn


def test_path_ranking():
    G = create_test_graph()
    paths = []
    for t in ["Development", "Deployment"]:
        for p in nx.all_simple_paths(G, source="Jira", target=t, cutoff=5):
            paths.append(p)
    ranked = rank_paths(G, paths, top_n=3)
    assert isinstance(ranked, list)
