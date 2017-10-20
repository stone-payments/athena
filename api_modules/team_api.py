from flask import request
from .config import *
import datetime as dt
from api import *


def team_languages():
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
    bind_vars = {"team": str.lower(team), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    soma = sum(item['size'] for item in result)
    for x in result:
        x['size'] = round((x['size']/soma*100), 2)
    print(result)
    return json.dumps(result[:12])


def team_open_source():
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
    bind_vars = {"team": str.lower(team), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    if not result[0]["openSource"]:
        return json.dumps([{'openSource': [404], 'notOpenSource': [404]}])
    try:
        result_open_source = int(result[0]["openSource"][0])
    except:
        result_open_source = 0
    try:
        resultnot_open_source = int(result[0]["notOpenSource"][0])
    except:
        resultnot_open_source = 0
    soma = result_open_source + resultnot_open_source
    for x in result:
        x['openSource'] = round(result_open_source/soma*100, 1)
        x['notOpenSource'] = round(resultnot_open_source/soma*100, 1)
    return json.dumps(result)


def team_commits():
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
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    days = [dt.datetime.strptime(str(start_date + dt.timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
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


def team_readme():
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
    bind_vars = {"team": str.lower(team), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    if not result[0]["ok"]:
        return json.dumps([{'ok': [404], 'poor': [404], 'bad': [404]}])
    try:
        result_ok = int(result[0]["ok"][0])
    except:
        result_ok = 0
    try:
        result_poor = int(result[0]["poor"][0])
    except:
        result_poor = 0
    try:
        result_bad = int(result[0]["bad"][0])
    except:
        result_bad = 0
    soma = result_ok + result_poor + result_bad
    print(result)
    for x in result:
        x['ok'] = round(result_ok/soma*100, 1)
        x['poor'] = round(result_poor/soma*100, 1)
        x['bad'] = round(result_bad/soma*100, 1)
    print(result)
    return json.dumps(result)


def team_license():
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
    bind_vars = {"team": str.lower(team), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=10000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    soma = sum([x['number'] for x in result])
    for x in result:
        if x['day'] is None:
            x['day'] = "None"
        x['number'] = round(x['number']/soma*100, 2)
    print(soma)
    print(result)
    return json.dumps(result)


def team_repo_members():
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
    bind_vars = {"team": str.lower(team), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def team_name():
    aql = """
    FOR Teams IN FULLTEXT(Teams, "teamName",@name)
    FILTER Teams.org == @org
    LIMIT 6
    RETURN {data:Teams.teamName}
    """
    name = "prefix:" + str(request.args.get("name"))
    org = str(request.args.get("org"))
    bind_vars = {"name": name, "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)