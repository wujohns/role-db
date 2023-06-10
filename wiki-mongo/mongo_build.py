# 将 wiki 的数据存储到 mongodb
import os
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
import bz2file
import re
import opencc
from tqdm import tqdm
from mongo import get_collection

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

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
# 备注：
# 1. 为了防止 mongodb 爆内存，可以采用分批写入，每次写入前都 restart mongod 清理缓存（或直接配置 mongodb 缓存策略）
# 2. 缓存策略配置参考：https://www.mongodb.com/docs/manual/reference/configuration-options/ 中的 storage.wiredTiger.engineConfig.cacheSizeGB 
# 3. 该部分的性能瓶颈主要为 python 的正则执行，可以考虑使用多线程进行优化（有多少核心就可以提高多少倍）
wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles1.xml-p1p187712.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles2.xml-p187713p630160.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles3.xml-p630161p1389648.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles4.xml-p1389649p2889648.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles4.xml-p2889649p3391029.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles5.xml-p3391030p4891029.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles5.xml-p4891030p5596379.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles6.xml-p5596380p7096379.bz2')
# wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles6.xml-p7096380p8387641.bz2')
wiki_pages = extract_pages(bz2file.open(wiki_path))

collection = get_collection()
cur_wiki_index = 0
wiki_list = tqdm(wiki_pages, desc=u'已获取0篇文章')
for wiki_doc in wiki_list:
  # 排除掉类型实体（图片等）
  if re.findall('^[a-zA-Z]+:', wiki_doc[0]):
    continue

  # if wiki_doc[0] and re.findall(u'^#', wiki_doc[1]):
  if wiki_doc[0]:
    # 解析并格式化 wiki 内容
    wiki_info = wiki_format(wiki_doc)
    title = wiki_info['title']
    content = wiki_info['content']
    abstract = wiki_info['abstract']

    if re.findall(u'^#(REDIRECT|重定向|重新导向)', content, re.IGNORECASE):
      redirect = re.sub(u'^#(REDIRECT|重定向|重新导向)', '', content, flags=re.IGNORECASE).strip()
      collection.find_one_and_update(
        { 'entityName': title },
        { '$set': { 'redirect': redirect } },
        upsert=True
      )
    else:
      collection.find_one_and_update(
        { 'entityName': title },
        { '$set': { 'entitySummary': abstract, 'entityContent': content } },
        upsert=True
      )

    # 进度计数
    cur_wiki_index += 1
    if cur_wiki_index % 500 == 0:
      wiki_list.set_description(u'已获取%s篇文章'%cur_wiki_index)

print('finish')
