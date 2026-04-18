import json
import os
import chromadb
from django.conf import settings
from chromadb.utils import embedding_functions
import requests
from aiserver.settings import BASE_DIR, RAG_CONFIG

CHROMA_HOST = settings.RAG_CONFIG["chroma_host"]
CHROMA_CONFIG = settings.RAG_CONFIG["chroma_config"]
chunks_path = os.path.join(BASE_DIR,"chunks","knowledge_chunks.json")
# if os.path.exists(chunks_path):
#     with open(chunks_path, 'r', encoding='utf-8') as f:
#         chunks = json.load(f)

#     print("📁 chunks 类型：", type(chunks))
#     print("📝 chunks 前两条数据：")
#     for i, c in enumerate(chunks[:2]):
#         print(f"  [{i+1}] 类型: {type(c)}, 内容: {c}")

# else:
#     print("❌ chunks 文件不存在！", chunks_path)
# chroma_client = chromadb.HttpClient(host = CHROMA_HOST["host"],port=CHROMA_HOST["port"])
# print("chroma_client:",chroma_client)

class MyChromaDB:
    def __init__(self,regconfig = {}):
        self.chroma_client = chromadb.HttpClient(
            host=regconfig["chroma_host"]["host"],port=regconfig["chroma_host"]["port"]
        )
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=CHROMA_CONFIG["embedding_model_path"]
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_CONFIG["collection_name"],
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.emb_fn,
        )
        print("✅ 集合名称:", self.collection.name)
        print("📊 集合中的总条目数:", self.collection.count())

        # ⭐ 关键步骤：尝试删除已存在的 collection（如果存在）
        # collection_name = CHROMA_CONFIG["collection_name"]
        # try:
        #     self.chroma_client.delete_collection(name=collection_name)
        #     print(f"🗑️ 已删除旧的集合: {collection_name}")
        # except Exception as e:
        #     print(f"ℹ️ 集合 '{collection_name}' 不存在或无法删除，继续创建... ({e})")
        # 👇 自动插入数据（仅当集合为空时）
        if self.collection.count() == 0:
            print("⚠️ 集合为空，正在插入数据...")
            self.insert_chunks()

            
        # 查看前 3 条数据（简洁显示）
        # peek_data = self.collection.peek(3)
        # for i, doc in enumerate(peek_data.get('documents', [])):
        #     # print(f"📄 样例文本 {i+1}: {doc[:150]}...")
        #     print("_________________________________-")
    def insert_chunks(self):
        # 1. 读取 chunks
        with open(RAG_CONFIG["chunks_path"], 'r', encoding='utf-8') as f:
            data = json.load(f)  # 加载JSON数据
        
        # # 2. 提取所有content字段
        # texts = [item["content"] for item in data if "content" in item]
        # 2. 提取所有 output 字段作为文档内容
        texts = [item["output"] for item in data if "output" in item]
        
        # 3. 准备 IDs 和数据
        ids = [f"chunk_{i}" for i in range(len(texts))]
        
        # 4. 插入到 Chroma（会自动计算 embedding）
        self.collection.add(
            ids=ids,
            documents=texts
        )
        print(f"✅ 成功插入 {len(texts)} 条文本块到集合 '{self.collection.name}'")

    # 定义查询方法
    def query(self,query_texts,n_results=20,ifRerank=True,topk=5):
        # 粗排：词向量数据库检索
        results = self.collection.query(
            query_texts=[query_texts],
            n_results=n_results,
        ) 
        # print("粗排的文档+++++++++",results)
        # 判断是否找到关联的知识块
        if len(results["documents"][0]) == 0: 
            return {
                "没找到答案"
            }
        # TODO 需要处理元消息和得分
        if not ifRerank: 
            return{
                "documents":results["documents"][0],
                "metadatas":results["metadatas"][0], 
                "distances":results["distances"][0],
                "ids":results["ids"][0]
            } 
        # 二次精排
        data = {
            "model":"/data/huggingface/bge-reranker-base",
            "query":query_texts,
            "documents": results["documents"][0],
        }
        # print("数据=========",data)
        response = requests.post(settings.RAG_CONFIG["rerank_host"],json=data)
        # print("======================",response.json())
        rerank_results = response.json()["results"][:5]
        # print("最相关的内容----==",rerank_results)
        # 构建metadata消息
        metedatas = []
        documents = []
        relevance_scores = []
        for d in rerank_results:
            (
                metedatas.append(results["metadatas"][0][d["index"]]) 
                if results["metadatas"][0][d["index"]] not in metedatas
                else None
            )
            documents.append(d['document']["text"]),
            relevance_scores.append(d["relevance_score"])
        # print("元消息----------------------------",metedatas)
        return {
            "documents": documents,
            "metadatas": metedatas,
            "relevance_scores": relevance_scores,
        }
        return rerank_results        
    # 根据阈值对找到的知识块进行筛选
    def filter_knowledge(self,rerank_results,threshold):
        print("原始内容",rerank_results)
        contexts = []
        metedatas = []
        for i,score in enumerate(rerank_results['relevance_scores']):
            if score >= threshold:
                contexts.append(rerank_results["documents"][i])
                # 构建不重复的元数据
                (
                    # 这里(rerank_results["metadatas"][0]) 因为是None 所以暂时填0 应该填i
                    metedatas.append(rerank_results["metadatas"][0]) 
                    if rerank_results["metadatas"] not in metedatas
                    else None
                )
        return contexts,metedatas
        print("筛选后的内容",contexts)
        print("元消息",metedatas)