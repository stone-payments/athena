from flask import Flask
from flask import request
from flask_cors import CORS
from pyArango.connection import *
import json
import datetime, calendar

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
    FOR Repo IN Repo
    FILTER Repo.repoName == @name
    RETURN {openSource:Repo.openSource,readme:Repo.readme,licenseType:Repo.licenseType}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/Issues')
def Issues():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER Issue.repoName == @name
    FILTER Issue.closedAt >= "2017-08-01T00:00:00Z"
    FILTER Issue.closedAt <= "2017-08-31T00:00:00Z"
    COLLECT 
    day = DATE_FORMAT(Issue.closedAt,"%www-%dd")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name =  request.args.get("name")
    month = request.args.get("month")
    print(month)
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
    FILTER Issue.createdAt >= "2017-08-01T00:00:00Z"
    FILTER Issue.createdAt <= "2017-08-31T00:00:00Z"
    COLLECT 
    day = DATE_FORMAT(Issue.createdAt,"%www-%dd")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name =  request.args.get("name")
    month = request.args.get("month")
    print(month)
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    year = 2017
    month = int(month)
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, day).strftime('%a-%d') for day in range(1, num_days+1)]
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

if __name__ == '__main__':
    app.run()