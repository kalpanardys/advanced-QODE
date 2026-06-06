# Pillar Graph Implementation Roadmap

## Based on Comprehensive Workbook Analysis

**Status**: Analysis Complete ✅  
**Confidence Level**: 85-95% for core pillars  
**Recommendation**: Proceed with Phase 1 immediately

---

## Executive Summary

Pillars **ARE** reliably represented in the workbook through:
1. **Score columns** (FxW=Function, GxW=Governance) → Objective weights
2. **Tables_PAQ** → Business impact definitions per pillar
3. **Tables_Cat row 9** → Pillar metric categories
4. **Q_Stories text** → Pillar references in Story/Output fields

---

## Phase 1: Score Column Implementation (IMMEDIATE - AQ-402)

### What to Build
```
Pillar Nodes: Function, Governance (from score columns)
Edges: Process → Role → Tool (weighted by FxW/GxW)
Confidence: 95%
Coverage: 2 pillars, ~90% workflow coverage
```

### Implementation Steps

1. **Update `graph_builder.py`**
   ```python
   def build_pillar_graph_from_scores(df):
       """
       Create pillar nodes from FxW/GxW columns
       - FxW > 0 → Function pillar
       - GxW > 0 → Governance pillar
       """
       graph = nx.DiGraph()
       
       # Add pillar nodes
       graph.add_node('Function', type='pillar')
       graph.add_node('Governance', type='pillar')
       
       # For each workflow row with non-zero scores
       for idx, row in df.iterrows():
           process = row['Story']
           
           if row['FxW'] > 0:
               # Function → Process
               graph.add_edge('Function', process, weight=row['FxW'])
           
           if row['GxW'] > 0:
               # Governance → Process
               graph.add_edge('Governance', process, weight=row['GxW'])
       
       return graph
   ```

2. **Update `query_processor_enhanced.py`**
   - When pillar = "Function" or "Governance", use score column directly
   - Add validation: If FxW/GxW column not found, return error

3. **Update `demo_enhanced_retrieval.py`**
   - Show edge weights from score columns in traversal output
   - Example: "Function (20.82) → SRS (15) → Architect"

### Validation
```
Expected: Pillar nodes appear in graph validation
Expected: 59 processes connected to Function
Expected: 54 processes connected to Governance
Test: test_pillar_graph_from_scores (new)
```

---

## Phase 2: Text-Based Heuristics (Follow-up - AQ-403)

### Mapping Rules

**Quality Pillar** (80% confidence)
- Q_Stories columns: "Story", "Output", "Primary metrics captured"
- Keywords: "quality", "test", "validation", "integrity"
- Rule: IF Story contains ANY keyword → Quality pillar

**Security Pillar** (80% confidence)
- Keywords: "security", "vulnerability", "scan", "compliance", "encryption"
- Rule: IF Story contains ANY keyword → Security pillar

**Reliability Pillar** (70% confidence)
- Keywords: "reliability", "failure", "resilience", "availability", "downtime"
- Rule: IF Story contains ANY keyword → Reliability pillar

**Compliance Pillar** (60% confidence)
- Keywords: "compliance", "audit", "SLA", "regulation", "policy"
- Rule: IF Story contains ANY keyword → Compliance pillar

**Performance Pillar** (70% confidence)
- Keywords: "performance", "NFR", "load", "latency", "throughput"
- Rule: IF Story contains ANY keyword → Performance pillar

### Implementation
```python
def build_pillar_graph_from_text(df):
    """Map pillars via text heuristics and fuzzy matching"""
    graph = nx.DiGraph()
    
    pillar_keywords = {
        'Quality': ['quality', 'test', 'validation', 'integrity'],
        'Security': ['security', 'vulnerability', 'scan', 'encryption'],
        'Reliability': ['reliability', 'failure', 'resilience', 'availability'],
        'Compliance': ['compliance', 'audit', 'sla', 'regulation'],
        'Performance': ['performance', 'nfr', 'load', 'latency'],
    }
    
    for idx, row in df.iterrows():
        story_text = str(row['Story']).lower()
        
        for pillar, keywords in pillar_keywords.items():
            if any(kw in story_text for kw in keywords):
                graph.add_node(pillar, type='pillar')
                graph.add_edge(pillar, row['Story'])
    
    return graph
```

