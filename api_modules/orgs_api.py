import datetime as dt
import datetime
from datetime import date
import json

from flask import request

from api_modules import db


def org_languages():
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
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=1000000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    soma = sum(item['size'] for item in result)
    for x in result:
        x['size'] = round((x['size'] / soma * 100), 2)
    print(result[:12])
    return json.dumps(result[:12])


def org_open_source():
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
    RETURN {openSource:openSource,notOpenSource:notOpenSource}"""
    name = request.args.get("name")
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    # print(result)
    # print(result[0]["notOpenSource"].get("notOpenSource", 0))
    if not result[0]["notOpenSource"]:
        result[0]["notOpenSource"] = [0]
    if not result[0]["openSource"]:
        result[0]["openSource"] = [0]
    soma = int(result[0]["openSource"][0]) + int(result[0]["notOpenSource"][0])
    print(result)
    for x in result:
        x['openSource'] = round(int(x['openSource'][0]) / soma * 100, 1)
        x['notOpenSource'] = round(int(x['notOpenSource'][0]) / soma * 100, 1)
    print(result)
    return json.dumps(result)


def org_commits():
    name = request.args.get("name")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
    query = [{'$match': {'org': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
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
    query_result = db.Commit.aggregate(query)
    result = [dict(i) for i in query_result]
    print(result)
    for x in result:
        x['date'] = dt.datetime(x['year'], x['month'], x['day'], 0, 0)
    print(result)
    days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
    # days = [dt.date.strptime(str(start_date + dt.timedelta(days=i)), '%Y-%m-%d %H:%M:%S')
    #         for i in range(delta.days + 1)]
    print(days)
    lst = []

    def recur(x):
        day = {}
        for y in result:
            if y.get('date') == x:
                day['day'] = str(y.get('date').strftime('%a %d-%b'))
                day['number'] = int(y.get('count'))
                return day
        day['day'] = x.strftime('%a %d-%b')
        day['count'] = 0
        return day
    for x in days:
        lst.append(recur(x))
    print(lst)
    return json.dumps(lst)


def org_readme():
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
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100, bindVars=bind_vars)
    # print([f for f in queryResult])
    result = [dict(i) for i in query_result]
    # if not result[0]["ok"] or not result[0]["poor"] or not result[0]["bad"]:
    #     return json.dumps([{'ok': 404, 'poor': 404, 'bad': 404}])
    if not result[0]["ok"]:
        result[0]["ok"] = [0]
    if not result[0]["poor"]:
        result[0]["poor"] = [0]
    if not result[0]["bad"]:
        result[0]["bad"] = [0]
    soma = int(result[0]["ok"][0]) + int(result[0]["poor"][0]) + int(result[0]["bad"][0])
    print(result)
    for x in result:
        x['ok'] = round(int(x['ok'][0]) / soma * 100, 1)
        x['poor'] = round(int(x['poor'][0]) / soma * 100, 1)
        x['bad'] = round(int(x['bad'][0]) / soma * 100, 1)
    print(result)
    return json.dumps(result)


def org_license():
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
    bind_vars = {"name": str.lower(name)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=10000, bindVars=bind_vars)
    # print([f for f in queryResult])
    result = [dict(i) for i in query_result]
    soma = sum([x['number'] for x in result])
    for x in result:
        if x['day'] is None:
            x['day'] = "None"
        x['number'] = round(x['number'] / soma * 100, 2)
    print(soma)
    # print(queryResult[0])
    print(result)
    return json.dumps(result)


def org_issues():
    aql_created = """
    let a =(    
    FOR Issue IN Issue
        FILTER LOWER(Issue.org) == @name
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
        FILTER LOWER(Issue.org) == @name
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
        FILTER LOWER(Issue.org) == @name
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
        FILTER LOWER(Issue.org) == @name
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
    response = [result_closed, result_created]
    return json.dumps(response)
