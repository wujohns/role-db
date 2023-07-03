import os

curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# embedding 模型地址
embedding_model_path = getAbsPath('../hg-repos/embedding-models/all-MiniLM-L6-v2')

# 服务器配置
host = '0.0.0.0'
port = 6000
debug = True
