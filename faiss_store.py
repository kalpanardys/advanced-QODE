import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from utils import load_qode_data


class FAISSStore:

    def __init__(self, file_path="sample_questions.xlsm"):

        self.file_path = file_path

        print("Loading BGE model...")
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")

        self.index = None
        self.documents = []

    def build_index(self):

        print("Loading dataframe...")

        df = load_qode_data(self.file_path)

        docs = []

        for _, row in df.iterrows():

            text = (
                f"Role: {row.get('Team / owner role', '')}. "
                f"Tool: {row.get('Automation tool', '')}. "
                f"Input: {row.get('Input', '')}. "
                f"Output: {row.get('Output', '')}."
            )

            docs.append(text)

        self.documents = docs

        print(f"Documents loaded = {len(docs)}")

        print("Generating embeddings...")

        embeddings = self.model.encode(docs)

        embeddings = np.array(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(embeddings)

        print(f"Indexed {self.index.ntotal} vectors")

    def search(self, query, top_k=5):

        query_embedding = self.model.encode(
            [query]
        )

        query_embedding = np.array(
            query_embedding,
            dtype="float32"
        )

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for idx in indices[0]:

            if idx < len(self.documents):
                results.append(
                    self.documents[idx]
                )

        return results