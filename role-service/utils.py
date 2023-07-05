# 相关工具方法封装
import os
import chromadb
import hashlib
from consts import embeddings
from langchain.vectorstores import Chroma
import traceback
from globals import dbMap

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# 获取文本 hash
def get_content_hash (content):
  hash = hashlib.md5()
  hash.update(content.encode(encoding='utf-8'))
  hash = hash.hexdigest()
  return hash

# 初始化向量数据库
def init_store ():
  global dbMap

  # 判断关键目录是否存在
  dbDirPath = getAbsPath('./db')
  if not os.path.exists(dbDirPath):
    os.makedirs(dbDirPath)

  # 读取已有的向量数据库
  dbDirFileList = os.listdir(dbDirPath)
  for item in dbDirFileList:
    itemPath = os.path.join(dbDirPath, item)
    if os.path.isdir(itemPath):
      dbMap[item] = Chroma(
        collection_name=f'{ item }_store',
        embedding_function=embeddings,
        client_settings=chromadb.config.Settings(
          chroma_db_impl="duckdb+parquet",
          persist_directory=itemPath,
          anonymized_telemetry=False
        ),
        persist_directory=itemPath
      )

# 添加或修改实体信息
def update_doc (dbName, doc):
  global dbMap
  dbPath = getAbsPath(f'./db/{ dbName }')
  metadata = doc.metadata
  hash = metadata['hash']

  # 检查 dbMap 是否存在对应的 db
  if (not dbName in dbMap):
    dbMap[dbName] = Chroma(
      collection_name=f'{ dbName }_store',
      embedding_function=embeddings,
      client_settings=chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=dbPath,
        anonymized_telemetry=False
      ),
      persist_directory=dbPath
    )

  # chroma 基于的 duckdb 安全性不够，可能出现未知错误导致中断
  vectorstore = dbMap[dbName]
  try:
    cur_docs = vectorstore._collection.get(
      where={ 'hash': hash }
    )
    cur_docs_ids = cur_docs['ids']
    print(cur_docs_ids)
    if len(cur_docs_ids) > 0:
      # 当前 doc 存在
      doc_id = cur_docs_ids[0]
      # vectorstore.update_document(document_id=doc_id, document=doc)
    else:
      # 当前 doc 不存在
      vectorstore.add_documents(documents=[doc], embeddings=embeddings)
    vectorstore.persist()
    return True
  except Exception as e:
    print('vectordb 操作发生错误:')
    traceback.print_exc()
    return False

# 直接按相似度搜索文档
def search_similarity (dbName, content):
  global dbMap

  # 对应的 db 不存在
  if (not dbName in dbMap):
    return False

  # db 存在则进行相似度搜索
  vectorstore = dbMap[dbName]
  oriDocs = vectorstore.similarity_search_with_score(content, k=4)

  # 格式整理
  docs = []
  for oriDoc in oriDocs:
    page_content = oriDoc[0].page_content
    hash = oriDocs[0][0].metadata['hash']
    docs.append({
      'content': page_content,
      'hash': hash
    })
  return docs

# 获取 db 条目总数
def count_docs (dbName):
  global dbMap

  # 对应的 db 不存在
  if (not dbName in dbMap):
    return False

  vectorstore = dbMap[dbName]
  num = vectorstore._collection.count()
  return num
