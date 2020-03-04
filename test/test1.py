from tools.mysql import MySQL
from tools.mongo import Mongo
import time
from pyecharts.charts import Bar
from pyecharts import options as opts

#同步mysql数据
# mydb = MySQL('10.50.50.82','root','wk-net','haoxueche',3306)
# mydb.ConnectDB()
#去掉不合法身份证号
# re = mydb.ExecuteSql("SELECT IdNumber,SchoolCode, CarType, State FROM ds_student where IdNumber REGEXP '[0-9]{18}|[0-9]{17}X'")
# print(len(re))
#连接mongodb
mg = Mongo(host="127.0.0.1",port=27017,dbase="jiapei",table='data')
#将需要统计数据存入mongodb
# for row in re:
#     # print(row)
#     data={
#         "IdNumber":row[0],
#         "SchoolCode":row[1],
#         "CarType":row[2],
#         "State":row[3]
#     }
#
#     mg.InsertData(data)
#
# size = mg.FindCount("data",{})
# print(size)

#当前时间 用于后面计算年龄
# LocalTime = time.localtime(time.time())
# res = mg.FindAllData({},{'_id':False})
#切换集合 将统计结果存储
mg.ChangeCollection('excle')
# for row in res:
#     # print(row)
#     if not row['IdNumber']:
#         continue
#     else:
#         StrId = row['IdNumber']
#         if not int(StrId[16])%2:
#             sex = '女'
#         else:
#             sex = '男'
#     AgeFile = StrId[6:10]
#     age = LocalTime.tm_year-int(AgeFile)
#     data = {
#         'sex':sex,
#         'age':age,
#         "SchoolCode": row['SchoolCode'],
#         "CarType":row['CarType']
#     }
#     mg.InsertData(data)


#统计男女数量
Man = mg.FindCount('excle',{'sex':'男'})
Women = mg.FindCount('excle',{'sex':'女'})

#年龄统计
res = mg.FindAllData({},{'_id':False,'age':True})

AgeAry = []
for i in res:
    AgeAry.append(i['age'])
AgeAry.sort()

#年龄与个数字典
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





# 性别分布
bar = (
    Bar()
    .add_xaxis(["男", "女"])
    .add_yaxis("性别", [Man, Women])
    .set_global_opts(title_opts=opts.TitleOpts(title="某驾校学员性别统计情况"))
)
bar.render('sex.html')

#年龄分布
bar2 = (
    Bar()
    .add_xaxis(Age)
    .add_yaxis("年龄", AgeCount)
    .set_global_opts(title_opts=opts.TitleOpts(title="某驾校学员年龄统计情况"))
)
bar2.render('age.html')


