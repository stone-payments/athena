from pyArango.collection import Collection, Field, Edges

from validators import *


class TeamsDev(Edges):
    """
    TEAMS_DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class TeamsRepo(Edges):
    """
    TEAMS_REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class DevCommit(Edges):
    """
    DEV_COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoCommit(Edges):
    """
    REPO_COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoFork(Edges):
    """
    REPO_FORK
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class DevFork(Edges):
    """
    DEV_FORK
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class RepoIssue(Edges):
    """
    REPO_ISSUE
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
    )


class LanguagesRepo(Edges):
    """
    LANGUAGES_DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        size=Field(validators=[val.NotNull(), IntVal()]),
    )


class RepoDev(Edges):
    """
    REPO_DEV
    """
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
        name=Field(validators=[val.NotNull(), StringVal()]),
        id=Field(validators=[val.NotNull(), StringVal()])
    )


class Teams(Collection):
    """
    TEAMS
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        createdAt=Field(validators=[val.NotNull(), StringVal()]),
        teamName=Field(validators=[val.NotNull(), StringVal()]),
        privacy=Field(validators=[val.NotNull(), StringVal()]),
        slug=Field(validators=[val.NotNull(), StringVal()]),
        membersCount=Field(validators=[IntVal()]),
        repoCount=Field(validators=[IntVal()]),
        id=Field(validators=[val.NotNull(), StringVal()]),
        org=Field(validators=[val.NotNull(), StringVal()])
    )


class Commit(Collection):
    """
    COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        messageHeadline=Field(validators=[StringVal()]),
        oid=Field(validators=[val.NotNull(), StringVal()]),
        committedDate=Field(validators=[val.NotNull(), StringVal()]),
        author=Field(validators=[StringVal()]),
        devId=Field(validators=[val.NotNull(), StringVal()]),
        GitHubId=Field(validators=[val.NotNull(), StringVal()]),
        repositoryId=Field(validators=[val.NotNull(), StringVal()]),
        repoName=Field(validators=[val.NotNull(), StringVal()]),
        branchName=Field(validators=[StringVal()]),
        commitId=Field(validators=[val.NotNull(), StringVal()]),
        org=Field(validators=[val.NotNull(), StringVal()]),
        totalAddDel=Field(validators=[val.NotNull(), IntVal()]),
        additions=Field(validators=[val.NotNull(), IntVal()]),
        deletions=Field(validators=[val.NotNull(), IntVal()]),
        numFiles=Field(validators=[val.NotNull(), IntVal()]),
    )


class Dev(Collection):
    """
    DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        devName=Field(validators=[StringVal()]),
        followers=Field(IntVal()),
        following=Field(IntVal()),
        login=Field(validators=[val.NotNull(), StringVal()]),
        avatarUrl=Field(validators=[StringVal()]),
        contributedRepositories=Field(IntVal()),
        pullRequests=Field(IntVal()),
        id=Field(validators=[val.NotNull(), StringVal()]),
        org=Field(validators=[val.NotNull(), StringVal()]),
    )


class Repo(Collection):
    """
    REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        repoName=Field(validators=[StringVal()]),
        description=Field(validators=[StringVal()]),
        url=Field(validators=[StringVal()]),
        openSource=Field(validators=[val.NotNull(), BoolVal()]),
        primaryLanguage=Field(validators=[StringVal()]),
        forks=Field(validators=[IntVal()]),
        issues=Field(validators=[IntVal()]),
        stargazers=Field(validators=[IntVal()]),
        watchers=Field(validators=[IntVal()]),
        createdAt=Field(validators=[StringVal()]),
        nameWithOwner=Field(validators=[StringVal()]),
        licenseId=Field(validators=[StringVal()]),
        licenseType=Field(validators=[StringVal()]),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
        readme=Field(validators=[StringVal()])
    )


class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), StringVal()]),
        repoName=Field(validators=[StringVal()]),
        createdAt=Field(validators=[val.NotNull(), StringVal()]),
        id=Field(validators=[val.NotNull(), StringVal()]),
        isPrivate=Field(validators=[val.NotNull(), BoolVal()]),
        isLocked=Field(validators=[BoolVal()]),
        devId=Field(validators=[val.NotNull(), StringVal()]),
        login=Field(validators=[StringVal()]),
        forkId=Field(validators=[val.NotNull(), StringVal()]),
        org=Field(validators=[val.NotNull(), StringVal()])
    )


class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), StringVal()]),
        repoName=Field(validators=[val.NotNull(), StringVal()]),
        state=Field(validators=[StringVal()]),
        closedAt=Field(validators=[StringVal()]),
        author=Field(validators=[StringVal()]),
        issueId=Field(validators=[val.NotNull(), StringVal()]),
        createdAt=Field(validators=[val.NotNull(), StringVal()]),
        closed=Field(validators=[BoolVal()]),
        label=Field(validators=[StringVal()]),
        title=Field(validators=[StringVal()]),
        org=Field(validators=[val.NotNull(), StringVal()])
    )
