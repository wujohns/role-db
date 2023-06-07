import os
from gensim.corpora.wikicorpus import extract_pages,filter_wiki
import bz2file
import re
import opencc
from tqdm import tqdm
import codecs

converter = opencc.OpenCC('t2s.json')
def wiki_replace(d):
  # 文本格式化解析
  s = d[1]
  s = re.sub(':*{\|[\s\S]*?\|}', '', s)
  s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
  s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
  s = filter_wiki(s)
  s = re.sub('\* *\n|\'{2,}', '', s)
  s = re.sub('\n+', '\n', s)
  s = re.sub('\n[:;]|\n +', '\n', s)
  s = re.sub('\n==', '\n\n==', s)

  # 标题
  title = d[0]

  # 摘要抽取
  abstract_match = re.search(title + '[\s\S]*?\n==', s)
  abstract = ''
  if (abstract_match):
    abstract = abstract_match.group()
    abstract = re.sub('\n==', '', abstract)
    abstract = converter.convert(abstract).strip()

  # 标题部分
  s = u'【' + d[0] + u'】\n' + s
  return converter.convert(s).strip()

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# wiki xml 压缩文件路径
wiki_path = getAbsPath('./zhwiki-latest-pages-articles.xml.bz2')
wiki = extract_pages(bz2file.open(wiki_path))

i = 0
f = codecs.open('wiki.txt', 'w', encoding='utf-8')
w = tqdm(wiki, desc=u'已获取0篇文章')
for d in w:
  if not re.findall('^[a-zA-Z]+:', d[0]) and d[0] and not re.findall(u'^#', d[1]):
    s = wiki_replace(d)
    f.write(s+'\n\n\n')
    i += 1
    if i % 100 == 0:
      w.set_description(u'已获取%s篇文章'%i)

f.close()
