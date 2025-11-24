from openai import OpenAI

# ==================== 配置区 ====================
client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1",  # 你的本地模型服务地址
)

MODEL_NAME = "/data/huggingface/deepseek-1.5B"  # 替换为你实际的模型路径或名称

# ==================== 检索工具（模拟 Milvus）====================
def retrieve_documents(query: str) -> str:
    """
    模拟向量数据库检索（如 Milvus / FAISS）
    实际项目中请替换为真实查询逻辑
    """
    mock_knowledge_base = {
        "YOLOv8小目标检测": """YOLOv8 在小目标检测上表现不佳的主要原因是特征图分辨率低和锚框不匹配。
        改进方法包括：
        1. 使用 PAFPN 替代 PANet 提升小目标特征融合；
        2. 减小 anchor 尺寸（如设置 [8, 16, 32]）；
        3. 引入 CBAM 或 ECA 注意力模块；
        4. 使用 Focal Loss 或 Distribution Focal Loss；
        5. 数据增强：Mosaic + MixUp + RandomResize（放大小目标）。
        参考论文：Small Object Detection in YOLOv8: A Comprehensive Survey (2024)""",

        "小目标检测 数据增强": """对于小目标，推荐使用 Mosaic 增强（将4张图拼接）和 RandomResize（随机缩放至原图2~3倍），使小目标占据更大像素区域。""",
        
        "PAFPN YOLOv8": """PAFPN（Path Aggregation Feature Pyramid Network）在 YOLOv8 中用于增强多尺度特征融合，尤其对小目标有显著提升，相比 PANet 更能保留低层细节信息。""",
        
        "Distribution Focal Loss": """Distribution Focal Loss (DFL) 将回归问题建模为分布预测，对小目标定位更鲁棒，已在 YOLOv8s 上验证可提升 mAP 1.5~2.5%。"""
    }

    for key_phrase in mock_knowledge_base:
        if key_phrase in query:
            return mock_knowledge_base[key_phrase]

    return "未找到相关文档，请尝试更具体的关键词。"


# ==================== 提示词模板 ====================
QUERY_EXPANSION_PROMPT = """
你是检索增强生成（RAG）系统中的查询扩展专家，非常擅长使用Milvus。
请将用户提出的简短查询扩展为一段详细的文档式检索请求，以便后续检索到更加全面和高质量的文档。
注意：不要回答问题，字数限制在100之内，直接返回扩展后的结果，不要有其他任何输出
用户查询：**{Query}**
"""

AGENT_PROMPT_TEMPLATE = """
你是一个AgenticRAG智能体，负责处理用户的复杂信息需求。你拥有以下能力：
- 你可以通过 'search' 工具获取外部知识
- 你必须逐步思考，每一步都输出 Thought 和 Action（如果需要）
- 你不能编造信息，必须基于检索结果作答

用户问题：{input}

请按以下格式逐步思考并行动：

Thought: 你的推理过程
Action: search（仅当需要外部信息时使用）
Action Input: 检索关键词（如果是第一次，使用扩展后的查询）
Observation: （系统自动填充）
Final Answer: 最终答案（必须基于观察结果，清晰、专业、有条理）

开始：
"""


# ==================== 主智能体函数 ====================
def agentic_rag(user_query: str):
    print(f"🔍 用户输入：{user_query}\n")

    # Step 1: 查询扩展（Query Expansion）
    expansion_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "你是检索增强生成(RAG)系统中的查询扩展专家"},
            {"role": "user", "content": QUERY_EXPANSION_PROMPT.format(Query=user_query)}
        ],
        stream=False,
        temperature=0.1,
        max_tokens=150
    )
    expanded_query = expansion_response.choices[0].message.content.strip()
    print(f"✨ 查询扩展后：{expanded_query}\n")

    # Step 2: AgenticRAG 循环（ReAct 思维链）
    max_iterations = 3
    iteration = 0
    observation = ""  # 初始无观察
    thought = ""
    action = ""

    while iteration < max_iterations:
        iteration += 1
        print(f"🔄 第 {iteration} 轮思考...")

        # 构建当前上下文提示
        prompt_content = AGENT_PROMPT_TEMPLATE.format(input=user_query)
        if thought or action:
            prompt_content += f"\n\nThought: {thought}\nAction: {action}\nObservation: {observation}"

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个AgenticRAG智能体，遵循ReAct范式。"},
                {"role": "user", "content": prompt_content}
            ],
            stream=False,
            temperature=0.2,
            max_tokens=600
        )

        full_response = response.choices[0].message.content.strip()
        print(f"🧠 模型输出：\n{full_response}\n")

        # 检查是否已得出最终答案
        if "Final Answer:" in full_response:
            final_answer = full_response.split("Final Answer:")[-1].strip()
            print("="*70)
            print("✅ 最终答案：")
            print(final_answer)
            return final_answer

        # 解析 Thought / Action / Action Input
        lines = full_response.splitlines()
        thought = ""
        action = ""
        action_input = ""

        for line in lines:
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                action_input = line.replace("Action Input:", "").strip()

        # 执行动作：检索
        if action == "search":
            if not action_input:
                action_input = expanded_query  # 默认用扩展后的查询
            print(f"⚡ 调用检索工具，关键词：{action_input}")
            observation = retrieve_documents(action_input)
            print(f"📚 检索结果：{observation[:200]}...\n")
            continue
        else:
            # 如果模型没请求检索，强制检索一次（避免空转）
            print("⚠️ 模型未请求检索，强制进行一次检索...")
            observation = retrieve_documents(expanded_query)
            print(f"📚 强制检索结果：{observation[:200]}...\n")
            continue

    # 超过轮次仍未结束，强行输出最后检索内容
    print("⏰ 超过最大迭代次数，输出最后检索结果作为答案")
    final_result = retrieve_documents(expanded_query)
    print("="*70)
    print("✅ 最终答案（超限兜底）：")
    print(final_result)
    return final_result


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 示例输入（可替换成任意问题）
    question = "YOLOv8小目标检测"
    result = agentic_rag(question)