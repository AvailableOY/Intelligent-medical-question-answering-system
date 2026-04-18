# from py2neo import Graph
# # 连接到Neo4j数据库
# graph = Graph("bolt://localhost:7687", auth=("neo4j", "Ouyang_1"),name="neo4j")
# print("连接成功",graph)
# def node_type_query(keyword, nodeType):
#     """
#     根据关键词和节点类型，在 Neo4j 图数据库中查询匹配的节点。
    
#     参数:
#         keyword (str): 要匹配的关键词（如公司名、投资人名、事件名等）
#         nodeType (str): 节点类型（如 "Investor", "Company", "EventType"）
    
#     返回:
#         list: 包含匹配节点的字典列表，每个字典代表一个节点对象
#     """
#     # 构造 Cypher 查询语句，查找指定类型节点中 name 属性包含关键词的节点
#     cypher = f"MATCH (n:{nodeType}) WHERE n.name CONTAINS '{keyword}' RETURN n"
#     print(cypher)
#     # 执行查询并返回原始数据（字典列表）
#     result = graph.run(cypher).data()
#     # 可选：打印调试信息（已注释掉）
#     # res = [item['n']['name'] for item in result[:10]]
#     # print(result)
#     # names = [item['name'] for item in result]
#     # print(f"查询到 {nodeType} 类型节点: {names}")
#     return result


# def neo4j_query(
#     investor_condition, company_condition, eventtype_condition, query_level=1
# ):
#     """
#     根据传入的条件，在 Neo4j 中执行投资关系或事件关系的查询。
    
#     参数:
#         investor_condition (str): 投资人筛选条件（Cypher WHERE 子句片段）
#         company_condition (str): 公司筛选条件（Cypher WHERE 子句片段）
#         eventtype_condition (str): 事件类型筛选条件（Cypher WHERE 子句片段）
#         query_level (int): 查询级别。1=包含投资人关系，2=仅公司与事件关系
    
#     返回:
#         list: 格式化后的上下文字符串列表，用于展示或后续处理
#     """
#     if query_level == 1:
#         # 查询投资人 -> 公司 -> 事件 的完整路径
#         query = f"""
#             MATCH (i:Investor)-[:INVEST]->(c:Company)
#             WHERE 1=1 {investor_condition}
#             OPTIONAL MATCH (c:Company)-[r:HAPPEN]->(e:EventType)
#             WHERE 1=1 {company_condition}{eventtype_condition}
#             RETURN i.name as investor, c.name as company_name, e.name as even_type, r as relation
#         """
#     elif query_level == 2:
#         # 仅查询公司 -> 事件 的路径（不涉及投资人）
#         query = f"""
#             MATCH (c:Company)-[r:HAPPEN]->(e)
#             WHERE 1=1 {company_condition} {eventtype_condition}
#             RETURN c.name as company_name, e.name as even_type, r as relation
#             """
#     # 执行 Cypher 查询
#     result = graph.run(query).data()

#     # 初始化用于存储最终结果的变量
#     contexts = []           # 最终返回的上下文字符串列表
#     context_list = {}       # 投资人 -> [公司列表] 的映射
#     company_happen = {}     # 公司 -> [事件列表] 的映射

#     # 第一次遍历：整理数据结构，去重冗余信息
#     for item in result:
#         # 如果查询结果包含投资人（即 query_level=1 的情况）
#         if "investor" in item:
#             # 将该公司添加到该投资人的公司列表中（自动创建键）
#             context_list.setdefault(item["investor"], []).append(item["company_name"])

#         # 如果有事件发生（事件可能为空，因为是 OPTIONAL MATCH）
#         if item["even_type"]:
#             # 将该事件添加到该公司的事件列表中
#             company_happen.setdefault(item["company_name"], []).append(item["even_type"])
#     # 如果存在投资人相关的数据（即 context_list 非空）
#     if len(context_list) > 0:
#         # 对每个投资人的公司列表去重
#         context_list = {k: list(set(v)) for k, v in context_list.items()}
#         # 生成最终的上下文描述字符串
#         for k, v in context_list.items():
#             for c in v:
#                 # 拼接：投资人 + 投资了 + 公司 + （可选）事件描述
#                 context = f"{k} 投资了 {c}{('，该公司发生了以下事件：' + '、'.join(company_happen.get(c, []))) if len(company_happen.get(c, [])) > 0 else ''}"
#                 contexts.append(context)
#     else:
#         # 如果没有投资人数据，只显示公司发生的事件
#         for k, v in company_happen.items():
#             context = f"{k}{('发生了以下事件：' + '、'.join(company_happen.get(k, []))) if len(company_happen.get(k, [])) > 0 else ''}"
#             contexts.append(context)
#     # print("完整的上下文信息：",contexts)
#     return contexts


# def get_context(words):
#     """
#     主查询入口函数：根据输入关键词，自动判断其属于哪种节点类型，
#     并执行相应的关系查询，返回格式化的上下文信息。
    
#     参数:
#         words (str): 用户输入的关键词（如公司名、投资人名、事件名）
    
