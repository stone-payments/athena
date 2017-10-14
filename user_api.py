from flask import request
from pyArango.connection import *
import json
import datetime, calendar
import datetime as dt
from datetime import date, timedelta,datetime
from api import *



def avatar():
    aql = """
    FOR Dev IN Dev
    FILTER Dev.login == @login
    RETURN {login:Dev.login,avatar:Dev.avatarUrl,followers:Dev.followers,following:Dev.following,
            contributed:Dev.contributedRepositories,pullrequests:Dev.pullRequests}"""
    login = request.args.get("login")
    bindvars = {"login" : login}
    queryresult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindvars)
    result = [dict(i) for i in queryresult]
    print(result)
    return json.dumps(result)


def user_commit():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.author == @name
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
                day['number'] = int(y.get('number'))
                return day
        day['day'] = x
        day['number'] = 0
        return day
    for x in days:
        lst.append(recur(x))
    # print(lst)
    return json.dumps(lst)


def user_language():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FOR Dev In Dev
    FOR RepoDev IN RepoDev
    FILTER RepoDev._from == Repo._id
    FILTER RepoDev._to == Dev._id
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER Dev.login == @dev
    COLLECT ageGroup = Languages.name 
    AGGREGATE soma = SUM(LanguagesRepo.size)
    SORT soma DESC
    LIMIT 12
    RETURN {name:ageGroup,size:soma}"""
    aql2 = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FOR Dev In Dev
    FOR RepoDev IN RepoDev
    FILTER RepoDev._from == Repo._id
    FILTER RepoDev._to == Dev._id
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER Dev.login == @dev
    RETURN DISTINCT Repo._id"""
    dev = request.args.get("name")
    bindVars = {"dev" : dev}
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


def user_contributed_repo():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.author == @name
    FILTER Commit.committedDate >= @startDate
    FILTER Commit.committedDate <= @endDate
    RETURN DISTINCT {member:Commit.repoName}"""
    name = request.args.get("name")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    bindVars = {"name": name, "startDate": str(startDate), "endDate": str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)


def user_issue():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER Issue.closed_login == @name
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
    FILTER Issue.created_login == @name
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

def user_stats():
    aql = """
        FOR Commit IN Commit
        FILTER Commit.author == @name
        FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
        COLLECT day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
        AGGREGATE additions = SUM(Commit.additions)
        RETURN {day:day,number:additions}"""
    name = request.args.get("name")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = endDate - startDate
    bindVars = {"name": name, "startDate": str(startDate), "endDate": str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
            range(delta.days + 1)]
    lst = []

    def recur(x):
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                day['number'] = int(y.get('number'))
                return day
        day['day'] = x
        day['number'] = 0
        return day

    value = 0
    for x in days:
        lst.append(recur(x))

        aql = """
                FOR Commit IN Commit
                FILTER Commit.author == @name
                FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
                FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
                COLLECT day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
                AGGREGATE deletions = SUM(Commit.deletions)
                RETURN {day:day,number:deletions}"""
    bindVars = {"name": name, "startDate": str(startDate), "endDate": str(endDate)}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
            range(delta.days + 1)]
    lst2 = []

    def recur(x):
        day = {}
        for y in result:
            if y.get('day') == x:
                day['day'] = str(y.get('day'))
                day['number'] = int(y.get('number'))
                return day
        day['day'] = x
        day['number'] = 0
        return day

    value = 0
    for x in days:
        lst2.append(recur(x))
    lista = []
    lista.append(lst)
    lista.append(lst2)
    print(lista)
    return json.dumps(lista)

def repo_name():
    aql = """
    FOR Repo IN FULLTEXT(Repo, "repoName",@name)
    LIMIT 6
    RETURN {data:Repo.repoName}
    """
    name = "prefix:"+str(request.args.get("name"))
    bindVars = {"name": name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)