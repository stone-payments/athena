from flask import request
from api import *
from .config import *
import datetime as dt


def avatar():
    aql = """
    FOR Dev IN Dev
    FILTER LOWER(Dev.login) == @login
    RETURN {login:Dev.login,avatar:Dev.avatarUrl,followers:Dev.followers,following:Dev.following,
            contributed:Dev.contributedRepositories,pullrequests:Dev.pullRequests}"""
    login = request.args.get("login")
    bindvars = {"login": str.lower(login)}
    queryresult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindvars)
    result = [dict(i) for i in queryresult]
    if not result:
        return json.dumps([{'login': 'user does not exist', 'avatar': 'assets/img/default-avatar.png', 'followers': "-",
                            'following': "-", 'contributed': "-", 'pullrequests': "-"}])
    print(result)
    return json.dumps(result)


def user_commit():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.author) == @name
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
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
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
    FILTER LOWER(Dev.login) == @dev
    COLLECT ageGroup = Languages.name 
    AGGREGATE soma = SUM(LanguagesRepo.size)
    SORT soma DESC
    RETURN {name:ageGroup,size:soma}"""
    dev = request.args.get("name")
    bind_vars = {"dev": str.lower(dev)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    soma = sum(item['size'] for item in result)
    for x in result:
        x['size'] = round((x['size'] / soma * 100), 2)
    print(result)
    return json.dumps(result[:12])


def user_contributed_repo():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.author) == @name
    FILTER Commit.committedDate >= @startDate
    FILTER Commit.committedDate <= @endDate
    RETURN DISTINCT {member:Commit.repoName}"""
    name = request.args.get("name")
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def user_issue():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER LOWER(Issue.closed_login) == @name
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
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
            range(delta.days + 1)]
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
    FILTER LOWER(Issue.created_login) == @name
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
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
            range(delta.days + 1)]
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


def user_stats():
    aql = """
        FOR Commit IN Commit
        FILTER LOWER(Commit.author) == @name
        FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
        COLLECT day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
        AGGREGATE additions = SUM(Commit.additions)
        RETURN {day:day,number:additions}"""
    name = request.args.get("name")
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
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
                FILTER LOWER(Commit.author) == @name
                FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
                FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
                COLLECT day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
                AGGREGATE deletions = SUM(Commit.deletions)
                RETURN {day:day,number:deletions}"""
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b') for i in
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
    response = [lst, lst2]
    print(response)
    return json.dumps(response)


def user_team():
    aql = """
    FOR Teams IN Teams
    FOR TeamsDev in TeamsDev
    FOR Dev IN Dev
    FILTER TeamsDev._from == Dev._id
    FILTER TeamsDev._to == Teams._id
    FILTER LOWER(Dev.login) == @name
    RETURN DISTINCT{teams:Teams.teamName}
    """
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def user_login():
    aql = """
    FOR Dev IN FULLTEXT(Dev, "login",@name)
    LIMIT 6
    RETURN {data:Dev.login}
    """
    name = "prefix:" + str(request.args.get("name"))
    bind_vars = {"name": name}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)