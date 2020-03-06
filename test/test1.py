from tools.mysql import MySQL
from tools.mongo import Mongo
import time
from pyecharts.charts import Bar
from pyecharts import options as opts
import numpy as np
from pyecharts.globals import ThemeType
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
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
    """驾校维度插入数据"""
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
    """驾校维度"""
    mg.ChangeCollection(table)
    res = mg.FindAllData({},{'SchoolCode':True,'data':True})
    AgeAry = []
    AgeDis = {}
    School =[]
    Average=[]
    AgeMaxNp = []
    #全部数据
    for row in res:
        school = row['SchoolCode']
        School.append(school)
        #驾校维度
        res = mg.FindAllData({'SchoolCode':school},{'data':True})
        for row1 in res:
            #同一驾校所有学员年龄
            for indexs in range(len(row1['data'])):
                age = row1['data'][indexs]['age']
                AgeAry.append(age)
        #驾校和该驾校所有学员年纪的字典
        AgeDis={'SchoolCode':school,'age':AgeAry}
        # print(AgeDis["age"])
        #平均年龄
        AgeAverag = np.mean(np.array(AgeAry))
        AgeAverag = np.around(AgeAverag, decimals=1)
        #最大年龄 numpy数组计算效率快
        AgeMax = np.array(AgeAry).max()
        # AgeMax = max(AgeAry)
        AgeAry.clear()
        Average.append(AgeAverag)
        #要先AgeMax转为python内置数组，图标框架只支持内置数组
        AgeMaxNp.append(AgeMax.tolist())
        # print(AgeAverag)
    print(AgeMaxNp,type(Average))


    bar = (
        Bar(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add_xaxis(School)
            .add_yaxis("平均年龄",Average)
            .add_yaxis("最大年龄",AgeMaxNp)
            .set_global_opts(title_opts=opts.TitleOpts(title="各驾校学员年龄情况"))
    )
    bar.render('ageaverage.html')
    return School,Average,AgeMaxNp

def SexDistrbution(mg,table):
    """驾校维度"""
    mg.ChangeCollection(table)
    SchoolAry=[]
    results  = mg.FindAllData({},{'SchoolCode':True})
    SexAry = []
    for row1 in results:
        school = row1['SchoolCode']
        SchoolAry.append(school)
        res = mg.FindAllData({'SchoolCode':school},{'_id':False,'data.sex':True})
        man = 0
        woman =0
        wmary = []
        for row in res:
            # print(row)
            # print(len(row['data']))
            for index in range(len(row['data'])):
                sex = row['data'][index]['sex']
                if sex=='男':
                    man +=1
                else:
                    woman +=1
            SexAry.append([man,woman])
    # print(SexAry)
    NpSexAry= np.array(SexAry)
    # print(NpSexAry,NpSexAry.shape)
    # print(NpSexAry[:,0])#第一列
    print(NpSexAry.T)#转置
    NewSexAry = NpSexAry.T
    print(NewSexAry[0])
    bar = (
        Bar(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add_xaxis(SchoolAry)
            .add_yaxis("男",NewSexAry[0].tolist())#不支持numpy数组
            .add_yaxis("女",NewSexAry[1].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title="各驾校学员性别"))
    )
    bar.render('sex.html')

def TotolGraduate(mg,table):
    mg.ChangeCollection(table)
    res = mg.FindAllData({},{'SchoolCode':True})
    SchoolAry=[]
    StateAry=[]
    for row in res:
        Graduate = 0
        NonGraduate = 0
        school = row['SchoolCode']
        SchoolAry.append(school)
        results = mg.FindAllData({'SchoolCode':school},{'data':True})
        for row1 in results:
            for index in range(len(row1['data'])):
                state = row1['data'][index]['State']
                if state==1:
                    Graduate +=1
                else:
                    NonGraduate +=1
            StateAry.append([Graduate,NonGraduate])
    StateAryNp = np.array(StateAry)
    NewStateAry = StateAryNp.T

    bar = (
        Bar(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add_xaxis(SchoolAry)
            .add_yaxis("已结业", NewStateAry[0].tolist())  # 不支持numpy数组
            .add_yaxis("未结业", NewStateAry[1].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title="各驾校学员结业情况"))
    )
    bar.render('graduate.html')

def CarTypeSpread(mg,table):
    mg.ChangeCollection(table)
    res = mg.FindAllData({},{'SchoolCode':True})
    SchoolAry = []
    CarTypeAry=[]
    for row in res:
        C1Ary=0
        Other=0
        school= row['SchoolCode']
        SchoolAry.append(school)
        results = mg.FindAllData({"SchoolCode":school},{'data':True})
        for row1 in results:
            for index in range(len(row1['data'])):
                CarType = row1['data'][index]['CarType']
                if CarType==21:
                    C1Ary +=1
                else:
                    Other +=1
            CarTypeAry.append([C1Ary,Other])
    CarTypeAryNp= np.array(CarTypeAry)
    NewCarTypeAry = CarTypeAryNp.T

    bar = (
        Bar(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add_xaxis(SchoolAry)
            .add_yaxis("C1", NewCarTypeAry[0].tolist())  # 不支持numpy数组
            .add_yaxis("其他", NewCarTypeAry[1].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title="各驾校学员培训车型情况"))
    )
    bar.render('CarType.html')


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
    """市区维度"""
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
    """市区维度"""
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
    # AgeDistrbution(mg,'school')
    # SexDistrbution(mg,'school')
    # TotolGraduate(mg,'school')
    # CarTypeSpread(mg,'school')
    make_snapshot(snapshot, "sex.html","sex.png")
    make_snapshot(snapshot, "graduate.html","graduate.png")
    make_snapshot(snapshot, "ageaverage.html","geaverage.png")
    make_snapshot(snapshot, "CarType.html","carType.png")