#     返回:
#         list: 格式化的上下文字符串列表；若无匹配结果，返回空列表
#     """
#     # 分别查询关键词是否匹配投资人、公司、事件类型节点
#     Investor_Type = node_type_query(words, "Investor")
#     print(words,"=============")
#     Company_Type = node_type_query(words, "Company")
#     EventType_Type = node_type_query(words, "EventType")

#     # 初始化查询条件字符串（用于拼接到 Cypher 的 WHERE 子句）
#     investor_condition = ""
#     company_condition = ""
#     eventtype_condition = ""

#     # 只要有一个节点类型匹配成功，就构造查询条件
#     if Investor_Type or Company_Type or EventType_Type:
#         if Investor_Type:
#             investor_condition = f" AND i.name CONTAINS '{words}'"
#         if Company_Type:
#             company_condition = f" AND c.name CONTAINS '{words}'"
#         if EventType_Type:
#             eventtype_condition = f" AND e.name CONTAINS '{words}'"
#     else:
#         # 如果没有任何节点匹配，直接返回空列表
#         return []

#     # 先尝试第一级查询（包含投资人关系）
#     contexts = neo4j_query(investor_condition, company_condition, eventtype_condition)

#     # 如果第一级查询无结果，降级到第二级查询（仅公司与事件）
#     if len(contexts) == 0:
#         contexts = neo4j_query(
#             investor_condition,
#             company_condition,
#             eventtype_condition,
#             query_level=2,
#             # 注意：原代码中 exclude_content 参数未在函数定义中声明，可能是笔误或遗留参数，建议删除或修正
#             # exclude_content=False,  # ← 此参数在函数定义中不存在，会导致 TypeError
#         )

#     return contexts

# def neo4j_query(investor_condition,company_condition,eventtype_condition):
#     query = f"""
#             MATCH (i:Investor)-[:INVEST]->(c:Company)
#             WHERE 1=1{investor_condition}
#             OPTIONAL MATCH (c)-[r:HAPPEN]->(e:EventType)
#             WHERE 1=1{company_condition}{eventtype_condition}
#             RETURN i.name as Investor, c.name as company_name, e.name AS eventtype,r as relation
#         """
#     # 执行query语句
#     result = graph.run(query).data()
#     print("查询结果为：",result)
#     return result

# def get_context(words):
#     investor_names = node_type_query(words, "Investor")
#     company_names = node_type_query(words, "Company")
#     event_names = node_type_query(words, "EventType")  

#     investor_condition = ""
#     company_condition = ""
#     eventtype_condition = ""

#     # 拼接条件（注意加引号！）
#     if investor_names:
#         investor_condition = f" AND i.name IN {repr(investor_names)}"
#     if company_names:
#         company_condition = f" AND c.name IN {repr(company_names)}"
#     if event_names:
#         eventtype_condition = f" AND e.name IN {repr(event_names)}"

#     # 如果没有任何匹配，返回空
#     if not (investor_names or company_names or event_names):
#         return []

#     return neo4j_query(investor_condition, company_condition, eventtype_condition)


from py2neo import Graph

# 连接到 Neo4j 数据库（请确认你的数据库地址和密码）
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Ouyang_1"), name="neo4j")
print("✅ 连接成功:", graph)


def node_type_query(keyword, nodeType):
    """
    根据关键词和节点类型，在 Neo4j 中查询匹配的节点。
    
    参数:
        keyword (str): 查询关键词（如“咳嗽”、“红霉素”）
        nodeType (str): 节点标签（如 "Disease", "Symptom", "Drug"）
    
    返回:
        list: 包含匹配节点的字典列表，每个元素为 {'n': {...}}
    """
    # 使用 CONTAINS 实现模糊匹配（支持中文）
    cypher = f"MATCH (n:{nodeType}) WHERE n.name CONTAINS '{keyword}' RETURN n"
    print(f"查询语句: {cypher}")
    result = graph.run(cypher).data()
    return result


