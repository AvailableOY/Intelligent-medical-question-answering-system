from openai import OpenAI
from langchain_core.prompts import PromptTemplate

client=OpenAI(
    api_key="EMPTY", # APIKey
    base_url="http://localhost:8000/v1",# 请求地址: /chat/completions
)


def rag_subproblems(question):
    Question = question
    prompt_template = """
        你是一名问题分析专家，请将以下复杂问题拆解为3个可以单独查询的子问题，尽量覆盖该复杂问题的所有核心要素。
        复杂问题：
        {Query}
        直接返回子问题，不要其他信息
        请拆解为子问题：
    """
    prompt = PromptTemplate(input_variables=["Query"], template=prompt_template)
    response =client.chat.completions.create(
        model="/data/huggingface/deepseek-1.5B", #
        #使用的模型:可以是模型名称或者模型路径
        messages=[
            {"role":"system","content":"你是检索增强生成(RAG)系统中的查询扩展专家"},
            {"role":"user","content":prompt.format(Query=Question)},
        ],
        stream=False,
    )
    #Python里面的数据类型的知识点
    print(response.choices[0].message.content)