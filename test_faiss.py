import faiss
import numpy as np

print("Creating vectors...")

vectors = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [7.0, 8.0, 9.0]
], dtype="float32")

print("Creating index...")

index = faiss.IndexFlatL2(3)

index.add(vectors)

print("Total vectors:", index.ntotal)

query = np.array([[1.0, 2.0, 3.0]], dtype="float32")

distances, indices = index.search(query, 2)

print("Indices:", indices)
print("Distances:", distances)  