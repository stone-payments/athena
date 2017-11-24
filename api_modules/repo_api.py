from flask import request
from api import *
from .config import *
import re


def repo_name():
    name = "^" + str(request.args.get("name"))
    org = str(request.args.get("org"))
    compiled_name = re.compile(r'%s' % name, re.I)
    print(compiled_name)
    query_result = db['Repo'].find({'org': org, 'repoName': {'$regex': compiled_name}}, {'_id': 0, 'repoName': 1})
    result = [dict(i) for i in query_result]
    return json.dumps(result)


def repo_languages():
    name = request.args.get("name")
    org = str(request.args.get("org"))
    query_result = db['Repo'].find({'org': org, 'repoName': name}, {"languages": 1, "_id": 0})
    result = [dict(i) for i in query_result]
    return json.dumps(result)


# def repo_commits():
#     start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
#     end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
#     query = [
#         {'$project': {
#             "day": {'$dayOfMonth': "$committedDate"},
#             "month": {'$month': "$committedDate"},
#             "year": {'$year': "$committedDate"}}},
#         {'$match': {"year": {'$gte': start_date.year, '$lte': end_date.year},
#                     "day": {'$gte': start_date.day, '$lte': end_date.day}, "month": {'$gte': start_date.month,
#                                                                                      '$lte': end_date.month}}},
#         {'$group': {"_id": "$day",
#                     "day": {'$first': "$day"},
#                     "month": {'$first': "$month"},
#                     "year": {'$first': "$year"},
#                     'count': {
#                         "$sum": 1
#                     }}},
#         {'$project': {"_id": 0,
#                       "count": 1,
#                       "day": 1,
#                       "month": 1,
#                       "year": 1
#                       }}]
#
#     aql = """
#     FOR Commit IN Commit
#     FILTER LOWER(Commit.repoName) == @name
#     FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") >= @startDate
#     FILTER DATE_FORMAT(Commit.committedDate,"%Y-%mm-%dd") <= @endDate
#     FILTER Commit.org == @org
#     COLLECT
#     day = DATE_FORMAT(Commit.committedDate,"%www %dd-%mmm")
#     WITH COUNT INTO number
#     SORT day ASC
#     RETURN {
#       day: day,
#       number: number
#     }"""
#
#     # start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d').strftime('%Y-%m-%d')
#     # end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d').strftime('%Y-%m-%d')
#     org = str(request.args.get("org"))
#     # delta = end_date - start_date
#     print(end_date)
#     # bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date), "org": org}
#     query_result = db['Commit'].aggregate(query)
#     # query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
#     result = [dict(i) for i in query_result]
#     print(result)
#     # days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
#     #         for i in range(delta.days + 1)]
#     # lst = []
#     #
#     # def recur(day_slice):
#     #     day_dict = {}
#     #     for y in result:
#     #         if y.get('day') == day_slice:
#     #             day_dict['day'] = str(y.get('day'))
#     #             day_dict['number'] = int(y.get('number'))
#     #             return day_dict
#     #     day_dict['day'] = day_slice
#     #     day_dict['number'] = 0
#     #     return day_dict
#     # for day in days:
#     #     lst.append(recur(day))
#     # return json.dumps(lst)
#     return json.dumps(result)


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
