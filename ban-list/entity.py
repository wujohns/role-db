# 模型测试相关
import os
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from seqeval.metrics.sequence_labeling import get_entities

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

os.environ["KMP_DUPLICATE_LIB_OK"] = 'TRUE'
model_path = getAbsPath('../hg-repos/models/bert4ner-base-chinese')
device = torch.device('cuda:0')

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
model = model.to(device)
model = model.eval()

label_list = ['I-ORG', 'B-LOC', 'O', 'B-ORG', 'I-LOC', 'I-PER', 'B-TIME', 'I-TIME', 'B-PER']

sentence = """
rainbow说: "建议看恶魔人"
Love陌兮说: "很遗憾 我玩ga大多都是冲血腥猎奇去的 不过还是更侧重剧情的 然后被euphoria整得有点电子阳痿 后劲太大了"
苏习羽说: "你要是看石头门，也必看凉宫春日的消失"
苏习羽说: "时间穿越题材的神"
契约者不会暴击1说: "恶魔人看完了"
契约者不会暴击1说: "人才是恶魔"
盒子鱼说: "说实话，最近看re0，觉得也挺好的"
契约者不会暴击1说: "美树串串香"
"""

def get_entity(sentence):
  tokens = tokenizer.tokenize(sentence)
  inputs = tokenizer.encode(sentence, return_tensors="pt")
  inputs = inputs.to(device)
  with torch.no_grad():
    outputs = model(inputs).logits
    outputs = outputs.to('cpu')
  predictions = torch.argmax(outputs, dim=2)
  print(outputs)
  char_tags = [(token, label_list[prediction]) for token, prediction in zip(tokens, predictions[0].numpy())][1:-1]
  print(sentence)
  print(char_tags)

  pred_labels = [i[1] for i in char_tags]
  entities = []
  line_entities = get_entities(pred_labels)
  for i in line_entities:
    word = sentence[i[1]:i[2] + 1]
    entity_type = i[0]
    entities.append((word, entity_type))

  print("Sentence entity:")
  print(entities)

get_entity(sentence)
