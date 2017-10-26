from flask import request
from api import *
from .config import *


def repo_name():
    aql = """
    FOR Repo IN FULLTEXT(Repo, "repoName",@name)
    FILTER Repo.org == @org
    LIMIT 6
    RETURN {data:Repo.repoName}
    """
    name = "prefix:" + str(request.args.get("name"))
    org = str(request.args.get("org"))
    bind_vars = {"name": name, "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def repo_languages():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Repo.org == @org
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER LOWER(Repo.repoName) == @name
    SORT LanguagesRepo.size ASC
    RETURN DISTINCT {Languages:Languages.name,Size:LanguagesRepo.size}"""
    name = request.args.get("name")
    org = str(request.args.get("org"))
    bind_vars = {"name": name, "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=10, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def repo_commits():
    aql = """
    FOR Commit IN Commit
    FILTER LOWER(Commit.repoName) == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
    FILTER Commit.org == @org
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
    org = str(request.args.get("org"))
    delta = end_date - start_date
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date), "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
    lst = []

    def recur(day_slice):
        day_dict = {}
        for y in result:
            if y.get('day') == day_slice:
                day_dict['day'] = str(y.get('day'))
                day_dict['number'] = int(y.get('number'))
                return day_dict
        day_dict['day'] = day_slice
        day_dict['number'] = 0
        return day_dict
    for day in days:
        lst.append(recur(day))
    return json.dumps(lst)


def repo_members():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.org == @org
    FILTER LOWER(Commit.repoName) == @name
    FILTER Commit.committedDate > "2017-01-01T00:00:00Z"
    FILTER Commit.author != "anonimo"
    RETURN DISTINCT {member:Commit.author}"""
    name = request.args.get("name")
    org = str(request.args.get("org"))
    bind_vars = {"name": str.lower(name), "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    print(result)
    return json.dumps(result)


def repo_best_practices():
    aql = """
    LET a =(
    FOR Repo IN Repo
    FILTER Repo.org == @org
    FILTER LOWER(Repo.repoName) == @name
    RETURN {openSource:Repo.openSource,readme:Repo.readme,licenseType:Repo.licenseType})
    LET b =(
    FOR Commit IN Commit
    FILTER Commit.org == @org
    FILTER LOWER(Commit.repoName) == @name
    FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") > @date
       COLLECT WITH COUNT INTO length
    RETURN length)
    RETURN {open:a,active:b}"""
    name = request.args.get("name")
    date = (dt.datetime.now() + dt.timedelta(-60)).strftime('%Y-%m-%d')
    org = str(request.args.get("org"))
    print(date)
    bind_vars = {"name": str.lower(name), "date": date, "org": org}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    if not result[0]["open"]:
        return json.dumps([{'open': [404], 'active': [404]}])
    print(result)
    return json.dumps(result)