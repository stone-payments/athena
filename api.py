from flask import Flask
from flask import request
from flask_cors import CORS
from pyArango.connection import *
import json
import datetime, calendar
import datetime as dt
from datetime import date, timedelta, datetime
from user_api import *


conn = Connection(username="root", password="")
db = conn["athena_teste"]
value = 0

app = Flask(__name__)
CORS(app)

# Repos #####


@app.route('/Languages')
def Languages():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER LOWER(Repo.repoName) == @name
    SORT LanguagesRepo.size ASC
    RETURN DISTINCT {Languages:Languages.name,Size:LanguagesRepo.size}"""
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=10, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


@app.route('/Commits2')
def Commits2():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.repoName) == @name
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
    start_date = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    days = [datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    return json.dumps(lst)


@app.route('/RepoMembers')
def RepoMembers():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.repoName) == @name
    FILTER Commit.committedDate > "2017-01-01T00:00:00Z"
    FILTER Commit.author != "anonimo"
    RETURN DISTINCT {member:Commit.author}"""
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


@app.route('/BestPractices')
def BestPractices():
    aql = """
    LET a =(
    FOR Repo IN Repo
    FILTER LOWER(Repo.repoName) == @name
    RETURN {openSource:Repo.openSource,readme:Repo.readme,licenseType:Repo.licenseType})
    LET b =(
    FOR Commit IN Commit
    FILTER LOWER(Commit.repoName) == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") > @date
       COLLECT WITH COUNT INTO length
    RETURN length)
    RETURN {open:a,active:b}"""
    name = request.args.get("name")
    date = (dt.datetime.now() + dt.timedelta(-60)).strftime('%Y-%m-%d')
    print(date)
    bind_vars = {"name": str.lower(name), "date": date}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    if not result[0]["open"]:
        return json.dumps([{'open': [404], 'active': [404]}])
    print(result)
    return json.dumps(result)


@app.route('/Issues')
def Issues():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER LOWER(Issue.repoName) == @name
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
    start_date = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    FILTER LOWER(Issue.repoName) == @name
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
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    response = [lst, lst2]
    print(response)
    return json.dumps(response)

# Orgs ############


