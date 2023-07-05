# 自定义的 embedding 封装
import os
import torch
from typing import List, Any
from pydantic import BaseModel, Extra
from langchain.embeddings.base import Embeddings
from argparse import Namespace
from transformers import AutoModel, AutoTokenizer

curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

# luotuo_bert 模型相关
device = torch.device('cuda:0')
luotuo_bert_model_path = getAbsPath('../hg-repos/embedding-models/luotuo-bert')
luotuo_bert_tokenizer = AutoTokenizer.from_pretrained(luotuo_bert_model_path)
luotuo_bert_model_args = Namespace(
  do_mlm=None, pooler_type="cls", temp=0.05,
  mlp_only_train=False, init_embeddings_model=None
)
luotuo_bert_model = AutoModel.from_pretrained(
  luotuo_bert_model_path,
  trust_remote_code=True,
  model_args=luotuo_bert_model_args
)
luotuo_bert_model = luotuo_bert_model.to(device)
luotuo_bert_model.eval()

# 使用 luotuo-bert 来做 embedding 的支持
class LuotuoBertEmbeddings(BaseModel, Embeddings):
  def __init__(self, **kwargs: Any):
    super().__init__(**kwargs)

  class Config:
    """Configuration for this pydantic object."""
    extra = Extra.forbid

  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    texts = [text[:512] for text in texts]
    inputs = luotuo_bert_tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    inputs = inputs.to(device)
    with torch.no_grad():
      embeddings = luotuo_bert_model(**inputs, output_hidden_states=True, return_dict=True, sent_emb=True).pooler_output
    return embeddings.tolist()

  def embed_query(self, text: str) -> List[float]:
    text = text[:512]
    texts = [text]
    inputs = luotuo_bert_tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    inputs = inputs.to(device)
    with torch.no_grad():
      embeddings = luotuo_bert_model(**inputs, output_hidden_states=True, return_dict=True, sent_emb=True).pooler_output
    return embeddings.tolist()[0]
