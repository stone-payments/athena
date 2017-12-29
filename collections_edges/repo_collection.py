from collectors_and_savers.collector import *


def repo(db, org, query, collection_name, edge_name="edges"):
    def content(**kwargs):
        node = kwargs.get('node')
        org_name = kwargs.get('org')
        lower_case_readme = find_key('lowerCaseReadme', node)
        upper_case_readme = find_key('upperCaseReadme', node)
        if upper_case_readme:
            readme = "OK" if upper_case_readme[-1]['endingLine'] >= 5 else "Poor"
        elif lower_case_readme:
            readme = "OK" if lower_case_readme[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(org_name, not_none=True),
            "_id": find_key('repoId', node),
            "repoName": string_validate(find_key('name', node), not_none=True),
            "description": string_validate(find_key('description', node)),
            "url": string_validate(find_key('url', node)),
            "openSource": bool_validate(False if find_key('isPrivate', node) else True),
            "openSource": bool_validate(False if find_key('isPrivate', node) else True),
            "primaryLanguage": string_validate(find_key('priLanguage', node)),
            "forks": int_validate(find_key('totalForks', node)),
            "issues": int_validate(find_key('totalIssues', node)),
            "stargazers": int_validate(find_key('totalStars', node)),
            "watchers": int_validate(find_key('totalWatchers', node)),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "nameWithOwner": string_validate(find_key('nameWithOwner', node)),
            "licenseId": string_validate(find_key('licenseId', node)),
            "licenseType": string_validate(find_key('licenseType', node)),
            "isFork": bool_validate(find_key('isFork', node)),
            "readme": string_validate(readme),
            "db_last_updated": datetime.datetime.utcnow(),
            "languages": parse_multiple_languages(node, "language_edges", "languageName",
                                                  "languageSize"),
            "committed_today": bool_validate(False if find_key('committedInRangeDate', node) is None else True)
        }
        return save_content

    def edges(*_):
        save_edges = [
        ]
        return save_edges

    start = CollectorGeneric(db=db, collection_name=collection_name, org=org, edges=edge_name, query=query,
                             number_of_repo=repo_number_of_repos, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()