@app.route('/LanguagesOrg')
def LanguagesOrg():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER LOWER(Repo.org) == @name
    COLLECT ageGroup = Languages.name 
    AGGREGATE soma = SUM(LanguagesRepo.size)
    SORT soma DESC
    RETURN {name:ageGroup,size:soma}"""
    name = "stone-payments"
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    soma = sum(item['size'] for item in result)
    for x in result:
        x['size'] = round((x['size']/soma*100), 2)
    print(result[:12])
    return json.dumps(result[:12])


@app.route('/OpenSource')
def OpenSource():
    aql = """
    LET openSource = (
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    FILTER Repo.openSource == True
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    LET notOpenSource = (
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    FILTER Repo.openSource == False
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    RETURN {openSource,notOpenSource}"""
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = int(result[0]["openSource"][0]) + int(result[0]["notOpenSource"][0])
    print(result)
    for x in result:
        x['openSource'] = round(int(x['openSource'][0])/soma*100, 1)
        x['notOpenSource'] = round(int(x['notOpenSource'][0])/soma*100, 1)
    print(result)
    return json.dumps(result)


@app.route('/CommitsOrg')
def CommitsOrg():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.org) == @name
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
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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


@app.route('/readmeOrg')
def readmeOrg():
    aql = """
    LET ok = (
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    FILTER Repo.readme == 'OK'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    LET poor = (
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    FILTER Repo.readme == 'Poor'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
        LET bad = (
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    FILTER Repo.readme == null
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    RETURN {ok,poor,bad}"""
    name = request.args.get("name")
    bindVars = {"name": str.lower(name)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = int(result[0]["ok"][0]) + int(result[0]["poor"][0]) + int(result[0]["bad"][0])
    print(result)
    for x in result:
        x['ok'] = round(int(x['ok'][0])/soma*100, 1)
        x['poor'] = round(int(x['poor'][0])/soma*100, 1)
        x['bad'] = round(int(x['bad'][0])/soma*100, 1)
    print(result)
    return json.dumps(result)


@app.route('/LicenseType')
def LicenseType():
    aql = """
    FOR Repo IN Repo
    FILTER LOWER(Repo.org) == @name
    COLLECT
    day = Repo.licenseType
    WITH COUNT INTO number
    SORT number DESC
    RETURN {
    day: day,
    number: number
    }"""
    name = request.args.get("name")
    bindVars = {"name": str.lower(name)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=10000, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    soma = sum([x['number'] for x in result])
    for x in result:
        if x['day'] is None:
            x['day'] = "None"
        x['number'] = round(x['number']/soma*100, 2)
    print(soma)
    # print(queryResult[0])
    print(result)
    return json.dumps(result)


@app.route('/IssuesOrg')
def IssuesOrg():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER LOWER(Issue.org) == @name
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
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    FILTER LOWER(Issue.org) == @name
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
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    response = [lst, lst2]
    print(response)
    return json.dumps(response)


# Teams ############################################################################################

@app.route('/LanguagesOrgTeam')
def LanguagesOrgTeam():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER LOWER(Repo.org) == @org
    FILTER LOWER(Teams.teamName) == @team
    COLLECT ageGroup = Languages.name 
    AGGREGATE soma = SUM(LanguagesRepo.size)
    SORT soma DESC
    RETURN {name:ageGroup,size:soma}"""
    org = request.args.get("org")
    team = request.args.get("team")
    bindVars = {"team": str.lower(team), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    soma = sum(item['size'] for item in result)
    for x in result:
        x['size'] = round((x['size']/soma*100), 2)
    print(result)
    return json.dumps(result[:12])


@app.route('/OpenSourceTeam')
def OpenSourceTeam():
    aql = """
    LET openSource = (
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER Repo.openSource == True
    FILTER LOWER(Teams.teamName) == @team
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    LET notOpenSource = (
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER Repo.openSource == False
    FILTER LOWER(Teams.teamName) == @team
        COLLECT 
        day = Repo.openSource
    WITH COUNT INTO number
    RETURN number)
    RETURN {openSource,notOpenSource}"""
    team = request.args.get("team")
    org = request.args.get("org")
    bindVars = {"team": str.lower(team), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    if not result[0]["openSource"]:
        return json.dumps([{'openSource': [404], 'notOpenSource': [404]}])
    try:
        resultOpenSource = int(result[0]["openSource"][0])
    except:
        resultOpenSource = 0
    try:
        resultnotOpenSource = int(result[0]["notOpenSource"][0])
    except:
        resultnotOpenSource = 0
    soma = resultOpenSource + resultnotOpenSource
    for x in result:
        x['openSource'] = round(resultOpenSource/soma*100, 1)
        x['notOpenSource'] = round(resultnotOpenSource/soma*100, 1)
    return json.dumps(result)


@app.route('/CommitsTeam')
def CommitsTeam():
    aql = """
    FOR Commit IN Commit
    FOR Repo IN Repo
    FOR RepoCommit IN RepoCommit
    FOR Teams IN Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER LOWER(Commit.org) == @org
    FILTER LOWER(Teams.teamName) == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <=  @endDate
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER RepoCommit._from == Repo._id
    FILTER RepoCommit._to == Commit._id
    COLLECT
    day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name = request.args.get("name")
    org = request.args.get("org")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = endDate - startDate
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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


@app.route('/readmeOrgTeam')
def readmeOrgTeam():
    aql = """
    LET ok = (
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER LOWER(Teams.teamName) == @team
    FILTER Repo.readme == 'OK'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    LET poor = (
        FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER LOWER(Teams.teamName) == @team
    FILTER Repo.readme == 'Poor'
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
        LET bad = (
        FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER LOWER(Teams.teamName) == @team
    FILTER Repo.readme == null
        COLLECT 
        day = Repo.readme
    WITH COUNT INTO number
    RETURN number)
    RETURN {ok,poor,bad}"""
    team = request.args.get("team")
    org = request.args.get("org")
    bindVars = {"team": str.lower(team), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    if not result[0]["ok"]:
        return json.dumps([{'ok': [404], 'poor': [404], 'bad': [404]}])
    try:
        resultOk = int(result[0]["ok"][0])
    except:
        resultOk = 0
    try:
        resultPoor = int(result[0]["poor"][0])
    except:
        resultPoor = 0
    try:
        resultBad = int(result[0]["bad"][0])
    except:
        resultBad = 0
    soma = resultOk + resultPoor + resultBad
    print(result)
    for x in result:
        x['ok'] = round(resultOk/soma*100, 1)
        x['poor'] = round(resultPoor/soma*100, 1)
        x['bad'] = round(resultBad/soma*100, 1)
    print(result)
    return json.dumps(result)


@app.route('/LicenseTypeTeam')
def LicenseTypeTeam():
    aql = """
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER LOWER(Teams.teamName) == @team
    COLLECT
    day = Repo.licenseType
    WITH COUNT INTO number
    SORT number DESC
    RETURN {
    day: day,
    number: number
    }"""
    team = request.args.get("team")
    org = request.args.get("org")
    bindVars = {"team": str.lower(team), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=10000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    soma = sum([x['number'] for x in result])
    for x in result:
        if x['day'] is None:
            x['day'] = "None"
        x['number'] = round(x['number']/soma*100, 2)
    print(soma)
    print(result)
    return json.dumps(result)


@app.route('/RepoMembersTeam')
def RepoMembersTeam():
    aql = """
    FOR Repo IN Repo
    FOR Teams In Teams
    FOR TeamsRepo IN TeamsRepo
    FOR Dev IN Dev
    FOR TeamsDev IN TeamsDev
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER TeamsDev._from == Dev._id
    FILTER TeamsDev._to == Teams._id
    FILTER LOWER(Repo.org) == @org
    FILTER Dev.login != "anonimo"
    FILTER LOWER(Teams.teamName) == @team
    RETURN DISTINCT {member:Dev.login}"""
    team = request.args.get("team")
    org = request.args.get("org")
    bindVars = {"team": str.lower(team), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)


@app.route('/IssuesTeam')
def IssuesTeam():
    global value
    aql = """
    FOR Issue IN Issue
    FOR Repo IN Repo
    FOR Teams IN Teams
    FOR RepoIssue IN RepoIssue
    FOR TeamsRepo IN TeamsRepo
    FILTER LOWER(Issue.org) == @org
    FILTER LOWER(Teams.teamName) == @name
    FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") <= @endDate
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER RepoIssue._from == Repo._id
    FILTER RepoIssue._to == Issue._id
    COLLECT 
    day = DATE_FORMAT(Issue.closedAt,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name = request.args.get("name")
    org = request.args.get("org")
    startDate = datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    endDate = datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = endDate - startDate
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    FOR Repo IN Repo
    FOR Teams IN Teams
    FOR RepoIssue IN RepoIssue
    FOR TeamsRepo IN TeamsRepo
    FILTER LOWER(Issue.org) == @org
    FILTER LOWER(Teams.teamName) == @name
    FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") <= @endDate
    FILTER TeamsRepo._from == Repo._id
    FILTER TeamsRepo._to == Teams._id
    FILTER RepoIssue._from == Repo._id
    FILTER RepoIssue._to == Issue._id
    COLLECT 
    day = DATE_FORMAT(Issue.createdAt,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    bindVars = {"name": str.lower(name), "startDate": str(startDate), "endDate": str(endDate), "org": str.lower(org)}
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    days = [datetime.strptime(str(startDate + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    response = [lst, lst2]
    print(response)
    return json.dumps(response)

# Users #########################


@app.route('/get_avatar')
def get_avatar():
    response = avatar()
    return response


@app.route('/get_user_commit')
def get_user_commit():
    response = user_commit()
    return response


@app.route('/get_user_language')
def get_user_language():
    response = user_language()
    return response


@app.route('/get_user_contributed_repo')
def get_user_contributed_repo():
    response = user_contributed_repo()
    return response


@app.route('/get_user_issue')
def get_user_issue():
    response = user_issue()
    return response


@app.route('/get_user_stats')
def get_user_stats():
    response = user_stats()
    return response


@app.route('/get_repo_name')
def get_repo_name():
    response = repo_name()
    return response


@app.route('/get_user_team')
def get_user_team():
    response = user_team()
    return response


if __name__ == '__main__':
    app.run()
