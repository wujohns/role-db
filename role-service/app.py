# 启动一个基础的 web 服务
# import hashlib

# str = 'kmk'
# h = hashlib.md5()
# h.update(str.encode(encoding='utf-8'))

# print(h.hexdigest())
import hashlib
from langchain.docstore.document import Document

from utils import init_store, update_doc, search_similarity

content = '你好，你好哈哈，老哥，零零零零'
hash = hashlib.md5()
hash.update(content.encode(encoding='utf-8'))
hash = hash.hexdigest()

doc = Document(page_content=content, metadata={ 'hash': hash })
init_store()
update_doc('kkm', doc)

docs = search_similarity('kkm', '你好')
print(docs)
