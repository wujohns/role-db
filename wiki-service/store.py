# chromadb 相关方法封装
import os
import chromadb
import shutil
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import globals

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# embeddings 处理方法
# 也可以考虑使用其他的 embedding 方法
embeddings = HuggingFaceEmbeddings(
  model_name=getAbsPath('../hg-repos/embedding-models/all-MiniLM-L6-v2')
)

# 初始化存储
def init_store (clear=False):
  DB_DIR = getAbsPath('db')
  if os.path.exists(DB_DIR) and clear:
    shutil.rmtree(DB_DIR)

  # 存储 entityName 的 store
  entity_name_path = getAbsPath('db/entity_name')
  globals.entity_name_store = Chroma(
    collection_name="entity_name_store",
    embedding_function=embeddings,
    client_settings=chromadb.config.Settings(
      chroma_db_impl="duckdb+parquet",
      persist_directory=entity_name_path,
      anonymized_telemetry=False
    ),
    persist_directory=entity_name_path
  )

  # 存储 entityAbastract 的 store
  entity_abstract_path = getAbsPath('db/entity_abstract')
  globals.entity_abstract_store = Chroma(
    collection_name="entity_abstract_store",
    embedding_function=embeddings,
    client_settings=chromadb.config.Settings(
      chroma_db_impl="duckdb+parquet",
      persist_directory=entity_abstract_path,
      anonymized_telemetry=False
    ),
    persist_directory=entity_abstract_path
  )

  # TODO entityContent 的 store 部分放在后续再做处理

# 添加或修改实体信息
def update_doc (vectorstore: Chroma, doc):
  metadata = doc.metadata
  entity_name = metadata['entity_name']

  # 查询对应的 doc 是否存在
  cur_docs = vectorstore._collection.get(
    where={ 'entity_name': entity_name }
  )
  cur_docs_ids = cur_docs['ids']
  if len(cur_docs_ids) > 0:
    # 当前 doc 存在
    doc_id = cur_docs_ids[0]
    vectorstore.update_document(document_id=doc_id, document=doc)
  else:
    # 当前 doc 不存在
    vectorstore.add_documents(documents=[doc], embeddings=embeddings)

# 先搜索相似的实例名，再准确搜索 abstract
def search_abstract (entity_name):
  # 先直接按关键字匹配搜索
  entity_abstract_info = globals.entity_abstract_store._collection.get(
    where={ 'entity_name': entity_name }
  )
  if len(entity_abstract_info['ids']) > 0:
    return {
      'search_name': entity_name,
      'abstract': entity_abstract_info['documents'][0]
    }

  # 没有匹配的则搜索相似的实例名
  entity_name_docs = globals.entity_name_store.similarity_search_with_score(entity_name, k=4)
  similar_name = entity_name_docs[0][0].page_content
  entity_abstract_info = globals.entity_abstract_store._collection.get(
    where={ 'entity_name': similar_name }
  )
  if len(entity_abstract_info['ids']) > 0:
    return {
      'search_name': similar_name,
      'abstract': entity_abstract_info['documents'][0]
    }

  return False

# 直接按相似度搜索 abstract
def search_abstract_similarity (entity_name):
  entity_abstract_docs = globals.entity_abstract_store.similarity_search_with_score(entity_name, k=4)
  return {
    'search_name': entity_abstract_docs[0][0].metadata['entity_name'],
    'abstract': entity_abstract_docs[0][0].page_content
  }
