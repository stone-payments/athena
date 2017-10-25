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
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class TeamsRepo(Edges):
    """
    TEAMS_REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class DevCommit(Edges):
    """
    DEV_COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class RepoCommit(Edges):
    """
    REPO_COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class RepoFork(Edges):
    """
    REPO_FORK
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class DevFork(Edges):
    """
    DEV_FORK
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class RepoIssue(Edges):
    """
    REPO_ISSUE
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class LanguagesRepo(Edges):
    """
    LANGUAGES_REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        size=Field(validators=[val.NotNull(), IntValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class RepoDev(Edges):
    """
    REPO_DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Languages(Collection):
    """
    LANGUAGES
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        name=Field(validators=[val.NotNull(), StringValidator()]),
        id=Field(validators=[val.NotNull(), StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Teams(Collection):
    """
    TEAMS
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        createdAt=Field(validators=[val.NotNull(), StringValidator()]),
        teamName=Field(validators=[val.NotNull(), StringValidator()]),
        privacy=Field(validators=[val.NotNull(), StringValidator()]),
        slug=Field(validators=[val.NotNull(), StringValidator()]),
        membersCount=Field(validators=[IntValidator()]),
        repoCount=Field(validators=[IntValidator()]),
        id=Field(validators=[val.NotNull(), StringValidator()]),
        org=Field(validators=[val.NotNull(), StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Commit(Collection):
    """
    COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        messageHeadline=Field(validators=[StringValidator()]),
        oid=Field(validators=[val.NotNull(), StringValidator()]),
        committedDate=Field(validators=[val.NotNull(), StringValidator()]),
        author=Field(validators=[StringValidator()]),
        devId=Field(validators=[val.NotNull(), StringValidator()]),
        GitHubId=Field(validators=[val.NotNull(), StringValidator()]),
        repositoryId=Field(validators=[val.NotNull(), StringValidator()]),
        repoName=Field(validators=[val.NotNull(), StringValidator()]),
        branchName=Field(validators=[StringValidator()]),
        commitId=Field(validators=[val.NotNull(), StringValidator()]),
        org=Field(validators=[val.NotNull(), StringValidator()]),
        totalAddDel=Field(validators=[val.NotNull(), IntValidator()]),
        additions=Field(validators=[val.NotNull(), IntValidator()]),
        deletions=Field(validators=[val.NotNull(), IntValidator()]),
        numFiles=Field(validators=[val.NotNull(), IntValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Dev(Collection):
    """
    DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        devName=Field(validators=[StringValidator()]),
        followers=Field(IntValidator()),
        following=Field(IntValidator()),
        login=Field(validators=[val.NotNull(), StringValidator()]),
        avatarUrl=Field(validators=[StringValidator()]),
        contributedRepositories=Field(IntValidator()),
        pullRequests=Field(IntValidator()),
        id=Field(validators=[val.NotNull(), StringValidator()]),
        org=Field(validators=[val.NotNull(), StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Repo(Collection):
    """
    REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        repoName=Field(validators=[StringValidator()]),
        description=Field(validators=[StringValidator()]),
        url=Field(validators=[StringValidator()]),
        openSource=Field(validators=[val.NotNull(), BoolValidator()]),
        primaryLanguage=Field(validators=[StringValidator()]),
        forks=Field(validators=[IntValidator()]),
        issues=Field(validators=[IntValidator()]),
        stargazers=Field(validators=[IntValidator()]),
        watchers=Field(validators=[IntValidator()]),
        createdAt=Field(validators=[StringValidator()]),
        nameWithOwner=Field(validators=[StringValidator()]),
        licenseId=Field(validators=[StringValidator()]),
        licenseType=Field(validators=[StringValidator()]),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
        readme=Field(validators=[StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()]),
        committed_today=Field(validators=[val.NotNull(), BoolValidator()])
    )


class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), StringValidator()]),
        repoName=Field(validators=[StringValidator()]),
        createdAt=Field(validators=[val.NotNull(), StringValidator()]),
        id=Field(validators=[val.NotNull(), StringValidator()]),
        isPrivate=Field(validators=[val.NotNull(), BoolValidator()]),
        isLocked=Field(validators=[BoolValidator()]),
        devId=Field(validators=[val.NotNull(), StringValidator()]),
        login=Field(validators=[StringValidator()]),
        forkId=Field(validators=[val.NotNull(), StringValidator()]),
        org=Field(validators=[val.NotNull(), StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )


class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull(), StringValidator()]),
        repoName=Field(validators=[val.NotNull(), StringValidator()]),
        state=Field(validators=[StringValidator()]),
        closed_login=Field(validators=[StringValidator()]),
        closedAt=Field(validators=[StringValidator()]),
        issueId=Field(validators=[val.NotNull(), StringValidator()]),
        created_login=Field(validators=[val.NotNull(), StringValidator()]),
        createdAt=Field(validators=[val.NotNull(), StringValidator()]),
        authorAssociation=Field(validators=[val.NotNull(), StringValidator()]),
        closed=Field(validators=[BoolValidator()]),
        label=Field(validators=[StringValidator()]),
        title=Field(validators=[StringValidator()]),
        org=Field(validators=[val.NotNull(), StringValidator()]),
        db_last_updated=Field(validators=[val.NotNull(), StringValidator()])
    )
