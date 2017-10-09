import types

import pyArango.validation as val
from pyArango.collection import Collection, Field, Edges
from pyArango.theExceptions import ValidationError


class String_val(val.Validator):
    def validate(self, value):
        if type(value) is not types.StringType or None:
            raise ValidationError("Field value must be a string")
        return True


class Int_val(val.Validator):
    def validate(self, value):
        if type(value) is not types.IntType or None:
            raise ValidationError("Field value must be an int")
        return True


class Bool_val(val.Validator):
    def validate(self, value):
        if type(value) is not types.BooleanType or None:
            raise ValidationError("Field value must be an int")
        return True


class TeamsDev(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class TeamsRepo(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class DevCommit(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoCommit(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoFork(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class DevFork(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoIssue(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class LanguagesRepo(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        size=Field(validators=[val.NotNull(), Int_val()]),
    )


class RepoDev(Edges):
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class Languages(Collection):
    """
    LANGUAGES
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        name=Field(validators=[val.NotNull(), String_val()]),
        id=Field(validators=[val.NotNull(), String_val()])
    )


class Teams(Collection):
    """
    TEAMS
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        createdAt=Field(validators=[val.NotNull(), String_val()]),
        teamName=Field(validators=[val.NotNull(), String_val()]),
        privacy=Field(validators=[val.NotNull(), String_val()]),
        slug=Field(validators=[val.NotNull(), String_val()]),
        childTeamsTotal=Field(validators=[Int_val()]),
        id=Field(validators=[val.NotNull(), String_val()]),
        org=Field(validators=[val.NotNull(), String_val()])
    )


class Commit(Collection):
    """
    COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        messageHeadline=Field(validators=[String_val()]),
        oid=Field(validators=[val.NotNull(), String_val()]),
        committedDate=Field(validators=[val.NotNull(), String_val()]),
        author=Field(validators=[String_val()]),
        devId=Field(validators=[val.NotNull(), String_val()]),
        GitHubId=Field(validators=[val.NotNull(), String_val()]),
        repositoryId=Field(validators=[val.NotNull(), String_val()]),
        repoName=Field(validators=[val.NotNull(), String_val()]),
        branchName=Field(validators=[String_val()]),
        commitId=Field(validators=[val.NotNull(), String_val()]),
        org=Field(validators=[val.NotNull(), String_val()]),
        totalAddDel=Field(validators=[val.NotNull(), Int_val()]),
        additions=Field(validators=[val.NotNull(), Int_val()]),
        deletions=Field(validators=[val.NotNull(), Int_val()]),
        numFiles=Field(validators=[val.NotNull(), Int_val()]),
    )


class Dev(Collection):
    """
    DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        devName=Field(validators=[String_val()]),
        followers=Field(Int_val()),
        following=Field(Int_val()),
        login=Field(validators=[val.NotNull(), String_val()]),
        avatarUrl=Field(validators=[String_val()]),
        contributedRepositories=Field(Int_val()),
        pullRequests=Field(Int_val()),
        id=Field(validators=[val.NotNull(), String_val()]),
        org=Field(validators=[val.NotNull(), String_val()]),
    )


class Repo(Collection):
    """
    REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        repoName=Field(validators=[String_val()]),
        description=Field(validators=[String_val()]),
        url=Field(validators=[String_val()]),
        openSource=Field(validators=[val.NotNull(), Bool_val()]),
        primaryLanguage=Field(validators=[String_val()]),
        forks=Field(validators=[Int_val()]),
        stargazers=Field(validators=[Int_val()]),
        watchers=Field(validators=[Int_val()]),
        createdAt=Field(validators=[String_val()]),
        nameWithOwner=Field(validators=[String_val()]),
        licenseId=Field(validators=[String_val()]),
        licenseType=Field(validators=[String_val()]),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
        readme=Field(validators=[String_val()])
    )


class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), String_val()]),
        repoName=Field(validators=[String_val()]),
        createdAt=Field(validators=[val.NotNull(), String_val()]),
        id=Field(validators=[val.NotNull(), String_val()]),
        isPrivate=Field(validators=[val.NotNull(), Bool_val()]),
        isLocked=Field(validators=[Bool_val()]),
        devId=Field(validators=[val.NotNull(), String_val()]),
        login=Field(validators=[String_val()]),
        forkId=Field(validators=[val.NotNull(), String_val()]),
        org=Field(validators=[val.NotNull(), String_val()])
    )


class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), String_val()]),
        repoName=Field(validators=[val.NotNull(), String_val()]),
        state=Field(validators=[String_val()]),
        closedAt=Field(validators=[String_val()]),
        issueId=Field(validators=[val.NotNull(), String_val()]),
        createdAt=Field(validators=[val.NotNull(), String_val()]),
        closed=Field(validators=[Bool_val()]),
        label=Field(validators=[String_val()]),
        title=Field(validators=[String_val()]),
        org=Field(validators=[val.NotNull(), String_val()])
    )
