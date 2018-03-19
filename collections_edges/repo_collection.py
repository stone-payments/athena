from collectors_and_savers.collector import *
from collection_modules.language_detect import text_to_language


def repo(db, org, query, collection_name, edge_name="edges"):
    def content(**kwargs):
        node = kwargs.get('node')
        org_name = kwargs.get('org')
        lower_case_readme = find_key('lowerCaseReadme', node)
        upper_case_readme = find_key('upperCaseReadme', node)
        lower_case_contributing = find_key('lowerCaseContributing', node)
        upper_case_contributing = find_key('upperCaseContributing', node)
        lower_case_text_readme = find_key('lowerCaseTextReadme', node)
        upper_case_text_readme = find_key('upperCaseTextReadme', node)
        if upper_case_readme:
            readme = "OK" if upper_case_readme[-1]['endingLine'] >= 5 else "Poor"
        elif lower_case_readme:
            readme = "OK" if lower_case_readme[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        if upper_case_text_readme and readme is not None:
            readme_language = text_to_language(upper_case_text_readme)
        elif lower_case_text_readme and readme is not None:
            readme_language = text_to_language(lower_case_text_readme)
        else:
            readme_language = None
        if upper_case_contributing:
            contributing = "OK"
        elif lower_case_contributing:
            contributing = "OK"
        else:
            contributing = None
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(org_name, not_none=True),
            "_id": find_key('repoId', node),
            "repoName": string_validate(find_key('name', node), not_none=True),
            "description": string_validate(find_key('description', node)),
            "url": string_validate(find_key('url', node)),
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
            "readmeLanguage": string_validate(readme_language),
            "contributing": string_validate(contributing),
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
                             number_of_repo=number_pagination_repositories, updated_utc_time=utc_time,
                             save_content=content, save_edges=edges)
    start.start()
