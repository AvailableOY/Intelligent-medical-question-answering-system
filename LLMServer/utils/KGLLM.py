import os
from openai import OpenAI
from langchain.prompts import PromptTemplate




class KG_LLM:
    def __init__(self,model = "qwen3-max-preview"):
        self.client = OpenAI(
            #若没有配置环境变量，请用百炼APIKey将下行替换为:api_key="sk-xxx",
            # sk-a8ad6e6eadff4f64b051208bced4476e
            api_key = "sk-a8ad6e6eadff4f64b051208bced4476e",#如何获取API Key:https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model

    def query(self, query,max_keywords):
        prompt_template = '''
            给定一些初始查询，提取最多{max_keywords}个相关关键词，考虑大小写、复数形式、常见表达等，
            用'|'符号分隔所有同义词/关键词:"关键词1|关键词2|关键词3|..."
            提取实体或者关系，提取的关键词不要有比如怎么治疗、生病、中毒、病这类似的词不是提取词，
            还有比如用户问题: 二硫化碳中毒吃什么
            只提取：二硫化碳中毒
            直接提取，不要有其他的输出。
            比如用户问题：得了这个病应该吃什么
            就不提取病这个词
            句子： ''{text}''
            结果：
            '''
        finally_template= PromptTemplate(   
            input_variables=["text","max_keywords"],
            template = prompt_template,
        )
        prompt = finally_template.format(text = query,max_keywords = 3)
        completion =self.client.chat.completions.create(
            #模型列表:https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen-plus",#qwen-plus属于qwen3模型，如需开启思考模式，请参见:https://help.aliyun.com/zh/model-studio/deep-thinking
            messages=[
            {'role': 'system','content': "你是一位知识图谱专家，擅长从一句话里面提取知识三元组"},
            {"role":'user','content':prompt}
            ]
        )
        return completion.choices[0].message.content.split("|")