def neo4j_query(disease_condition="", symptom_condition="", department_condition="", 
                check_condition="", drug_condition="", complication_condition="", food_condition=""):
    """
    根据条件查询疾病及其关联实体，返回结构化上下文。
    
    参数:
        各种 condition 是 Cypher WHERE 子句片段，例如 " AND d.name CONTAINS '糖尿病'"
    
    返回:
        list: 格式化的自然语言上下文字符串列表
    """
    # 构建主查询：从 Disease 出发，连接所有相关实体
    query = f"""
        MATCH (d:Disease)
        WHERE 1=1 {disease_condition}
        
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (d)-[:BELONGS_TO]->(dep:Department)
        OPTIONAL MATCH (d)-[:REQUIRES_CHECK]->(c:CheckItem)
        OPTIONAL MATCH (d)-[:TREATED_BY]->(dr:Drug)
        OPTIONAL MATCH (d)-[:HAS_COMPLICATION]->(comp:Complication)
        OPTIONAL MATCH (d)-[:RECOMMENDS_FOOD]->(f:Food)
        OPTIONAL MATCH (d)-[:AVOIDS_FOOD]->(af:Food)
        
        RETURN 
            d.name AS disease_name,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dep.name) AS departments,
            collect(DISTINCT c.name) AS checks,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT comp.name) AS complications,
            collect(DISTINCT f.name) AS recommend_foods,
            collect(DISTINCT af.name) AS avoid_foods
    """

    # print(f"执行查询:\n{query}")
    result = graph.run(query).data()

    contexts = []

    for item in result:
        disease = item["disease_name"]
        if not disease:
            continue

        # 构建上下文描述
        parts = [f"{disease}"]

        # 症状
        if item["symptoms"] and any(item["symptoms"]):
            parts.append(f"的主要症状包括：{'、'.join(item['symptoms'])}")

        # 科室
        if item["departments"] and any(item["departments"]):
            parts.append(f"属于：{'、'.join(item['departments'])}科")

        # 检查项目
        if item["checks"] and any(item["checks"]):
            parts.append(f"需做检查：{'、'.join(item['checks'])}")

        # 治疗药物
        if item["drugs"] and any(item["drugs"]):
            parts.append(f"常用药物有：{'、'.join(item['drugs'])}")

        # 并发症
        if item["complications"] and any(item["complications"]):
            parts.append(f"可能并发：{'、'.join(item['complications'])}")

        # 推荐饮食
        if item["recommend_foods"] and any(item["recommend_foods"]):
            parts.append(f"推荐饮食：{'、'.join(item['recommend_foods'])}")

        # 禁忌饮食
        if item["avoid_foods"] and any(item["avoid_foods"]):
            parts.append(f"禁忌食物：{'、'.join(item['avoid_foods'])}")

        # 合并成一句话
        context = "；".join(parts) + "。"
        contexts.append(context)

    return contexts


def search_by_symptom(symptom_keyword):
    """当用户输入的是症状时，反向查找有哪些疾病具有该症状"""
    cypher = f"""
        MATCH (s:Symptom)-[:HAS_SYMPTOM]->(d:Disease)
        WHERE s.name CONTAINS '{symptom_keyword}'
        RETURN DISTINCT d.name AS disease_name
    """
    result = graph.run(cypher).data()
    contexts = []
    for item in result:
        disease = item["disease_name"]
        contexts.append(f"【{symptom_keyword}】常见于疾病：{disease}")
    return contexts


def search_by_drug(drug_keyword):
    """当用户输入的是药物时，查找哪些疾病使用该药"""
    cypher = f"""
        MATCH (d:Drug)-[:TREATED_BY]->(dis:Disease)
        WHERE d.name CONTAINS '{drug_keyword}'
        RETURN DISTINCT dis.name AS disease_name
    """
    result = graph.run(cypher).data()
    contexts = []
    for item in result:
        disease = item["disease_name"]
        contexts.append(f"【{drug_keyword}】用于治疗疾病：{disease}")
    return contexts


def search_by_department(dept_keyword):
    """当用户输入的是科室时，查找该科室治疗哪些疾病"""
    cypher = f"""
        MATCH (dep:Department)-[:BELONGS_TO]->(d:Disease)
        WHERE dep.name CONTAINS '{dept_keyword}'
        RETURN DISTINCT d.name AS disease_name
    """
    result = graph.run(cypher).data()
    contexts = []
    for item in result:
        disease = item["disease_name"]
        contexts.append(f"【{dept_keyword}】科治疗疾病：{disease}")
    return contexts


def get_context(words):
    """
    主入口函数：接收用户输入关键词，自动识别类型并执行对应查询。
    
    参数:
        words (str): 用户输入的关键词（如“咳嗽”、“红霉素”、“呼吸内科”、“百日咳”）
    
    返回:
        list: 格式化的自然语言上下文列表
    """
    # 尝试匹配不同类型的节点
    disease_result = node_type_query(words, "Disease")
    symptom_result = node_type_query(words, "Symptom")
    drug_result = node_type_query(words, "Drug")
    dept_result = node_type_query(words, "Department")
    # 其他节点类型暂时不单独处理（可扩展）

    # 判断关键词最可能属于哪一类
    if disease_result:
        print(f"检测到关键词 '{words}' 是疾病实体")
        # 直接查询该疾病的全部信息
        disease_condition = f" AND d.name CONTAINS '{words}'"
        return neo4j_query(disease_condition=disease_condition)

    elif symptom_result:
        print(f"检测到关键词 '{words}' 是症状")
        return search_by_symptom(words)

    elif drug_result:
        print(f"检测到关键词 '{words}' 是药物")
        return search_by_drug(words)

    elif dept_result:
        print(f"检测到关键词 '{words}' 是科室")
        return search_by_department(words)

    else:
        print(f"未识别出有效实体类型：'{words}'")
        # 可选：尝试模糊匹配 Disease（兜底）
        disease_fallback = node_type_query(words, "Disease")
        if disease_fallback:
            print("使用兜底匹配：按疾病名称模糊查找")
            disease_condition = f" AND d.name CONTAINS '{words}'"
            return neo4j_query(disease_condition=disease_condition)

        return []  # 无结果