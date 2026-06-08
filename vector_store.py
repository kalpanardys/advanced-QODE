from sentence_transformers import SentenceTransformer
from utils import load_qode_data
import chromadb


class VectorStore:

    def __init__(self, file_path="sample_questions.xlsm"):

        self.file_path = file_path

        print("Loading BGE model...")
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")

        self.client = chromadb.PersistentClient(path="./chromadb")

        try:
            self.client.delete_collection("qode_knowledge")
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
                name="qode_knowledge",
                embedding_function=None
        )

    def build_index(self):

        print("Loading dataframe...")
        df = load_qode_data(self.file_path)

        print(f"Rows loaded = {len(df)}")

        docs = []
        ids = []

        for idx, row in df.iterrows():

            role = str(row.get("Team / owner role", ""))
            tool = str(row.get("Automation tool", ""))
            input_val = str(row.get("Input", ""))
            output_val = str(row.get("Output", ""))

            text = (
                f"Role: {role}. "
                f"Tool: {tool}. "
                f"Input: {input_val}. "
                f"Output: {output_val}."
            )

            docs.append(text)
            ids.append(f"record_{idx}")

        print(f"Documents created = {len(docs)}")

        if not docs:
            raise Exception("No documents created")

        print("First document:")
        print(docs[0])

        print("Generating embeddings...")
        embeddings = self.model.encode(docs).tolist()

        print("Embeddings generated")

        print(f"IDs count = {len(ids)}")
        print(f"Docs count = {len(docs)}")
        print(f"Embeddings count = {len(embeddings)}")
        print(f"Embedding size = {len(embeddings[0])}")

        print("Adding ONLY 2 records to ChromaDB for testing...")

        try:
            print(type(self.collection))
            self.collection.add(
                ids=ids[:2],
                documents=docs[:2],
                embeddings=embeddings[:2]
            )

            print("Indexed 2 records successfully")

        except Exception as e:

            print("CHROMADB ERROR:")
            print(type(e))
            print(str(e))
            raise

    def search(self, query, top_k=2):

        print("Generating query embedding...")

        query_embedding = self.model.encode([query]).tolist()[0]

        print("Searching ChromaDB...")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results