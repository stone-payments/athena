import datetime as dt
import datetime
from datetime import date
import json
from operator import itemgetter
from flask import request
from bson import json_util
from api_modules import db


def org_languages():
    name = request.args.get("name")
    query = [{'$match': {'org': name}},
             {'$unwind': "$languages"},
             {'$group': {
                 '_id': {
                     'language': "$languages.language",
                 },
                 'count': {'$sum': '$languages.size'}
             }},
             {'$sort': {'count': -1}},
             {'$project': {'_id': 0, "languages": "$_id.language", 'count': 1}}]

    query_result = db.Repo.aggregate(query)
    result = [dict(i) for i in query_result]
    print(result)
    soma = sum([language['count'] for language in result])
    print(soma)
    for x in result:
        x['count'] = round((x['count'] / soma * 100), 2)
    soma = sum([language['count'] for language in result])
    print(soma)
    print(result[:12])
    return json.dumps(result[:12])


def org_open_source():
    name = request.args.get("name")
    query = [{'$match': {'org': name}},
             {'$group': {
                 '_id': {
                     'openSource': "$openSource",
                 },
                 'count': {'$sum': 1}
             }},
             {'$sort': {'_id.openSource': 1}},
             {'$project': {'_id': 0, "openSource": "$_id.openSource", 'count': 1}}
             ]
    query_result = db.Repo.aggregate(query)
    open_source_type_list = [dict(i) for i in query_result]
    soma = sum([license_type['count'] for license_type in open_source_type_list])
    for open_source_status in open_source_type_list:
        if open_source_status['openSource'] is None:
            open_source_status['openSource'] = 'None'
        open_source_status['count'] = round(int(open_source_status['count']) / soma * 100, 1)
    open_source_type_list = sorted(open_source_type_list, key=itemgetter('count'), reverse=True)
    return json.dumps(open_source_type_list)


def org_commits():
    name = request.args.get("name")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    print(end_date)
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


def org_readme():
    name = request.args.get("name")
    query = [{'$match': {'org': name}},
             {'$group': {
                 '_id': {
                     'status': "$readme",
                 },
                 'count': {'$sum': 1}
             }},
             {'$sort': {'_id.status': -1}},
             {'$project': {'_id': 0, "status": "$_id.status", 'count': 1}}
             ]
    query_result = db.Repo.aggregate(query)
    readme_status_list = [dict(i) for i in query_result]
    soma = sum([readme_status['count'] for readme_status in readme_status_list])
    for readme_status in readme_status_list:
        if readme_status['status'] is None:
            readme_status['status'] = 'None'
        readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
    return json.dumps(readme_status_list)


def org_license():
    name = request.args.get("name")
    query = [{'$match': {'org': name}},
             {'$group': {
                 '_id': {
                     'license': "$licenseType",
                 },
                 'count': {'$sum': 1}
             }},
             {'$project': {'_id': 0, "license": "$_id.license", 'count': 1}}
             ]
    query_result = db.Repo.aggregate(query)
    license_type_list = [dict(i) for i in query_result]
    soma = sum([license_type['count'] for license_type in license_type_list])
    for license_type in license_type_list:
        if license_type['license'] is None:
            license_type['license'] = 'None'
        license_type['count'] = round(int(license_type['count']) / soma * 100, 1)
    license_type_list = sorted(license_type_list, key=itemgetter('count'), reverse=True)
    return json.dumps(license_type_list)


def org_issues():
    def fill_all_dates(x, commits_count_list):
        day = {}
        for y in commits_count_list:
            if y.get('date') == x:
                day['day'] = str(y.get('date').strftime('%a %d-%b'))
                day['count'] = int(y.get('count'))
                return day
        day['day'] = x.strftime('%a %d-%b')
        day['count'] = 0
        return day

    def accumulator(days):
        value_accumulated = 0
        for day in days:
            print(day)
            if day["count"] > 0:
                value_accumulated += day["count"]
                day["count"] = value_accumulated
            else:
                day["count"] = value_accumulated
        return days

    name = request.args.get("name")
    start_date = datetime.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
    end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
    query = [{'$match': {'org': name, 'createdAt': {'$gte': start_date, '$lte': end_date}}},
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
    delta = end_date - start_date
    commits_count_list = db.Issue.aggregate(query)
    commits_count_list = [dict(i) for i in commits_count_list]
    print(commits_count_list)
    for commit_count in commits_count_list:
        commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
    print(commits_count_list)
    days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
    print(days)
    created_issues_list = []
    created_issues_list = accumulator(created_issues_list)
    for z in days:
        created_issues_list.append(fill_all_dates(z, commits_count_list))
    print(created_issues_list)

    query = [{'$match': {'org': name, 'closedAt': {'$gte': start_date, '$lte': end_date}}},
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
    delta = end_date - start_date
    commits_count_list = db.Issue.aggregate(query)
    commits_count_list = [dict(i) for i in commits_count_list]
    print(commits_count_list)
    for commit_count in commits_count_list:
        commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
    print(commits_count_list)
    days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
    print(days)
    closed_issues_list = []
    for z in days:
        closed_issues_list.append(fill_all_dates(z, commits_count_list))
    print(closed_issues_list)
    closed_issues_list = accumulator(closed_issues_list)
    print(closed_issues_list)
    response = [created_issues_list, closed_issues_list]
    return json.dumps(response)


def org_info():
    name = request.args.get("name")
    query = {'org': name}
    projection = {'_id': 0, 'collection_name': 0}
    query_result = db.Org.find(query, projection)
    print(query_result)
    org_info_list = [dict(i) for i in query_result]
    org_info_list[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                 org_info_list[0]['db_last_updated']).total_seconds()/60)
    print(org_info_list)
    return json.dumps(org_info_list)
