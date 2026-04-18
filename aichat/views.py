import json
from django.http import JsonResponse,StreamingHttpResponse
from django.conf import settings
# print(settings.VLLM_CONFIG)
from .Qwen import Deepseek
from .models import Topic,Chat
import requests
import chromadb
from utils.KGLLM import KG_LLM
kg_llm = KG_LLM()
from utils.neo import *




# LLM内容生成的参数
gen_kwargs = {
    "max_tokens": 4096,  # 生成的最大长度  4096
    "temperature": 0.7,  # 生成丰富性，越大越有创造力 越小越确定
    "top_p": 0.8,  # 采样时的前P个候选词，越大越随机
    "extra_body": {
        "do_sample": True,  # 是否使用概率采样
        "top_k": 50,  # 采样时的前K个候选词，越大越随机
        "repetition_penalty": 1.2,  # 重复惩罚系数，越大越不容易重复
    },
}

qwen = Deepseek(host=settings.VLLM_CONFIG.get("host"),
                model=settings.VLLM_CONFIG.get("model"),
                gen_kwargs=gen_kwargs
)
# requests请求地址
requeset_base_url = settings.VLLM_CONFIG.get("host") + "/tokenize"

# 词向量数据库
from .RagChroma import MyChromaDB
vdb = MyChromaDB(settings.RAG_CONFIG)

# 一次性加载知识块到内存中
CHUNKS_PATH = settings.RAG_CONFIG["chunks_path"]
print("加载知识块中...",CHUNKS_PATH)
knowledge = []
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    knowledge = json.load(f)
# 构建docments用于rerank
# print(knowledge,"这是knowledge")
# documents = [item["content"] for item in knowledge]
documents = [item["output"] for item in knowledge]






def chathistory(request):
    # 接收客户端提交上来的主题ID
    topic_id = int(request.GET.get("topic_id","0"))
    print("主题ID:",topic_id)
    # print("主题ID:",topic_id)
    # 获取主题下面的聊天内容
    chats = Chat.objects.filter(topic_id=topic_id,status = 1).order_by("id")
    history = []
    for item in chats:
        history.append({
            "role":item.role,
            "content":item.content
        })
    data = {
        "code":200,
        "message":"获取成功",
        "data":history
    }
    return JsonResponse(data,safe=False)

def _truncate_messages(messages, max_tokens_len=4000):
    current_tokens_len = 0
    temp = [{"role": "system", "content": "你是一个可靠的AI助手"}]
    for msg in reversed(messages[1:]):
        # current_tokens_len += len(msg["content"] * 0.6)  # 最高效的，对服务器的压力比较小
        # 下面的代码是最精确的：服务器的压力比较大
        resp = requests.post(
            requeset_base_url,
            json={"prompt": msg["content"]}
        )
        current_tokens_len += resp.json()["count"]
        if current_tokens_len > max_tokens_len:
            break

        temp.insert(1, msg)

    return temp
