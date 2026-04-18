import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

API_KEY = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY") or "apikey"

MOCK_PRODUCTS = [
    "Keychron K3 Pro low-profile mechanical keyboard: optimized for macOS shortcuts, lightweight and portable, ideal for long coding sessions and daily office work, supports seamless Bluetooth multi-device switching. Price: RMB 699.",
    "Logitech MX Master 3S wireless mouse: ergonomic design, ultra-fast scrolling, works on any surface including glass, perfect for office work and productivity. Price: RMB 799.",
    "Razer Basilisk V3 gaming mouse: 26000 DPI high-precision sensor, RGB lighting, 11 programmable buttons, excellent for fast-paced games and advanced control scenarios. Price: RMB 349.",
    "Sony WH-1000XM5 noise-canceling headphones: flagship active noise cancellation, 30-hour battery life, multi-point connection, touch controls, and wear detection. 2-year warranty. Price: RMB 2699.",
    "Apple Magic Trackpad: precise glass surface, magnetic charging, works well with macOS and iPadOS, ideal for Mac users who want better productivity. Price: RMB 749.",
    "Anker 65W multi-port charger: USB-C and USB-A support, charges up to 4 devices, compatible with MacBook, iPad, and iPhone, excellent for travel. Price: RMB 199.",
    "Xiaomi smart desk lamp: low blue-light design, app-controlled brightness and color temperature, suitable for students and office workers. Price: RMB 99.",
    "Suntory sugar-free oolong tea (24 bottles): crisp taste, zero sugar, zero fat, zero calories, suitable for daily hydration. Price: RMB 79 per case.",
    "Suntory black oolong tea (30 packs): rich roasted flavor, often chosen for office use and heavy meals. Price: RMB 89 per case.",
    "Mengniu pure milk (24 cartons): high calcium, lower fat, suitable for families and students. Price: RMB 59 per case.",
    "C'estbon mineral water (12 bottles): refreshing hydration for everyday use. Price: RMB 39 per case.",
    "NFC orange juice 1L: 100% juice, no additives, cold-chain delivery. Price: RMB 14.9 per bottle.",
    "Uniqlo AIRism quick-dry T-shirt: breathable, moisture-wicking, suitable for summer daily wear. Price: RMB 79.",
    "Nike Flex Stride running shorts: lightweight and breathable, ideal for training and running. Price: RMB 199.",
    "Adidas Ultraboost 23 running shoes: strong cushioning and support for running and gym sessions. Price: RMB 799.",
    "Columbia outdoor shell jacket: waterproof, breathable, designed for hiking and trekking. Price: RMB 599.",
    "L'Oreal hyaluronic acid hydration mask: deep hydration for dry and combination skin. Price: RMB 29 each.",
    "Shiseido HADA LABO toner: strong hydration, suitable for most skin types. Price: RMB 89.",
    "LANEIGE sleeping mask: overnight hydration and repair, no-rinse formula. Price: RMB 149.",
    "Olay eye cream: helps reduce fine lines and brighten the eye area. Price: RMB 69.",
    "IKEA BILLY bookshelf: minimalist storage with good load capacity for compact homes. Price: RMB 299.",
    "Panasonic humidifier 4L: quiet operation, suitable for bedroom and office use. Price: RMB 349.",
    "Philips LED ceiling light 48W: energy-efficient with multiple color temperatures. Price: RMB 159.",
    "Midea electric kettle 1.7L: fast heating with boil-dry protection. Price: RMB 69.",
    "Python deep learning book: classic reference covering practical theory and implementation. Price: RMB 148.",
    "System design interview book: useful architecture guide for major tech interviews. Price: RMB 89.",
    "MySQL performance course: practical optimization and tuning lessons. Price: RMB 99.",
    "Decathlon 60L hiking backpack: large capacity, comfortable carry system, suitable for outdoor trips. Price: RMB 299.",
    "Black Diamond hiking boots: waterproof and supportive for mountain terrain. Price: RMB 999.",
    "Coleman 2-person tent: easy setup with water-resistant outdoor protection. Price: RMB 399.",
    "Royal Canin dog food 2kg: balanced nutrition for large-breed adult dogs. Price: RMB 129.",
    "Covered litter box with deodorizing litter set: sealed odor control and easy cleaning. Price: RMB 149.",
    "Petkit automatic feeder: scheduled feeding with mobile app control. Price: RMB 249."
]

def init_mock_vector_db():
    print("  -> [Vector DB] 1. 开始初始化本地商品知识库...")
    
    # 丰富的模拟商品数据库，覆盖多个品类、价格段、用途
    docs = [Document(page_content=text) for text in MOCK_PRODUCTS]
    
    print("  -> [Vector DB] 2. 准备初始化 Embeddings 对象...")
    embeddings = OpenAIEmbeddings(
        openai_api_base="https://api.siliconflow.cn/v1",
        openai_api_key=API_KEY,
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


def fallback_retrieve_products(query: str, k: int = 2):
    normalized = (query or "").lower()
    keyword_groups = {
        "headphones": ["headphone", "headset", "noise", "music", "call", "耳机", "降噪"],
        "keyboard": ["keyboard", "typing", "code", "macos", "键盘"],
        "mouse": ["mouse", "wireless mouse", "办公", "office", "鼠标"],
        "drink": ["drink", "tea", "water", "juice", "milk", "饮品", "乌龙茶", "果汁"],
        "outdoor": ["outdoor", "camp", "hiking", "tent", "露营", "户外", "登山"],
        "beauty": ["mask", "toner", "cream", "beauty", "护肤", "面膜", "爽肤水"],
        "pet": ["pet", "dog", "cat", "宠物", "狗粮", "猫"]
    }

    scores = []
    for product in MOCK_PRODUCTS:
        product_lower = product.lower()
        score = 0
        for keywords in keyword_groups.values():
            hits = sum(1 for keyword in keywords if keyword in normalized and keyword in product_lower)
            score += hits * 3
        for token in normalized.split():
            if len(token) > 2 and token in product_lower:
                score += 1
        scores.append((score, product))

    ranked = [item for item in sorted(scores, key=lambda x: x[0], reverse=True) if item[0] > 0]
    if ranked:
        best_score = ranked[0][0]
        threshold = max(1, best_score - 2)
        selected = [item for item in ranked if item[0] >= threshold][:k]
    else:
        selected = []
    return [Document(page_content=product) for _, product in selected]