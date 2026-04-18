from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def init_mock_vector_db():
    print("  -> [Vector DB] 正在初始化本地商品知识库...")
    
    # 模拟几条电商商品数据
    mock_products = [
        "Keychron K3 Pro 矮轴机械键盘：完美适配 macOS 快捷键，轻薄便携，适合长期敲代码和日常办公，支持蓝牙多设备无缝切换。",
        "雷蛇巴塞利斯蛇 V3 电竞鼠标：具备 26000 DPI 高精度传感器，RGB 幻彩灯效，11个可编程按键，非常适合用来玩《原神》或《GTA V》等对操作要求高的游戏。",
        "Suntory 乌龙茶无糖版（整箱24瓶）：茶多酚含量高，口感清爽不涩，适合日常补水，0糖0脂0卡，健康轻负担。",
        "索尼 WH-1000XM5 头戴式降噪耳机：行业标杆级主动降噪，30小时超长续航，支持多点触控与佩戴感应。"
    ]
    
    docs = [Document(page_content=text) for text in mock_products]
    
    # 使用 OpenAI 的 Embedding 模型将文本向量化并存入 Chroma
    # 注意：这里会消耗微量的 OpenAI API 额度
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=OpenAIEmbeddings(model="text-embedding-ada-002")
    )
    
    # 返回一个检索器，设置每次召回最相关的 2 条数据
    return vectorstore.as_retriever(search_kwargs={"k": 2})

# 全局单例检索器
product_retriever = init_mock_vector_db()