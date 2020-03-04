import MySQLdb

class MySQL:
    def __init__(self,host,user,paswd,dbname,port):
        self.host =host
        self.dbname=dbname
        self.user =user
        self.paswd=paswd
        self.port=port
        self.client = None
    def ConnectDB(self):
        res =  False
        try:
            self.client = MySQLdb.Connect(self.host,self.user,self.paswd,self.dbname,self.port,charset='utf8')#charset='utf8' 必须指定
            res =True
        except Exception as e:
            print(f'数据库连接失败：{e}')
        finally:
            return res

    def ExecuteSql(self,sql):
        """执行sql语句"""
        results=[]
        self.cursordb = self.client.cursor()
        try:
            self.cursordb.execute(sql)
            # self.client.commit()
            # 获取所有记录列表
            results = self.cursordb.fetchall()
        except Exception as e:
            print(f'{sql}执行失败:{e}')
            self.client.rollback()
        finally:
            return results
