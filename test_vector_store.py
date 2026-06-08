from vector_store import VectorStore

try:

    vs = VectorStore()

    print("Building index...")
    vs.build_index()

    print("Searching...")

    results = vs.search(
        "What is impacted if Jira fails?"
    )

    print("\nSEARCH RESULTS:")
    print(results)

except Exception as e:

    print("\nTEST FAILED")
    print(type(e))
    print(str(e))