---

## Phase 3: Long-term Improvements

### Extend Workbook
- Add columns: RxW, CxW, PxW (Risk, Compliance, Performance weights)
- Add column: "Explicit Pillar" assignment per row
- Revisit Cost pillar (currently absent)

### Enhanced Mapping
- Map Practice type → Tables_PAQ assessment categories
- Create lookup table: Practice type → Primary pillar
- Add confidence scores per mapping

---

## Current Blockers & Solutions

### Issue: Only 2 Pillars Covered in Scores
- **Blocker**: FxW/GxW only cover Function and Governance
- **Solution Phase 1**: Accept this limitation; document clearly
- **Solution Phase 2**: Add text heuristics for remaining pillars
- **Solution Phase 3**: Request workbook extension

### Issue: Cost Pillar Missing
- **Status**: Not mentioned anywhere in workbook
- **Action**: Skip for now; escalate to business stakeholder
- **Note**: May be tracked in separate systems

### Issue: Risk Pillar Minimally Represented
- **Status**: Only 1 mention in Tables_PAQ
- **Confidence**: 40% (very low)
- **Action**: Include text heuristic, but flag confidence as LOW

---

## Testing Strategy

### Unit Tests
```python
test_build_pillar_graph_from_scores()
    # Verify: Function and Governance nodes created
    # Verify: 59 processes connected to Function
    # Verify: 54 processes connected to Governance
    # Verify: Edge weights = FxW/GxW values

test_pillar_resolution_with_scores()
    # Query: "Show Function dependencies"
    # Expected: Returns path starting from Function node

test_pillar_fuzzy_matching_with_scores()
    # Query: "What does governance impact?"
    # Expected: Resolves to Governance pillar (fuzzy match)
```

### Integration Tests
```python
test_demo_enhanced_retrieval_with_score_pillars()
    # Run demo with Function/Governance queries
    # Expected: All sections execute without error
    # Expected: Confidence scores shown in output
```

---

## Files to Modify

### Priority 1 (Phase 1)
- ✅ `graph_builder.py` - Add build_pillar_graph_from_scores()
- ✅ `query_processor_enhanced.py` - Validate pillar in score columns
- ✅ `demo_enhanced_retrieval.py` - Show score-based edge weights
- ✅ `test_enhanced_features.py` - Add score column tests

### Priority 2 (Phase 2)
- `graph_builder.py` - Add build_pillar_graph_from_text()
- `entity_resolver.py` - Add text-to-pillar confidence scoring
- New file: `pillar_mapper.py` - Text mapping rules and logic

### Priority 3 (Phase 3)
- Workbook schema extension
- Business stakeholder engagement

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Only 2/9 pillars from scores | HIGH | MEDIUM | Phase 2 text heuristics; document as "Phase 1 MVP" |
| Cost pillar unmapped | HIGH | LOW | Skip for now; escalate separately |
| Risk pillar low confidence | MEDIUM | LOW | Flag in output; user can override |
| Text heuristics produce false positives | MEDIUM | MEDIUM | Add confidence thresholds; manual review option |

---

## Success Criteria

✅ Phase 1 Complete when:
- [ ] Function pillar resolved with 95% queries
- [ ] Governance pillar resolved with 95% queries
- [ ] Edge weights visible in traversal output
- [ ] All tests pass (40+ tests)
- [ ] Demo executes without errors

---

## Timeline Estimate

- **Phase 1**: 2-4 hours (score column integration + testing)
- **Phase 2**: 4-6 hours (text heuristics + mapping rules)
- **Phase 3**: 8+ hours (workbook extension + business alignment)

---

## References

- 📄 [COMPREHENSIVE_PILLAR_ANALYSIS.txt](./COMPREHENSIVE_PILLAR_ANALYSIS.txt) - Full evidence report
- 📄 [PILLAR_MAPPING_ANALYSIS.txt](./PILLAR_MAPPING_ANALYSIS.txt) - Initial findings
- 📊 [sample_questions.xlsm](./sample_questions.xlsm) - Source data

