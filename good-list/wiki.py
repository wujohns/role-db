import os
from langchain.document_loaders import WikipediaLoader

# # 绝对路径获取方法
# curPath = os.path.dirname(os.path.abspath(__file__))
# def getAbsPath (relativePath):
#   joinPath = os.path.join(curPath, relativePath)
#   return os.path.normpath(
#     os.path.abspath(joinPath)
#   )

# # 代理配置
os.environ['http_proxy'] = 'http://192.168.101.216:7890'
os.environ['https_proxy'] = 'http://192.168.101.216:7890'

docs = WikipediaLoader(query='辉夜大小姐', lang='zh', load_max_docs=1).load()
for doc in docs:
  print('-----------------------------------------')
  print(doc.page_content)
  print('-----------------------------------------aaa')
  print(doc.metadata.get('summary'))

import wikipedia
import opencc

# wikipedia.set_lang('zh')
# kk = wikipedia.search(query='恶魔人', results=2, suggestion=False)
# print(kk)
# try:
#   kk = wikipedia.summary('恶魔人')
#   print('-----------------------------------------')
#   print(kk)

#   converter = opencc.OpenCC('t2s.json')
#   print('-----------------------------------------')
#   kkk = converter.convert(kk)
#   print(kkk)
# except Exception as e:
#   print('发生异常: ', str(e))

from langchain.chains.summarize import load_summarize_chain
