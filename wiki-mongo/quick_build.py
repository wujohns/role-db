# 将 wiki 的数据存储到 mongodb
# 多进程优化版
import os
from multiprocessing import Pool
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
import bz2file
import re
import opencc
from tqdm import tqdm
from mongo import get_collection

# 进程数
process_num = 10

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
  # 排除掉类型实体（图片等）
  if not doc[0] or re.findall('^[a-zA-Z]+:', doc[0]):
    return False

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

  # 信息汇总
  title = converter.convert(title).strip()
  content = converter.convert(s).strip()

  # 确认是否是重定向
  update = { '$set': { 'entitySummary': abstract, 'entityContent': content } }
  if re.findall(u'^#(REDIRECT|重定向|重新导向)', content, re.IGNORECASE):
    redirect = re.sub(u'^#(REDIRECT|重定向|重新导向)', '', content, flags=re.IGNORECASE).strip()
    update = { '$set': { 'redirect': redirect } }

  return {
    'title': title,
    'update': update
  }

wiki_path = getAbsPath('../wiki-dump/zhwiki-latest-pages-articles.xml.bz2')
wiki_pages = extract_pages(bz2file.open(wiki_path))

collection = get_collection()
cur_wiki_index = 0

# 创建进程池
pool = Pool(process_num)

# 提交任务到进程池
results = pool.imap_unordered(wiki_format, wiki_pages)
result_list = tqdm(results, desc=u'已完成0个task, 有效记录0个')
finished_index = 0
valid_index = 0
for result in result_list:
  finished_index += 1
  if result:
    valid_index += 1
    collection.find_one_and_update(
      { 'entityName': result['title'] },
      result['update'], upsert=True
    )

  if valid_index % 500 == 0:
    result_list.set_description(f'已完成{ finished_index }个task, 有效记录{ valid_index }个') 
