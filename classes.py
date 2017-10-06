import pyArango.validation as val
from pyArango.collection import Collection, Field, Edges


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
        size=Field(validators=[val.NotNull()]),
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
        name=Field(validators=[val.NotNull()]),
        id=Field(validators=[val.NotNull()])
    )


class Teams(Collection):
    """
    TEAMS
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        createdAt=Field(validators=[val.NotNull()]),
        teamName=Field(validators=[val.NotNull()]),
        privacy=Field(validators=[val.NotNull()]),
        slug=Field(validators=[val.NotNull()]),
        childTeams=Field(),
        childTeamsTotal=Field(),
        ancestors=Field(),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()])
    )


class Commit(Collection):
    """
    COMMIT
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        messageHeadline=Field(),
        oid=Field(validators=[val.NotNull()]),
        committedDate=Field(validators=[val.NotNull()]),
        author=Field(),
        devId=Field(validators=[val.NotNull()]),
        GitHubId=Field(validators=[val.NotNull()]),
        repositoryId=Field(validators=[val.NotNull()]),
        repoName=Field(validators=[val.NotNull()]),
        branchName=Field(),
        commitId=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
        totalAddDel=Field(validators=[val.NotNull()]),
        additions=Field(validators=[val.NotNull()]),
        deletions=Field(validators=[val.NotNull()]),
        numFiles=Field(validators=[val.NotNull()]),
    )


class Dev(Collection):
    """
    DEV
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        devName=Field(),
        followers=Field(),
        following=Field(),
        login=Field(validators=[val.NotNull()]),
        avatarUrl=Field(),
        contributedRepositories=Field(),
        pullRequests=Field(),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
    )


class Repo(Collection):
    """
    REPO
    """
    _validation = {
        'allow_foreign_fields': False
    }
    _fields = dict(
        repoName=Field(),
        description=Field(),
        url=Field(),
        openSource=Field(validators=[val.NotNull()]),
        primaryLanguage=Field(),
        forks=Field(),
        stargazers=Field(),
        watchers=Field(),
        createdAt=Field(),
        nameWithOwner=Field(),
        licenseId=Field(),
        licenseType=Field(),
        id=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()]),
        readme=Field()
    )


class Fork(Collection):
    """
    Fork
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull()]),
        repoName=Field(),
        createdAt=Field(validators=[val.NotNull()]),
        id=Field(validators=[val.NotNull()]),
        isPrivate=Field(validators=[val.NotNull()]),
        isLocked=Field(),
        devId=Field(validators=[val.NotNull()]),
        login=Field(),
        forkId=Field(validators=[val.NotNull()]),
        org=Field(validators=[val.NotNull()])
    )


class Issue(Collection):
    """
    Issue
    """
    _fields = dict(
        repositoryId=Field(validators=[val.NotNull()]),
        repoName=Field(),
        state=Field(),
        closedAt=Field(),
        author=Field(),
        issueId=Field(validators=[val.NotNull()]),
        createdAt=Field(validators=[val.NotNull()]),
        closed=Field(),
        label=Field(),
        title=Field(),
        org=Field(validators=[val.NotNull()])
    )
