from chromadb.utils import embedding_functions
from django.conf import settings

CHROMA_CONFIG = {
        "embedding_model_path": "D:/PythonModel/huggingface/bge-base-zh-v1.5",
        "collection_name": "my-collection-decimal"
        }
class ChromaDB:
    def __init__(self):
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=CHROMA_CONFIG["embedding_model_path"]
        )
    def myPrint(self):
        test_emb = self.emb_fn(["test"])
        print("Embedding dimension:", len(test_emb[0])) 

if __name__ == "__main__":
    myChromaDB = ChromaDB()
    myChromaDB.myPrint()