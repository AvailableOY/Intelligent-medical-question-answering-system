from sentence_transformers import SentenceTransformer
import numpy as np

_MODEL_PATH = "D:/MyFirstD/PythonModel/huggingface/bge-base-zh-v1.5" 
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_PATH)
        print("✅ 成功加载 bge-base-zh-v1.5 模型")
    return _model

def is_related_to_history(current_question, history_questions, threshold=0.6):
    if not history_questions:
        return False

    model = get_model()
    current_vec = model.encode(current_question)

    max_sim = 0.0
    for hist_q in history_questions:
        hist_vec = model.encode(hist_q)
        sim = np.dot(current_vec, hist_vec) / (np.linalg.norm(current_vec) * np.linalg.norm(hist_vec))
        if sim > max_sim:
            max_sim = sim

    print(f"🔹 [语义检测] 当前问题 vs 历史: 最高相似度={max_sim:.4f}, 阈值={threshold}")
    return max_sim >= threshold