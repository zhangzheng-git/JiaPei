import pymongo
from bson.objectid import ObjectId
class Mongo:
    def __init__(self, host, port, dbase=None, table=None,username=None, password=None,):
        try:
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            self.client = pymongo.MongoClient(host, port)
            self.dbase = self.client[dbase]
            self.table = self.dbase[table]
            self.collection = self.dbase.get_collection(table)
        except Exception as e:
            print(f"数据库初始化错误，错误原因：{e}")
            self.CloseConnect()
    def ChangeCollection(self, table):
        """切换表"""
        self.table = self.dbase[table]
        self.collection = self.dbase.get_collection(table)


    def InsertData(self, data):
        """插入数据"""
        ret = False
        try:
            self.collection.insert(data)
            ret = True
        except Exception as e:
            print(f"插入数据{data}出错,错误原因:{e}")
        finally:
            return ret

    def FindCount(self, talble, filter):
        """查找文档数量
        filter 过滤条件"""
        count = 0
        try:
            self.collection = self.dbase.get_collection(talble)
            count = self.collection.find(filter).count()
        except Exception as e:
            print(f"获取{self.table}表文档数量失败,错误原因:{e}")
        finally:
            return count

    def FindOneData(self, filter, ret):
        """返回ret指定格式的数据
        filter过滤条件"""
        retlist = {}
        try:
            retlist = self.collection.find_one(filter, ret)
        except Exception as e:
            print(f"查找{filter}失败,错误原因:{e}")
        finally:
            return retlist

    def FindAllData(self, filter, ret, limit=0, skip=0):
        """查找满足所有过滤条件的数据"""
        retlist = []
        try:
            if not limit:
                if not skip:
                    retlist = self.collection.find(filter, ret)
                else:
                    retlist = self.collection.find(filter, ret).skip(skip)
            else:
                if not skip:
                    retlist = self.collection.find(filter, ret).limit(limit)
                else:
                    retlist = self.collection.find(filter, ret).limit(limit).skip(skip)
        except Exception as e:
            print(f"查找{filter}文档失败,错误原因:{e}")
        finally:
            self.retlist = retlist
            return self.retlist

    def DelData(self, filter):
        """删除满足fiter条件的数据"""
        ret = False
        try:
            self.collection.remove(filter)
            ret = True
        except Exception as e:
            print(f"删除{filter}文档失败，错误原因：{e}")
        finally:
            return ret

    def UpdateData(self, filter, updata, upsert=False, multi=False):
        """更新文档"""
        ret = False
        try:
            self.collection.update(filter, updata, upsert, multi)
            ret = True
        except Exception as e:
            print(f"更新{filter}失败，错误原因：{e}")
        return ret

    def get(self,post_id):
        """字符串转换为ObjectId"""
        document = self.collection.find_one({'_id': ObjectId(post_id)})

    def SortData(self,filter=None,restr=None, sortrule=None):
        """排序
        filter 过滤条件
        restr 返回形式
        sortrule 格式{'average':1} 改 [('average',1)]"""
        ret =[]
        try:
            ret =  self.collection.find(filter,restr).sort(sortrule)
        except Exception as e:
            print(f"根据{filter}排序错误，错误原因：{e}")
        return ret

    def CloseConnect(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()