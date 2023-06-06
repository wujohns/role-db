# 测试私有模型的汇总处理
import os
import torch
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration

# 绝对路径获取方法
curPath = os.path.dirname(os.path.abspath(__file__))
def getAbsPath (relativePath):
  joinPath = os.path.join(curPath, relativePath)
  return os.path.normpath(
    os.path.abspath(joinPath)
  )

model_path = getAbsPath('../hg-repos/models/Randeng-T5-77M-MultiTask-Chinese')
device = torch.device('cuda:0')

special_tokens = ["<extra_id_{}>".format(i) for i in range(100)]
tokenizer = T5Tokenizer.from_pretrained(
  pretrained_model_name_or_path=model_path,
  do_lower_case=True,
  max_length=512,
  truncation=True,
  additional_special_tokens=special_tokens
)
model = T5ForConditionalGeneration.from_pretrained(
  pretrained_model_name_or_path=model_path
)
model.resize_token_embeddings(len(tokenizer))
model.eval()

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
text = "实体识别任务：找出【" + sentence + "】这篇文章中所有实体？"
encode_dict = tokenizer(text, max_length=512, padding='max_length',truncation=True)

inputs = {
  "input_ids": torch.tensor([encode_dict['input_ids']]).long(),
  "attention_mask": torch.tensor([encode_dict['attention_mask']]).long(),
}

logits = model.generate(
  input_ids = inputs['input_ids'],
  max_length=100, 
  early_stopping=True,
)

logits=logits[:,1:]
predict_label = [tokenizer.decode(i,skip_special_tokens=True) for i in logits]
print(predict_label)
