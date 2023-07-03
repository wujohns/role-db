import os

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
# 3. luotuo-bert: 李鲁鲁团队训练的中文相似度查询模型
embedding_model_path = getAbsPath('../hg-repos/embedding-models/luotuo-bert')

# 服务器配置
host = '0.0.0.0'
port = 6000
debug = True
