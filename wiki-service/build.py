# 构建本地 wiki 数据库
import os
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
import bz2file
import re
import opencc
from tqdm import tqdm
from langchain.docstore.document import Document
from store import init_store, update_doc
import globals

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# 初始化向量db
init_store(True)

# wiki 内容解析
converter = opencc.OpenCC('t2s.json')
def wiki_format(doc):
  # 标题
  title = doc[0]

  # 主要文本内容
  s = doc[1]
  s = re.sub(':*{\|[\s\S]*?\|}', '', s)
  s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
  s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
  s = filter_wiki(s)
  s = re.sub('\* *\n|\'{2,}', '', s)
  s = re.sub('\n+', '\n', s)
  s = re.sub('\n[:;]|\n +', '\n', s)
  s = re.sub('\n==', '\n\n==', s)

  # 摘要抽取
  abstract_match = re.search(re.escape(title) + '[\s\S]*?\n==', s)
  abstract = ''
  if (abstract_match):
    abstract = abstract_match.group()
    abstract = re.sub('\n==', '', abstract)
    abstract = converter.convert(abstract).strip()

  return {
    'title': converter.convert(title).strip(),
    'content': converter.convert(s).strip(),
    'abstract': abstract
  }

# 读取 wiki 内容并进行处理
wiki_path = getAbsPath('../zhwiki-latest-pages-articles.xml.bz2')
wiki_pages = extract_pages(bz2file.open(wiki_path))

cur_wiki_index = 0
wiki_list = tqdm(wiki_pages, desc=u'已获取0篇文章')
for wiki_doc in wiki_list:
  # 相比于参考案例中保留英文 entity
  # if not re.findall('^[a-zA-Z]+:', wiki_doc[0]) and wiki_doc[0] and not re.findall(u'^#', wiki_doc[1]):
  if wiki_doc[0] and not re.findall(u'^#', wiki_doc[1]):
    # 解析并格式化 wiki 内容
    wiki_info = wiki_format(wiki_doc)
    title = wiki_info['title']
    content = wiki_info['content']
    abstract = wiki_info['abstract']

    # 保存 wiki 信息
    entity_name_doc = Document(page_content=title, metadata={ 'entity_name': title })
    entity_abstract_doc = Document(page_content=abstract, metadata={ 'entity_name': title })
    update_doc(globals.entity_name_store, entity_name_doc)
    update_doc(globals.entity_abstract_store, entity_abstract_doc)

    # 进度计数
    cur_wiki_index += 1
    if cur_wiki_index % 100 == 0:
      wiki_list.set_description(u'已获取%s篇文章'%cur_wiki_index)
