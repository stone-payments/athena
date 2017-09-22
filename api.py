from flask import Flask
from flask import request
from flask_cors import CORS
from pyArango.connection import *
import json

conn = Connection(username="root", password="")
db = conn["athena3"]


app = Flask(__name__)
CORS(app)
@app.route('/Languages')
def Languages():
    aql = """
    FOR Languages IN Languages
    FOR LanguagesRepo IN LanguagesRepo
    FOR Repo IN Repo
    FILTER Languages._id == LanguagesRepo._from
    FILTER Repo._id == LanguagesRepo._to
    FILTER Repo.repoName == @name
    SORT LanguagesRepo.size DESC
    RETURN {Languages:Languages.name,Size:LanguagesRepo.size}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=10, bindVars=bindVars)
    # print([f for f in queryResult])
    result = [dict(i) for i in queryResult]
    # print(queryResult[0])
    print(result)
    return json.dumps(result)
    # return json.dumps(dict([f for f in queryResult]))
    # return json.dumps(dict(queryResult[0]))
@app.route('/Commits')
def Commits():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER Commit.committedDate >= "2017-08-01T00:00:00Z"
    FILTER Commit.committedDate <= "2017-08-31T00:00:00Z"
    COLLECT
    day = DATE_FORMAT(Commit.committedDate,"%dd - %www")
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      month: day,
      number: number
    }"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/Commits2')
def Commits2():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER Commit.committedDate >= "2017-08-20T00:00:00Z"
    FILTER Commit.committedDate < "2017-08-21T00:00:00Z"
    COLLECT
    day = DATE_DAY(Commit.committedDate)
    WITH COUNT INTO number
    SORT day ASC
    RETURN {
      day: day,
      number: number
    }"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)

@app.route('/RepoMembers')
def RepoMembers():
    aql = """
    FOR Commit IN Commit
    FILTER Commit.repoName == @name
    FILTER Commit.committedDate > "2017-01-01T00:00:00Z"
    RETURN DISTINCT {member:Commit.author}"""
    name = request.args.get("name")
    bindVars = {"name" : name}
    # by setting rawResults to True you'll get dictionaries instead of Document objects, useful if you want to result to set of fields for example
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100000, bindVars=bindVars)
    result = [dict(i) for i in queryResult]
    print(result)
    return json.dumps(result)


if __name__ == '__main__':
    app.run()
