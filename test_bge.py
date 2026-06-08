from sentence_transformers import SentenceTransformer

print("Loading model...")

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

embedding = model.encode("What is impacted if Jira fails?")

print("Embedding generated")
print(f"Vector length = {len(embedding)}")