from ddgs import DDGS

def perform_web_search(query, max_results=3):
    """
    使用 DuckDuckGo 进行网络搜索，返回前 max_results 个结果的文本摘要
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            summaries = []
            for r in results:
                # 可选：只取标题+摘要，或加上正文片段
                summary = f"标题: {r['title']}\n摘要: {r['body']}\n链接: {r['href']}"
                summaries.append(summary)
            return summaries
    except Exception as e:
        print(f"Web Search Error: {e}")
        return []