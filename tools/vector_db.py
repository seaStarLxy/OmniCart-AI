from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def init_mock_vector_db():
    print("  -> [Vector DB] 1. 开始初始化本地商品知识库...")
    
    # 这里放回了你原本的 4 条模拟商品数据
    mock_products = [
        "Keychron K3 Pro 矮轴机械键盘：完美适配 macOS 快捷键，轻薄便携，适合长期敲代码和日常办公，支持蓝牙多设备无缝切换。",
        "雷蛇巴塞利斯蛇 V3 电竞鼠标：具备 26000 DPI 高精度传感器，RGB 幻彩灯效，11个可编程按键，非常适合用来玩《原神》或《GTA V》等对操作要求高的游戏。",
        "Suntory 乌龙茶无糖版（整箱24瓶）：茶多酚含量高，口感清爽不涩，适合日常补水，0糖0脂0卡，健康轻负担。",
        "索尼 WH-1000XM5 头戴式降噪耳机：行业标杆级主动降噪，30小时超长续航，支持多点触控与佩戴感应。"
    ]
    
    docs = [Document(page_content=text) for text in mock_products]
    
    print("  -> [Vector DB] 2. 准备初始化 Embeddings 对象...")
    embeddings = OpenAIEmbeddings(
        openai_api_base="https://api.siliconflow.cn/v1",
        openai_api_key="apikey", 
        model="BAAI/bge-m3",
        check_embedding_ctx_length=False,
        # 【新增】：强制设置 15 秒超时，并且只重试 1 次，打破无限卡死
        timeout=15,
        max_retries=1
    )
    
    print("  -> [Vector DB] 3. 开始调用 API 将数据向量化并写入 Chroma...")
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings
    )
    
    print("  -> [Vector DB] 4. 向量库初始化完成！")
    return vectorstore.as_retriever(search_kwargs={"k": 2})

# 全局单例检索器
product_retriever = init_mock_vector_db()