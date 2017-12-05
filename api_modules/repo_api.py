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
    if not query_result:
        return json.dumps([{'response': 404}])
    print(result)
    return json.dumps(result)


def repo_languages():
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


def repo_commits():
    name = request.args.get("name")
    org = request.args.get("org")
    start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
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
    if not commits_count_list:
        return json.dumps([{'response': 404}])
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
    print(query_result)
    query_result = [dict(i) for i in query_result]
    if not query_result:
        return json.dumps([{'response': 404}])
    print(query_result)
    query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                query_result[0]['db_last_updated']).total_seconds() / 60)
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
    if not query_result:
        return json.dumps([{'response': 404}])
    query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                query_result[0]['db_last_updated']).total_seconds() / 60)
    print(query_result)
    return json.dumps(query_result)


def repo_issues():
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

    def accumulator(days):
        value_accumulated = 0
        for day in days:
            if day["count"] > 0:
                value_accumulated += day["count"]
                day["count"] = value_accumulated
            else:
                day["count"] = value_accumulated
        return days

    def process_data(db_collection, db_query, days_delta):
        count_list = db[db_collection].aggregate(db_query)
        count_list = [dict(i) for i in count_list]
        for count in count_list:
            count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
        range_days = [start_date + dt.timedelta(days=i) for i in range(days_delta.days + 1)]
        processed_list = []
        for day in range_days:
            processed_list.append(fill_all_dates(day, count_list))
        processed_list = accumulator(processed_list)
        return processed_list

    name = request.args.get("name")
    org = request.args.get("org")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    delta = end_date - start_date
    query_created = [{'$match': {'org': org, 'repoName': name, 'createdAt': {'$gte': start_date, '$lte': end_date}}},
                     {'$group': {
                         '_id': {
                             'year': {'$year': "$createdAt"},
                             'month': {'$month': "$createdAt"},
                             'day': {'$dayOfMonth': "$createdAt"},
                         },
                         'count': {'$sum': 1}
                     }},
                     {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
                     ]
    query_closed = [{'$match': {'org': org, 'repoName': name, 'closedAt': {'$gte': start_date, '$lte': end_date}}},
                    {'$group': {
                        '_id': {
                            'year': {'$year': "$closedAt"},
                            'month': {'$month': "$closedAt"},
                            'day': {'$dayOfMonth': "$closedAt"},
                        },
                        'count': {'$sum': 1}
                    }},
                    {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
                    ]
    created_issues_list = process_data('Issue', query_created, delta)
    closed_issues_list = process_data('Issue', query_closed, delta)
    response = [closed_issues_list, created_issues_list]
    print(response)
    return json.dumps(response)
