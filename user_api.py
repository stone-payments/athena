from flask import request
from pyArango.connection import *
import json
import datetime, calendar
import datetime as dt
from datetime import date, timedelta,datetime
from api import *



def avatar():
    aql = """
    FOR Dev IN Dev
    FILTER Dev.login == @login
    RETURN {login:Dev.login,avatar:Dev.avatarUrl,followers:Dev.followers,following:Dev.following,
            contributed:Dev.contributedRepositories,pullrequests:Dev.pullRequests}"""
    login = request.args.get("login")
    bindvars = {"login" : login}
    queryresult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindvars)
    result = [dict(i) for i in queryresult]
    print(result)
    return json.dumps(result)