def ai_chat_123(request):

    question = request.POST.get("question"," ")
    messages = [
        {"role": "system", "content": "你是一个可靠的AI助手,尽可能根据''{Context}'中的内容回答用户问题，请使用中文回答"},
        # {"role": "user", "content": question}
    ]
    print("用户问题:",question)

    # 接收客户端提交上来的主题ID
    topic_id = int(request.POST.get("topic_id","0"))
    print("----------主题ID:",topic_id)

    # 保存：对话的主题
    if topic_id == 0:
        summary = question
        if len(summary)>40:
            # 生成摘要
            summary = qwen.inference([
                {"role": "system", "content": "你是一个可靠的AI助手,你需要总结用户的问题，不需要推理,并且返回40字以内的总结"},
                {"role": "user", "content": f"请根据下面内容生成40字以内的摘要：不需要推理，直接生成：\n\n{question}"}
            ])
        
        topic1 = Topic(title=question,summary=summary.split("</think>")[-1][:40],user_id=6)
        topic1.save()
        topic_id = topic1.id
        print("新建的主题主键ID",topic1.id)
    else:
        # 获取主题下面的聊天内容
        chats = Chat.objects.filter(topic_id=topic_id).order_by("id")
        for item in chats:
            messages.append(
                {
                    "role": item.role,
                    "content": (
                        item.content
                        if item.role == "user"
                        else item.content.split("</think>")[-1]
                    ),
                }
            )


    # Chroma词向量数据库
    # 无论如何用户的问题都要追加在最后面
    # 用户问题完成知识块的筛选 粗排和精拍都支持
    # 根据用户问题完初筛
    # rerank_results = vdb.query(question,topk=settings.RAG_CONFIG["rerank_threshold"])
    # #RAG 

    # rerank_top_k = settings.RAG_CONFIG["rerank_top_k"]

    # # 根据阈值筛选上下文信息
    # threshold = settings.RAG_CONFIG["rerank_threshold"]
    # contexts, metedatas = vdb.filter_knowledge(rerank_results,threshold)
    # context_text = "\n\n".join(contexts)

    # Neo4j词向量库
    result = kg_llm.query(question,3)
    print(result)
    context_lists = []
    if len(result) > 0:
        #根据每一个关键词创建上下文信息
        for words in result:
            contexts = get_context(words)
            context_lists.extend(contexts)
        print("完整的上下文信息：",context_lists)
    context_text = "\n\n".join(context_lists)



    if len(contexts) == 0:
        prompt = f''' 
                请回答用户问题：
                    Context: {context_text},
                    Question: {question},
                    Response:
                '''
    else:
        # TODO 把上下文信息存储到数据库，用于统计命中率
        prompt = f''' 
                结合上下文内容，请回答用户问题：
                    Context: {context_text},
                    Question: {question},
                    Response:
                '''
    messages.append({"role": "user", "content": prompt})
    messages = _truncate_messages(messages)
    print("最终的prompt:",messages)

    # print('构建的对话列表：', messages)
    response_data = qwen.inference(messages,True)

    # 保存：对话的内容
    chat1 = Chat(content = question,topic_id = topic_id,user_id = 6,role="user")
    chat1.save()
    print("新增的数据主键ID:",chat1.id)

        # 用于拼接 AI 的完整回复
    assistant_reply = ""

    # 流式
    def event_stream():
        # 加一个异常处理，防止客户端断开连接
        try:
            # 响应主题的id到客户端
            yield "data: <topic_id__IGCV>" + str(topic_id) + "</topic_id__IGCV>\n\n"
            content = ""
            for chunk in response_data:  # 流式
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    # 打印delta原始信息
                    # print("内容块：", delta)
                    if delta and delta.content:
                        # SSE 协议要求：必须以 "data:" 开头，以两个换行结尾
                        content += delta.content
                        content_chunk = delta.content.replace("\n", "\\n")
                        yield f"data: {content_chunk}\n\n"
            # 记录模型的回答
            # 记录大模型回答的内容
            chat2 = Chat(content=content, topic_id=topic_id, user_id=6, role="assistant")
            chat2.save()
            print("新增的LLM主键ID：", chat2.id)

        except Exception as e:
            print("异常：",e)
            yield "data:[DONE]\n\n"
        finally: 
            # yield "data:<metedata_IGCV>" + str(metedatas) + "</metedata_IGCV>\n\n"
            yield "data:[DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    # 设置缓存控制：只要有yield产生的数据，就立即响应到客户端，不要缓存
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # 禁止 Nginx 缓冲
    return response

def chatlist(request):
    # 假设用户ID
    user_id = 6
    # 逻辑删除，不是物理意义的删除，只是逻辑删除，数据还在，只是标记为删除
    history = Topic.objects.filter(user_id=user_id,status = 1).order_by("-id")
    chatlist = []
    #  把数据放到列表
    for item in history:
        chatlist.append({
            "id":item.id,
            "title":item.summary,
        })
    data = {
        "code":200,
        "message":"获取成功",
        "data":chatlist
    }
    return JsonResponse(data,safe=False)

def deltopic(request):
    topic_id = request.GET.get("topic_id","0")
    # 删除主题
    # Topic.objects.filter(id=topic).delete()
    # 删除对话内容
    # Chat.objects.filter(topic_id=topic).delete()
    Topic.objects.filter(id=topic_id).update(status=0)
    data = {
        "code":200,
        "message":"删除成功"
    }
    return JsonResponse(data)
