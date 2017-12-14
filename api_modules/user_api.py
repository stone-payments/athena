from flask import request
from api import *
from .config import *
import datetime as dt
import re
import json


def avatar():
    name = request.args.get("login")
    query = {'login': name}
    projection = {'_id': 0, 'collection_name': 0}
    query_result = db.Dev.find(query, projection)
    query_result = [dict(i) for i in query_result]
    if not query_result:
        return json.dumps([{'response': 404}])
    print(query_result)
    query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                query_result[0]['db_last_updated']).total_seconds() / 60)
    query_result[0]['response'] = 200
    print(query_result)
    return json.dumps(query_result)


def user_commit():
    name = request.args.get("name")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    print(start_date)
    print(end_date)
    query = [{'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lt': end_date}}},
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

    name = request.args.get("name")
    org = str(request.args.get("org"))
    query_result = db['Repo'].find({'org': org, 'repoName': name}, {"languages": 1, "_id": 0})
    result = [dict(i) for i in query_result]
    if not result:
        return json.dumps([{'response': 404}])
    result = (result[0]['languages'])
    result = sorted(result, key=itemgetter('size'), reverse=True)
    print(result)
    return json.dumps(result)


def user_contributed_repo():
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    name = request.args.get("name")
    query_result = db.Commit.find({'author': name, 'committedDate': {'$gte': start_date, '$lt': end_date}},
                                  {'_id': 0, 'repoName': 1}).distinct("repoName")
    print(query_result)
    return json.dumps(query_result)


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
    def fill_all_dates(day_in_range, issue_count_list):
        days = {}
        for issue in issue_count_list:
            if issue.get('date') == day_in_range:
                days['day'] = str(issue.get('date').strftime('%a %d-%b'))
                days['count'] = int(issue.get('count'))
                return days
        days['day'] = day_in_range.strftime('%a %d-%b')
        days['count'] = 0
        return days

    def process_data(db_collection, db_query, days_delta):
        count_list = db[db_collection].aggregate(db_query)

        count_list = [dict(i) for i in count_list]
        print(count_list)
        for count in count_list:
            count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
        range_days = [start_date + dt.timedelta(days=i) for i in range(days_delta.days + 1)]
        processed_list = []
        for day in range_days:
            processed_list.append(fill_all_dates(day, count_list))
        # processed_list = accumulator(processed_list)
        return processed_list

    name = request.args.get("name")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    delta = end_date - start_date
    query_addttions = [
        {'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
        {
            '$group':
                {
                    '_id': {'author': "$author",
                            'year': {'$year': "$committedDate"},
                            'month': {'$month': "$committedDate"},
                            'day': {'$dayOfMonth': "$committedDate"},
                            },
                    'totalAmount': {'$sum': '$additions'}
                }
        },
        {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'author': '$_id.author',
                      'count': '$totalAmount'}}
    ]
    query_deletions = [
        {'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
        {
            '$group':
                {
                    '_id': {'author': "$author",
                            'year': {'$year': "$committedDate"},
                            'month': {'$month': "$committedDate"},
                            'day': {'$dayOfMonth': "$committedDate"},
                            },
                    'totalAmount': {'$sum': '$deletions'}
                }
        },
        {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'author': '$_id.author',
                      'count': '$totalAmount'}}
    ]
    addttions_list = process_data('Commit', query_addttions, delta)
    deletions_list = process_data('Commit', query_deletions, delta)
    response = [addttions_list, deletions_list]
    print(response)
    return json.dumps(response)


def user_team():
    name = request.args.get("name")
    query = [{'$lookup': {
        'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Team'}}
        , {'$lookup': {
            'from': 'Dev', 'localField': 'from', 'foreignField': '_id', 'as': 'Dev'}},
        {
            '$match':
                {"Dev.0.login": name, 'type': 'dev_to_team'}
        },
        {'$sort': {'Team.teamName': 1}},
        {'$project': {'_id': 0, "Team.teamName": 1, 'Team.org': 1}}
    ]
    query_result = db.edges.aggregate(query)
    result = [dict(i) for i in query_result]
    result = [x['Team'][0] for x in result]
    print(result)
    return json.dumps(result)


def user_login():
    name = "^" + str(request.args.get("name"))
    compiled_name = re.compile(r'%s' % name, re.I)
    query_result = db['Dev'].find({'login': {'$regex': compiled_name}},
                                  {'_id': 0, 'login': 1}).limit(6)
    result = [dict(i) for i in query_result]
    if not query_result:
        return json.dumps([{'response': 404}])
    print(result)
    return json.dumps(result)
