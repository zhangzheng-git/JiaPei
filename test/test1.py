from tools.mysql import MySQL
from tools.mongo import Mongo
import time
from pyecharts.charts import Bar
from pyecharts import options as opts

results=[]

def SysMysqltable(host,user,passwd,dbname,port):
    """同步mysql数据"""
    mydb = MySQL('10.50.50.82','root','wk-net','haoxueche',3306)
    mydb.ConnectDB()
    # 去掉不合法身份证号
    global results
    results = mydb.ExecuteSql("SELECT IdNumber,SchoolCode, CarType, State FROM ds_student where IdNumber REGEXP '[0-9]{18}|[0-9]{17}X'")
    print(len(results))

def ConnectMongo(host,port,dbase,table):
    #连接mongodb
    mg = Mongo(host,port,dbase,table)
    return mg

def InsertMongo(mg):
    #将需要统计数据存入mongodb
    global results
    for row in results:
        # print(row)
        data={
            "IdNumber":row[0],
            "SchoolCode":row[1],
            "CarType":row[2],
            "State":row[3]
        }
        mg.InsertData(data)
    size = mg.FindCount("data",{})
    print(size)

def SchoolFiled(mg,schooltable):
    res = mg.FindAllData({}, {'_id': False})
    school=[]
    for row in res['SchoolCode']:
        if row not in school:
            school.append(row)
    for index in range(len(school)):
        res = mg.FindAllData({"SchoolCode":school[index]},{'_id':False})
        data = {'SchoolCode':school[index]}
        for row in res:
            datail={
                'data':[{'sex':sex,
                'age':age,
                "CarType":row['CarType'],
                "State":row['State']}]
            }
            data.update(datail)






def AnalyAndUpdateData(mg,newtable):
    #当前时间 用于后面计算年龄
    LocalTime = time.localtime(time.time())
    res = mg.FindAllData({},{'_id':False})
    #切换集合 将统计结果存储
    mg.ChangeCollection(newtable)
    for row in res:
        # print(row)
        if not row['IdNumber']:
            continue
        else:
            StrId = row['IdNumber']
            if not int(StrId[16])%2:
                sex = '女'
            else:
                sex = '男'
        AgeFile = StrId[6:10]
        age = LocalTime.tm_year-int(AgeFile)
        data = {
            'sex':sex,
            'age':age,
            "SchoolCode": row['SchoolCode'],
            "CarType":row['CarType'],
            "State":row['State']
        }
        mg.InsertData(data)


def TotalMWChart(mg,newtable):
    mg.ChangeCollection(newtable)
    #统计男女数量
    Man = mg.FindCount(newtable,{'sex':'男'})
    Women = mg.FindCount(newtable,{'sex':'女'})
    # 性别分布
    bar = (
        Bar()
            .add_xaxis(["男", "女"])
            .add_yaxis("性别", [Man, Women])
            .set_global_opts(title_opts=opts.TitleOpts(title="某驾校学员性别统计情况"))
    )
    bar.render('sexchart.html')

def AgeLevelChart(mg,newtable):
    mg.ChangeCollection(newtable)
    #年龄统计
    res = mg.FindAllData({},{'_id':False,'age':True})
    AgeAry = []
    for i in res:
        AgeAry.append(i['age'])
    AgeAry.sort()

    #年龄与其对应的个数字典
    AgeDrc={}
    for item in AgeAry:
        size = AgeAry.count(item)
        data = {item:size}
        # print(data)
        AgeDrc.update(data)
    print(len(AgeDrc))

    #年龄个数统计
    AgeCount=[]
    Age=[]
    for key in AgeDrc.keys():
        # print(key,AgeDrc[key])
        AgeCount.append(AgeDrc[key])
        Age.append(key)
    # 年龄分布
    bar = (
        Bar()
            .add_xaxis(Age)
            .add_yaxis("年龄", AgeCount)
            .set_global_opts(title_opts=opts.TitleOpts(title="某驾校学员年龄统计情况"))
    )
    bar.render('agechart.html')

if __name__ == '__main__':
    mg = ConnectMongo("127.0.0.1",27017,"jiapei",'data')
    AgeLevelChart(mg,'excle')



