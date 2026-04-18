# OmniCart-AI



# 环境搭建

# 创建名为 .venv 的虚拟环境
python3 -m venv .venv

# 激活虚拟环境 (成功后终端提示符前会多出 (.venv))
source .venv/bin/activate

# 顺手升级一下 pip
pip install --upgrade pip

# 核心依赖
pip install langgraph langchain langchain-openai fastapi uvicorn chromadb pydantic langchain-community

export OPENAI_API_KEY=""