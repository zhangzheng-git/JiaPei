import MySQLdb

# class MySQL:
#     def __init__(self,host,user,paswd,dbname,port):
#         self.host =host
#         self.dbname=dbname
#         self.user =user
#         self.paswd=paswd
#         self.port=port
#         self.client = None
#     def ConnectDB(self):
#         res =  False
#         try:
#             self.client = MySQLdb.Connect(self.host,self.user,self.paswd,self.dbname,self.port,charset='utf8')#charset='utf8' 必须指定
#             res =True
#         except Exception as e:
#             print(f'数据库连接失败：{e}')
#         finally:
#             return res
#
#     def ExecuteSql(self,sql):
#         """执行sql语句"""
#         results=[]
#         self.cursordb = self.client.cursor()
#         try:
#             self.cursordb.execute(sql)
#             # self.client.commit()
#             # 获取所有记录列表
#             results = self.cursordb.fetchall()
#         except Exception as e:
#             print(f'{sql}执行失败:{e}')
#             self.client.rollback()
#         finally:
#             return results



class MySQL:
    def ConnectDB(self,host,user,paswd,dbname,port):
        res =  False
        try:
            self.client = MySQLdb.Connect(host,user,paswd,dbname,port,charset='utf8')#charset='utf8' 必须指定
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
            self.client.commit()
            # 获取所有记录列表
            # results = self.cursordb.fetchall()
        except Exception as e:
            print(f'{sql}执行失败:{e}')
            self.client.rollback()
        finally:
            return results
#
# mysql = MySQL()
# mysql.ConnectDB('127.0.0.1','root','123qwe','myemployees',3306)
# re =  mysql.ExecuteSql("""SELECT LENGTH(last_name) 长度,SUBSTR(last_name,1,1)
# 首字符,last_name FROM employees ORDER BY
# 首字符;""")
# for row in re:
#     print(row)
Sim = 0
mysql = MySQL()
mysql.ConnectDB('10.50.50.82', 'root', 'wk-net', 'haoxueche', 3306)
for i in range(2,2002):
    Sim = str(16000000001+i)
    print('sim',Sim)

    re = mysql.ExecuteSql(f"""INSERT INTO `haoxueche`.`ds_devicetest1`
            (`Id`,
             `DeviceId`,
             `State`,
             `Sim`,
             `CarNo`,
             `SchoolCode`,
             `SchoolUnifyCode`,
             `DeviceUnifyCode`,
             `DeviceKey`,
             `DevicePwd`,
             `DeviceType`)
VALUES ({i},
        {i},
        1,
        {Sim},
        '川E3985学',
        510500095,
        '6652336654464232',
        '3845107175430145',
        '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',
        'GgSiLEtTNDS2',
        1);""")
