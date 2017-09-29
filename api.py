from flask import Flask
from flask import request
from flask_cors import CORS
from pyArango.connection import *
import json
import datetime, calendar
import datetime as dt
from datetime import date, timedelta,datetime

conn = Connection(username="root", password="")
db = conn["athena3"]
value = 0

app = Flask(__name__)
CORS(app)

################# Repos ############################################################################################

@app.route('/Languages')
def Languages():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER Repo.repoName == @name
    SORT LanguagesRepo.size DESC
    RETURN {Languages:Languages.name,Size:LanguagesRepo.size}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=10, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    # print(queryResult[0])
    print(result)
    return json.dumps(result)
    # return json.dumps(dict([f for f in queryResult]))
    # return json.dumps(dict(queryResult[0]))
@app.route('/Commits')
def Commits():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER Commit.committedDate >= "2017-08-01T00:00:00Z"
    FILTER Commit.committedDate <= "2017-08-31T00:00:00Z"
    COLLECT
    day = DATE_FORMAT(Commit.committedDate,"%dd - %www")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      month: day,
      number: number
    }"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/Commits2')
def Commits2():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
    COLLECT
    day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name = request.args.get("name")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = endDate - startDate
    bindVars = {"name" : name,"startDate": str(startDate),"endDate":str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in range(delta.days + 1)]
    lst = []
    def recur(x):
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                day['number'] = str(y.get('number'))
                return day
        day['day'] = x
        day['number'] = 0
        return day
    for x in days:
        lst.append(recur(x))
    # print(lst)
    return json.dumps(lst)

@app.route('/RepoMembers')
def RepoMembers():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER Commit.committedDate > "2017-01-01T00:00:00Z"
    RETURN DISTINCT {member:Commit.author}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/BestPractices')
def BestPractices():
    aql = """
    LET a =(
    FOR Repo IN Repo
    FILTER Repo.repoName == @name
    RETURN {openSource:Repo.openSource,readme:Repo.readme,licenseType:Repo.licenseType})
    LET b =(
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") > @date
       COLLECT WITH COUNT INTO length
    RETURN length)
    RETURN {open:a,active:b}"""
    name = request.args.get("name")
    date = (dt.datetime.now() + dt.timedelta(-60)).strftime('%Y-%m-%d')
    print(date)
    bindVars = {"name" : name,"date":date}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/Issues')
def Issues():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER Issue.repoName == @name
    FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") <= @endDate
    COLLECT 
    day = DATE_FORMAT(Issue.closedAt,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name = request.args.get("name")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = endDate - startDate
    bindVars = {"name" : name,"startDate": str(startDate),"endDate":str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in range(delta.days + 1)]
    lst = []
    def recur(x):
        global value
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                value = int(y.get('number')) + value
                day['number'] = value
                return day
        day['day'] = x
        day['number'] = 0 + value
        return day
    value = 0
    for x in days:
        lst.append(recur(x))

        aql = """
    FOR Issue IN Issue
    FILTER Issue.repoName == @name
    FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") <= @endDate
    COLLECT 
    day = DATE_FORMAT(Issue.createdAt,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    bindVars = {"name" : name,"startDate": str(startDate),"endDate":str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in range(delta.days + 1)]
    lst2 = []
    def recur(x):
        global value
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                value = int(y.get('number')) + value
                day['number'] = value
                return day
        day['day'] = x
        day['number'] = 0 + value
        return day
    value = 0
    for x in days:
        lst2.append(recur(x))
    lista = []
    lista.append(lst)
    lista.append(lst2)
    print(lista)
    return json.dumps(lista)

################# Orgs ############################################################################################

@app.route('/LanguagesOrg')
def LanguagesOrg():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER Repo.org == @name
    COLLECT ageGroup = Languages.name 
    AGGREGATE soma = SUM(LanguagesRepo.size)
    SORT soma DESC
    LIMIT 12
    RETURN {name:ageGroup,size:soma}"""
    aql2 = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    RETURN DISTINCT Repo._id"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bindVars)
    queryResult2 = db.AQLQuery(aql2, rawResults=True, batchSize=100000, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    result2 = len(queryResult2)
    print(queryResult2)
    for x in result:
        x['size'] = round(x['size']/result2,2)
    print(result)
    return json.dumps(result)

@app.route('/OpenSource')
def OpenSource():
    aql = """
    LET openSource = (
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Repo.openSource == True
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    LET notOpenSource = (
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Repo.openSource == False
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    RETURN {openSource,notOpenSource}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = int(result[0]["openSource"][0]) + int(result[0]["notOpenSource"][0])
    print(result)
    for x in result:
        x['openSource'] = round(int(x['openSource'][0])/soma*100,1)
        x['notOpenSource'] = round(int(x['notOpenSource'][0])/soma*100,1)
    print(result)
    return json.dumps(result)

@app.route('/CommitsOrg')
def CommitsOrg():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.org == @name
    FILTER Commit.committedDate >= "2017-08-01T00:00:00Z"
    FILTER Commit.committedDate <= "2017-08-31T00:00:00Z"
    COLLECT
    day = DATE_FORMAT(Commit.committedDate,"%www-%dd")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name =  request.args.get("name")
    month = request.args.get("month")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    year = 2017
    month = int(month)
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, day).strftime('%a-%d') for day in range(1, num_days+1)]
    lst = []
    def recur(x):
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                day['number'] = str(y.get('number'))
                return day
        day['day'] = x
        day['number'] = 0
        return day
    for x in days:
        lst.append(recur(x))
    # print(lst)
    return json.dumps(lst)

@app.route('/readmeOrg')
def readmeOrg():
    aql = """
    LET ok = (
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Repo.readme == 'OK'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    LET poor = (
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Repo.readme == 'Poor'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
        LET bad = (
    FOR Repo IN Repo
    FILTER Repo.org == @name
    FILTER Repo.readme == null
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    RETURN {ok,poor,bad}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = int(result[0]["ok"][0]) + int(result[0]["poor"][0]) + int(result[0]["bad"][0])
    print(result)
    for x in result:
        x['ok'] = round(int(x['ok'][0])/soma*100,1)
        x['poor'] = round(int(x['poor'][0])/soma*100,1)
        x['bad'] = round(int(x['bad'][0])/soma*100,1)
    print(result)
    return json.dumps(result)

@app.route('/LicenseType')
def LicenseType():
    aql = """
    FOR Repo IN Repo
    FILTER Repo.org == @name
    COLLECT
    day = Repo.licenseType
    WITH COUNT INTO number
    SORT number DESC
    RETURN {
    day: day,
    number: number
    }"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=10000, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = sum([x['number'] for x in result])
    for x in result:
        if x['day'] == None:
            x['day'] = "None"
        x['number'] = round(x['number']/soma*100,2)
    print(soma)
    # print(queryResult[0])
    print(result)
    return json.dumps(result)


if __name__ == '__main__':
    app.run()
