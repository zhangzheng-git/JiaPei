from tools.mysql import MySQL
from tools.mongo import Mongo
import time
from pyecharts.charts import Bar
from pyecharts import options as opts
import numpy as np
from pyecharts.globals import ThemeType
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
    #统计驾校列表
    for row in res:
        if row['SchoolCode'] not in school:
            school.append(row['SchoolCode'])
    for index in range(len(school)):
        # falge = False
        mg.ChangeCollection('excel')
        #根据驾校编号查询记录
        res = mg.FindAllData({"SchoolCode":school[index]},{'_id':False})
        data = {'SchoolCode':school[index]}
        for row in res:
            #数组形式
            datail={
                'sex':row['sex'],
                'age':row['age'],
                "CarType":row['CarType'],
                "State":row['State']
            }
            #插入新库
            mg.ChangeCollection(schooltable)
            # if not falge:
            #     # data.update(datail)
            #     # mg.InsertData(data)
            #     mg.UpdateData({'SchoolCode': school[index]}, {'$set': {'data': datail}}, True)
            #     # mg.UpdateData({'SchoolCode': school[index]}, {'$set': {'name':[{'host_id':'t1'}]}}, True)
            #     falge = True
            # else:
            mg.UpdateData({'SchoolCode':school[index]},{'$push':{'data':datail}},True)

def AgeDistrbution(mg,table):
    mg.ChangeCollection(table)
    res = mg.FindAllData({},{'SchoolCode':True,'data':True})
    AgeAry = []
    AgeDis = {}
    School =[]
    #全部数据
    for row in res:
        school = row['SchoolCode']
        #驾校维度
        res = mg.FindAllData({'SchoolCode':school},{'data':True})
        for row1 in res:
            # print(row['data'])
            #同一驾校所有学员年龄
            for indexs in range(len(row1['data'])):
                age = row1['data'][indexs]['age']
                AgeAry.append(age)
        #驾校和该驾校所有学员年纪的字典
        AgeDis={'SchoolCode':school,'age':AgeAry}
        print(AgeDis["age"])
        School.append(school)
    # --------------------------------------------
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.PURPLE_PASSION))
            .add_xaxis(School)
            # .add_yaxis("年龄", AgeAry)
            .add_yaxis("平均年龄",np.mean(np.array(AgeAry)) )
            .set_global_opts(title_opts=opts.TitleOpts(title="柱状图", subtitle="各驾校平均年龄"))
        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    bar.render('render.html')





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
    SchoolCode
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
    # AnalyAndUpdateData(mg,'excel')
    # mg.ChangeCollection('excel')
    # SchoolFiled(mg,'school')
    AgeDistrbution(mg,'school')




