# 文件名: test_api.py
import requests

url = "https://api.siliconflow.cn/v1/embeddings"
headers = {
    "Authorization": "Bearer sk-dikkdnbuvkhmsvyoruibkhgdsobbvhbiaxlulopbrxziijwt", # 你的 Key
    "Content-Type": "application/json"
}
data = {
    "model": "BAAI/bge-m3",
    "input": ["测试一下网络连通性"]
}

print("正在发送请求到硅基流动 API...")
try:
    # 设置 10 秒超时
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"HTTP 状态码: {response.status_code}")
    print("返回内容缩略:", response.text[:200])
except Exception as e:
    print(f"请求失败，网络不通！具体原因: {e}")