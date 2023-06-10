# mongo 相关方法封装
from pymongo import MongoClient

# mongo 连接配置
# 192.168.101.216
username = 'common-data'
password = 'data-pwd-123'
host = '192.168.101.216'
port = 27017
authentication_database = 'common-data'
database_name = 'common-data'
collection_name = 'wikientities'

connection_string = f"mongodb://{username}:{password}@{host}:{port}/?authSource={authentication_database}"

# collection 需要小写
# collection = db['wikientities']
# result = collection.find_one({ 'username': '空白易逝' })
# print(result)

def get_collection ():
  client = MongoClient(connection_string)
  db = client[database_name]
  collection = db[collection_name]
  return collection
