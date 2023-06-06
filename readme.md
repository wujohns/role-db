# role-db
角色数据库

## 前言
角色数据库主要为提供角色的描述的信息，或作为角色的知识点的补充，其中潜在的解决该部分的方案有:  
1. 实体抽取/知识图谱  
1. 向量数据库  

## 当前需要参考的内容
### 已经确认失败的方向
1. 萌娘百科 datasets(尝试解析 - 数据格式混乱): https://huggingface.co/datasets/milashkaarshif/MoeGirlPedia_wikitext_raw_archive  
1. langchain 中的 webloader - 对于前后端分离的站点无法支持: https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/web_base.html  
1. langchain 中的 bilibililoader - 爬取的信息缺失严重：https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/bilibili.html  
1. baiduspider - 接口失效: https://github.com/BaiduSpider/BaiduSpider  
1. 通过直接从群聊对话中获取实体摘要 - 由于知识缺乏准确度，会严重受模型幻觉影响  
1. 直接使用开源小模型来做实体提取(shibing624/bert4ner-base-chinese) - 对群聊中的实体提取效果极差，需要额外训练且其训练需要的自定义数据集较为繁琐  
1. https://huggingface.co/IDEA-CCNL/Randeng-T5-77M-MultiTask-Chinese 在做 summary 时的效果也极差  
1. 直接从用户在群聊的零散信息对话中获取实体摘要(相当于在群聊中学习) - 1v1 的对话模式学习效果不错，但是群聊场景由于发言较为发散，实体摘要效果很差  

备注:  
1. nlp 领域参数量小于 3b 的模型是工程陷阱(解决特定领域的处理时完全可以被普通db以及通用的相似度查询处理，基本没有泛用特性)  
1. 失败的尝试放入到 ban-list 中  

### 已确认可行的方向
1. 使用 langchain 中的 Wikipedia loader 作为数据来源(实体数据信息): https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/wikipedia.html  
1. llm(newbing, gpt3.5) 处理实体提取和内容汇总(效果极好)  

备注：
1. wiki 接口方式获取的数据较为规范，但是其 summary 信息不一定准确，需要额外使用 llm 做 summary 辅助  
1. wiki 中获取的内容可能为繁体，可以使用繁转简方案处理：https://pypi.org/project/opencc-python  

### 待确认的点
1. 知乎数据集(需要依据实际业务方向做定向筛选清洗): https://huggingface.co/datasets/wangrui6/Zhihu-KOL  
1. 知识图谱存储方案：https://zhuanlan.zhihu.com/p/83893713  
1. 采用 lora + chatglm 的模式进行训练可能比传统方式要更好  

### memory 组织方式
将摘要喂给 chroma ?
1. langchain - chroma: https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html  

备注：
1. 向量数据库当前存在无法去重的问题，这里需要对其进行酌情处理  

## 相关策略汇总
1. 使用成熟的 llm 进行业务支撑，并同时收集语料  
1. 后续再尝试使用 lora + chatglm 基于已经收集的语料训练模型  
1. 基本可以抛弃小参数模型(虽然资源消耗少，但依赖更多的人力以及在工程特性上效果太差，兜底也是需要采用 chatglm-6b + lora 的方案)  
