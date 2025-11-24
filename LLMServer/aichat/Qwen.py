from openai import OpenAI

class Deepseek():
    def __init__(self,host,model,gen_kwargs):
        self.client = OpenAI(
            api_key="EMPTY",
            base_url= host + "/v1",
        )
        #二:设置生成参数和输入消息
        self.gen_kwargs = gen_kwargs
        self.model = model
        pass
    def inference(self,messages,stream=False):
        response = self.client.chat.completions.create(
        model = self.model,
        messages=messages,
        stream=stream, #是否流式返回
        **self.gen_kwargs
        )
        # 只是非流式
        if not stream: 
            return response.choices[0].message.content
        # 流式
        return response
    
    







