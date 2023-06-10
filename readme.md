# role-db
角色数据库

## 前言
角色数据库主要为提供角色的描述的信息，或作为角色的知识点的补充，其中潜在的解决该部分的方案有:  
1. 实体抽取/知识图谱  
1. 向量数据库  

备注：
1. 在进行诸多尝试后，可行方案的实现已经由其他工程处理，本工程只作为一个思路的记录  

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
1. wiki 的本地化中使用 chroma 的方案 - chromadb 的写入性能太差，完成 wiki 的导入需要以百天的时间，在工程实践中得不偿失  

备注:  
1. nlp 领域参数量小于 3b 的模型是工程陷阱(解决特定领域的处理时完全可以被普通db以及通用的相似度查询处理，基本没有泛用特性)  
1. 失败的尝试放入到 ban-list 中  

### 虽然可行但是工程性能太差的方向
1. 使用 langchain 中的 Wikipedia loader 作为数据来源(实体数据信息): https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/wikipedia.html  

备注：  
1. wiki 官方虽然提供了便捷的接口，但是改接口的查询速度较慢，且有频率限制  
1. 这里推荐改用将 wiki 数据存储到本地数据库然后对实体名称做向量化查询的方案  

### 已确认可进行工程化实施的方向
1. wiki 本地化并配合 mongodb
1. llm(newbing, gpt3.5) 处理实体提取和内容汇总(效果极好)  

备注：
1. 可以参考 [维基百科数据本地化](/docs/维基百科数据本地化.md)
1. wiki 接口方式获取的数据较为规范，但是其 summary 信息不一定准确，可以考虑额外使用 llm 做 summary 辅助  
1. wiki 中获取的内容可能为繁体，可以使用繁转简方案处理：https://pypi.org/project/opencc-python  
1. wiki 在 mongodb 中的资源占用汇总:  
```
总实例数 236,3237
dataSize(数据库中的数据大小): 3.2g
storageSize(数据库中存储的数据的物理大小): 1.97g
indexSize(索引的总大小): 165m
totalSize(数据库的总体大小): 2.13g

建议: 
1. 对于中文 wiki 内容，至少为 mongo 留足 4g 以上内存作为缓存空间  
1. mongodb 缓存大小规则与配置可以参考：https://www.mongodb.com/docs/manual/reference/configuration-options/ 中的 storage.wiredTiger.engineConfig.cacheSizeGB  
1. 对于之后的英文 wiki 内容，则至少需要留足 40g 以上内存作为缓存空间  

一些延申问题: 
1. 单体大服务模式在未来的机器配置日益增加的背景下，将是工程上更适合的选择  
1. wiki 的资源消耗远远低于预期  
```

### 待确认的点
1. 知乎数据集(需要依据实际业务方向做定向筛选清洗): https://huggingface.co/datasets/wangrui6/Zhihu-KOL  
1. 知识图谱存储方案：https://zhuanlan.zhihu.com/p/83893713  
1. 采用 lora + chatglm 的模式进行训练可能比传统方式要更好  

wiki 的数据也有打包下载的方式，可以参考这个站点：https://dumps.wikimedia.org/zhwiki/latest/
对其相关数据的解析可以参考：https://cloud.tencent.com/developer/article/1564349

### memory 组织方式
目前先采用将实体名称喂给 chroma 辅助信息查询，但是否有必要投喂 entity 摘要有待商榷  
1. langchain - chroma: https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html  

## 相关策略汇总
1. 使用成熟的 llm 进行业务支撑，并同时收集语料  
1. 后续再尝试使用 lora + chatglm 基于已经收集的语料训练模型  
1. 基本可以抛弃小参数模型(虽然资源消耗少，但依赖更多的人力以及在工程特性上效果太差，兜底也是需要采用 chatglm-6b + lora 的方案)  

