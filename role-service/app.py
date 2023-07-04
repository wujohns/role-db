# 启动一个基础的 web 服务
import json
import consts
from utils import get_content_hash, init_store, update_doc, search_similarity
from quart import Quart, jsonify, request
from langchain.docstore.document import Document

app = Quart(__name__)

# 更新或添加向量数据
@app.route('/update', methods=['POST'])
async def update ():
  data_str = await request.data
  data = json.loads(data_str)
  
  db_name = data['dbName']
  content = data['content']
  hash = get_content_hash(content)
  doc = Document(page_content=content, metadata={ 'hash': hash })
  success = update_doc(db_name, doc)

  return jsonify({ 'success': success })

# 按照相似度搜索
@app.route('/search', methods=['POST'])
async def search ():
  data_str = await request.data
  data = json.loads(data_str)

  db_name = data['dbName']
  content = data['content']
  docs = search_similarity(db_name, content)
  if docs:
    return jsonify({ 'success': True, 'docs': docs })
  else:
    return jsonify({ 'success': False })

# 服务启动前的处理
@app.before_serving
def startup ():
  print('init db')
  init_store()

# 服务关闭时的处理
@app.after_serving
def shutdown ():
  print('close server')

# 服务启动
if __name__ == '__main__':
  # 启动 web 服务
  print('start develop web server')
  app.run(
    host=consts.host,
    port=consts.port,
    debug=consts.debug
  )
