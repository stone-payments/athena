from flask import request
from .config import *
import datetime as dt
from api import *
import re
from operator import itemgetter
import json


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
        x['size'] = round((x['size'] / soma * 100), 2)
    print(result)
    return json.dumps(result[:12])


def team_open_source():
    org = request.args.get("org")
    name = request.args.get("name")
    query = [
        {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}}
        , {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
        {
            '$match':
                {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
        {'$group': {
            '_id': {
                'status': "$Repo.openSource",
            },
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id.status': -1}},
        {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
    ]
    query_result = db.edges.aggregate(query)
    readme_status_list = [dict(i) for i in query_result]
    print(readme_status_list)
    soma = sum([readme_status['count'] for readme_status in readme_status_list])
    for readme_status in readme_status_list:
        if readme_status['status'][0] is None:
            readme_status['status'] = 'None'
        else:
            readme_status['status'] = readme_status['status'][0]
        readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
    print(readme_status_list)
    return json.dumps(readme_status_list)


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
    org = request.args.get("org")
    name = request.args.get("name")
    query = [
        {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}}
        , {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
        {
            '$match':
                {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
        {'$group': {
            '_id': {
                'status': "$Repo.readme",
            },
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id.status': -1}},
        {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
    ]
    query_result = db.edges.aggregate(query)
    readme_status_list = [dict(i) for i in query_result]
    print(readme_status_list)
    soma = sum([readme_status['count'] for readme_status in readme_status_list])
    for readme_status in readme_status_list:
        if readme_status['status'][0] is None:
            readme_status['status'] = 'None'
        else:
            readme_status['status'] = readme_status['status'][0]
        readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
    print(readme_status_list)
    return json.dumps(readme_status_list)


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
        x['number'] = round(x['number'] / soma * 100, 2)
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
    name = "^" + str(request.args.get("name"))
    org = request.args.get("org")
    compiled_name = re.compile(r'%s' % name, re.I)
    query_result = db['Teams'].find({'slug': {'$regex': compiled_name}, 'org': org},
                                    {'_id': 0, 'slug': 1}).limit(6)
    result = [dict(i) for i in query_result]
    if not query_result:
        return json.dumps([{'response': 404}])
    print(result)
    return json.dumps(result)


def issues_team():
    aql_created = """
    let a =(    
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
        day = DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd")
        WITH COUNT INTO number
        SORT day ASC
        RETURN {
          day: day,
          number: number
        })
    
    let begin = @startDate
    let end = @endDate
    let b = (
    for date in 0..DATE_DIFF(begin, end, "days")
        let actual_date = DATE_FORMAT(DATE_ADD(begin, date,  "d"),"%Y-%mm-%dd")
        return {day:actual_date,number:0})

    let removable = REMOVE_VALUES(b, a )
    let result = UNION(removable, a)
    FOR results IN result
    SORT results.day ASC
    RETURN  results"""
    name = request.args.get("name")
    org = request.args.get("org")
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date), "org": str.lower(org)}
    query_result = db.AQLQuery(aql_created, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result_created = [dict(i) for i in query_result]

    def accumulator(days):
        value_accumulated = 0
        for day in days:
            if day["number"] > 0:
                value_accumulated += day["number"]
                day["number"] = value_accumulated
            else:
                day["number"] = value_accumulated
        return days

    result_created = accumulator(result_created)

    aql_closed = """
        let a =(    
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
        day = DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd")
        WITH COUNT INTO number
        SORT day ASC
        RETURN {
          day: day,
          number: number
        })
    
    let begin = @startDate
    let end = @endDate
    let b = (
    for date in 0..DATE_DIFF(begin, end, "days")
        let actual_date = DATE_FORMAT(DATE_ADD(begin, date,  "d"),"%Y-%mm-%dd")
        return {day:actual_date,number:0})

    let removable = REMOVE_VALUES(b, a )
    let result = UNION(removable, a)
    FOR results IN result
    SORT results.day ASC
    RETURN  results"""

    query_result = db.AQLQuery(aql_closed, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result_closed = [dict(i) for i in query_result]
    result_closed = accumulator(result_closed)
    response = [result_closed, result_created]
    return json.dumps(response)
