from faiss_store import FAISSStore

store = FAISSStore()

store.build_index()

results = store.search(
    "What is impacted if Jira fails?"
)

print("\nRESULTS:\n")

for r in results:
    print(r)
    print("-" * 50)