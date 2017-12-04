from flask import request
import datetime as dt
import datetime
from api import *
from .config import *
import re
from operator import itemgetter
import json


def repo_name():
    name = "^" + str(request.args.get("name"))
    org = str(request.args.get("org"))
    compiled_name = re.compile(r'%s' % name, re.I)
    query_result = db['Repo'].find({'org': org, 'repoName': {'$regex': compiled_name}},
                                   {'_id': 0, 'repoName': 1}).limit(6)
    result = [dict(i) for i in query_result]
    return json.dumps(result)


def repo_languages():
    name = request.args.get("name")
    org = str(request.args.get("org"))
    query_result = db['Repo'].find({'org': org, 'repoName': name}, {"languages": 1, "_id": 0})
    result = [dict(i) for i in query_result]
    result = (result[0]['languages'])
    result = sorted(result, key=itemgetter('size'), reverse=True)
    print(result)
    return json.dumps(result)


def repo_commits():
    name = request.args.get("name")
    org = request.args.get("org")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    print(start_date)
    print(end_date)
    query = [{'$match': {'org': org, 'repoName': name, 'committedDate': {'$gte': start_date, '$lt': end_date}}},
             {'$group': {
                 '_id': {
                     'year': {'$year': "$committedDate"},
                     'month': {'$month': "$committedDate"},
                     'day': {'$dayOfMonth': "$committedDate"},
                 },
                 'count': {'$sum': 1}
             }},
             {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
             ]
    delta = end_date - start_date
    commits_count_list = db.Commit.aggregate(query)
    commits_count_list = [dict(i) for i in commits_count_list]
    print(commits_count_list)
    for commit_count in commits_count_list:
        commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
    print(commits_count_list)
    days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
    print(days)
    lst = []

    def fill_all_dates(x):
        day = {}
        for y in commits_count_list:
            if y.get('date') == x:
                day['day'] = str(y.get('date').strftime('%a %d-%b'))
                day['count'] = int(y.get('count'))
                return day
        day['day'] = x.strftime('%a %d-%b')
        day['count'] = 0
        return day

    for x in days:
        lst.append(fill_all_dates(x))
    print(lst)
    return json.dumps(lst)



def repo_members():
    name = request.args.get("name")
    org = str(request.args.get("org"))
    # bind_vars = {"name": str.lower(name), "org": org}
    # query_result = db.Commit.distinct('author', {'org': org, 'repoName': name}, {'_id': 0, 'author': 1})
    query_result = db.Commit.find({'org': org, 'repoName': name, 'author': {'$ne': None}},
                                  {'_id': 0, 'author': 1}).distinct("author")
    return json.dumps(query_result)


def repo_infos():
    name = request.args.get("name")
    # date = (dt.datetime.now() + dt.timedelta(-60)).strftime('%Y-%m-%d')
    org = str(request.args.get("org"))
    query = {'org': org, 'repoName': name}
    projection = {'_id': 0, 'repoName': 1, 'forks': 1, 'stargazers': 1, 'openSource': 1, 'licenseType': 1, 'readme': 1,
                  'db_last_updated': 1}
    query_result = db.Repo.find(query, projection)
    query_result = [dict(i) for i in query_result]
    query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                query_result[0]['db_last_updated']).total_seconds() / 60)
    print(query_result)
    return json.dumps(query_result)


def repo_best_practices():
    name = request.args.get("name")
    # date = (dt.datetime.now() + dt.timedelta(-60)).strftime('%Y-%m-%d')
    org = str(request.args.get("org"))
    query = {'org': org, 'repoName': name}
    projection = {'_id': 0, 'repoName': 1, 'forks': 1, 'stargazers': 1, 'openSource': 1, 'licenseType': 1, 'readme': 1,
                  'db_last_updated': 1}
    query_result = db.Repo.find(query, projection)
    query_result = [dict(i) for i in query_result]
    query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                query_result[0]['db_last_updated']).total_seconds() / 60)
    print(query_result)
    return json.dumps(query_result)


def repo_issues():
    aql_created = """
    let a =(    
    FOR Issue IN Issue
        FILTER LOWER(Issue.repoName) == @name
        FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") <= @endDate
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

    let c =(    
    FOR Issue IN Issue
        FILTER LOWER(Issue.repoName) == @name
        FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") <= @endDate
        COLLECT 
        day = DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd")
        WITH COUNT INTO number
        SORT day DESC
        RETURN {
          day: day, number:0
        })
    let removable = REMOVE_VALUES(b, c )
    let result = UNION(removable, a)
    FOR results IN result
    SORT results.day ASC
    RETURN  results"""
    name = request.args.get("name")
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
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
        FILTER LOWER(Issue.repoName) == @name
        FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") <= @endDate
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
        
    let c =(    
    FOR Issue IN Issue
        FILTER LOWER(Issue.repoName) == @name
        FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") >= @startDate
        FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") <= @endDate
        COLLECT 
        day = DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd")
        WITH COUNT INTO number
        SORT day DESC
        RETURN {
          day: day, number:0
        })
    let removable = REMOVE_VALUES(b, c )
    let result = UNION(removable, a)
    FOR results IN result
    SORT results.day ASC
    RETURN  results"""

    query_result = db.AQLQuery(aql_closed, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result_closed = [dict(i) for i in query_result]
    result_closed = accumulator(result_closed)
    response = [result_created, result_closed]
    return json.dumps(response)
