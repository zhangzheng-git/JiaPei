from tools.mysql import MySQL
from tools.mongo import Mongo

mydb = MySQL('10.50.50.82','root','wk-net','haoxueche',3306)
mydb.ConnectDB()
re = mydb.ExecuteSql('SELECT IdNumber,SchoolCode, CarType, State FROM ds_student WHERE IdNumber !=""')
print(len(re))
mg = Mongo(host="127.0.0.1",port=27017,dbase="jiapei",table='data')
for row in re:
    print(row)
    data={
        "IdNumber":row[0],
        "SchoolCode":row[1],
        "CarType":row[2],
        "State":row[3]
    }
    mg.InsertData(data)

size = mg.FindCount("data",{})
print(size)