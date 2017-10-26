import os
from flask import Flask
from flask import request
from flask_cors import CORS
from pyArango.connection import *
import json
import datetime, calendar
import datetime as dt
from datetime import date, timedelta, datetime
from api_modules import *
# from team_api import *
# from repo_api import *
# from orgs_api import *
# from config import *
# import collections
# conn = Connection(username="root", password="")
# db = conn["athena_teste"]
value = 0

app = Flask(__name__, static_url_path='/static')
CORS(app)

with open("static/assets/js/configs.js", "w") as config_js:
    config_js.write('let address = "'+os.getenv("API_URL")+'"')

# Repos #####


@app.route('/Languages')
def Languages():
    response = repo_languages()
    return response


@app.route('/Commits_Repo')
def Commits_Repo():
    response = repo_commits()
    return response


@app.route('/RepoMembers')
def RepoMembers():
    response = repo_members()
    return response


@app.route('/BestPractices')
def BestPractices():
    response = repo_best_practices()
    return response


@app.route('/Issues')
# def Issues():
#     global value
#     aql = """
#     FOR Issue IN Issue
#     FILTER LOWER(Issue.repoName) == @name
#     FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") >= @startDate
#     FILTER DATE_FORMAT(Issue.closedAt,"%Y-%mm-%dd") <= @endDate
#     COLLECT
#     day = DATE_FORMAT(Issue.closedAt,"%www %dd-%mmm")
#     WITH COUNT INTO number
#     SORT day ASC
#     RETURN {
#       day: day,
#       number: number
#     }"""
#     name = request.args.get("name")
#     start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
#     end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d')
#     delta = end_date - start_date
#     bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
#     query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
#     result = [dict(i) for i in query_result]
#     days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
#             for i in range(delta.days + 1)]
#     lst = []
#
#     def recur(x):
#         global value
#         day = {}
#         for y in result:
#             if y.get('day') == x:
#                 day['day'] = str(y.get('day'))
#                 value = int(y.get('number')) + value
#                 day['number'] = value
#                 return day
#         day['day'] = x
#         day['number'] = 0 + value
#         return day
#     value = 0
#     for day in days:
#         lst.append(issue_accumulator(day))
#
#         aql = """
#     FOR Issue IN Issue
#     FILTER LOWER(Issue.repoName) == @name
#     FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") >= @startDate
#     FILTER DATE_FORMAT(Issue.createdAt,"%Y-%mm-%dd") <= @endDate
#     COLLECT
#     day = DATE_FORMAT(Issue.createdAt,"%www %dd-%mmm")
#     WITH COUNT INTO number
#     SORT day ASC
#     RETURN {
#       day: day,
#       number: number
#     }"""
#     bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date)}
#     query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
#     result = [dict(i) for i in query_result]
#     days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
#             for i in range(delta.days + 1)]
#     lst2 = []
#
#     def issue_accumulator(x):
#         global value
#         day_dict = {}
#         for y in result:
#             if y.get('day') == x:
#                 day_dict['day'] = str(y.get('day'))
#                 value += int(y.get('number'))
#                 day_dict['number'] = value
#                 return day_dict
#         day_dict['day'] = x
#         day_dict['number'] = 0 + value
#         return day_dict
#     value = 0
#     for day in days:
#         lst2.append(issue_accumulator(day))
#     response = [lst, lst2]
#     print(response)
#     return json.dumps(response)

def Issues():
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


# Orgs ############


@app.route('/LanguagesOrg')
def LanguagesOrg():
    response = org_languages()
    return response


@app.route('/OpenSource')
def OpenSource():
    response = org_open_source()
    return response


@app.route('/CommitsOrg')
def CommitsOrg():
    response = org_commits()
    return response


@app.route('/readmeOrg')
def readmeOrg():
    response = org_readme()
    return response


@app.route('/LicenseType')
def LicenseType():
    response = org_license()
    return response


@app.route('/IssuesOrg')
def IssuesOrg():
    global value
    aql = """
    FOR Issue IN Issue
    FILTER LOWER(Issue.org) == @name
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
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    FILTER LOWER(Issue.org) == @name
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
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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


@app.route('/get_repo_name')
def get_repo_name():
    response = repo_name()
    return response


# Teams ###


@app.route('/LanguagesOrgTeam')
def LanguagesOrgTeam():
    response = team_languages()
    return response


@app.route('/OpenSourceTeam')
def OpenSourceTeam():
    response = team_open_source()
    return response


@app.route('/CommitsTeam')
def CommitsTeam():
    response = team_commits()
    return response


@app.route('/readmeOrgTeam')
def readmeOrgTeam():
    response = team_readme()
    return response


@app.route('/LicenseTypeTeam')
def LicenseTypeTeam():
    response = team_license()
    return response


@app.route('/RepoMembersTeam')
def RepoMembersTeam():
    response = team_repo_members()
    return response


@app.route('/IssuesTeam')
def IssuesTeam():
    global value
    aql = """
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
    day = DATE_FORMAT(Issue.closedAt,"%www %dd-%mmm")
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
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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
    day = DATE_FORMAT(Issue.createdAt,"%www %dd-%mmm")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    bind_vars = {"name": str.lower(name), "startDate": str(start_date), "endDate": str(end_date), "org": str.lower(org)}
    query_result = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bind_vars)
    result = [dict(i) for i in query_result]
    days = [dt.datetime.strptime(str(start_date + timedelta(days=i)), '%Y-%m-%d %H:%M:%S').strftime('%a %d-%b')
            for i in range(delta.days + 1)]
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


# Users #########################


@app.route('/get_avatar')
def get_avatar():
    response = avatar()
    return response


@app.route('/get_user_commit')
def get_user_commit():
    response = user_commit()
    return response


@app.route('/get_user_language')
def get_user_language():
    response = user_language()
    return response


@app.route('/get_user_contributed_repo')
def get_user_contributed_repo():
    response = user_contributed_repo()
    return response


@app.route('/get_user_issue')
def get_user_issue():
    response = user_issue()
    return response


@app.route('/get_user_stats')
def get_user_stats():
    response = user_stats()
    return response


@app.route('/get_user_team')
def get_user_team():
    response = user_team()
    return response


@app.route('/get_team_name')
def get_team_name():
    response = team_name()
    return response


@app.route('/get_user_login')
def get_user_login():
    response = user_login()
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT"))

