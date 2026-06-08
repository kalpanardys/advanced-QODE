import chromadb

print("A")

client = chromadb.PersistentClient(path="./chromadb_test")

print("B")

collection = client.get_or_create_collection(
    name="test_collection",
    embedding_function=None
)

print("C")

try:
    collection.add(
        ids=["1"],
        documents=["hello world"],
        embeddings=[[0.1] * 768]
    )

    print("D")

except BaseException as e:
    print("ERROR")
    print(type(e))
    print(e)

print("E")