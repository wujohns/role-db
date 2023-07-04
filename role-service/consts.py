import os
from env import openai_key, openai_proxy
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# embedding 模型地址
# 目前有三个选型
# 1. all-MiniLM-L6-v2: langchain 默认采用的相似度查询模型
# 2. paraphrase-multilingual-MiniLM-L12-v2: huggingface 推出的多语言相似度查询模型
# 3. luotuo-bert: 李鲁鲁团队训练的中文相似度查询模型(这个需要单独修改代码结构，需要进行额外的代码解析编写工作)
# embeddings = HuggingFaceEmbeddings(model_name=getAbsPath('../hg-repos/embedding-models/paraphrase-multilingual-MiniLM-L12-v2'))
embeddings = HuggingFaceEmbeddings(model_name=getAbsPath('../hg-repos/embedding-models/all-MiniLM-L6-v2'))

# openai 暂时被限制使用，这里需要考虑使用其他方法进行处理
# embeddings = OpenAIEmbeddings(
#   openai_api_key=openai_key,
#   openai_proxy=openai_proxy
# )

# 参考 https://docs.trychroma.com/embeddings 尝试编写自定义 embedding

# 服务器配置
host = '0.0.0.0'
port = 6000
debug = True
