from collectors_and_savers.collector import *


def repo(db, org, query, collection_name, edge_name="edges"):
    def content(**kwargs):
        node = kwargs.get('node')
        org_name = kwargs.get('org')
        readme_ranges = find_key('ranges', node)
        if readme_ranges:
            readme = "OK" if readme_ranges[-1]['endingLine'] >= 5 else "Poor"
        else:
            readme = None
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(org_name, not_none=True),
            "_id": node["node"]["repoId"],
            "repoName": string_validate(node["node"]["name"], not_none=True),
            "description": string_validate(node["node"]["description"]),
            "url": string_validate(node["node"]["url"]),
            "openSource": bool_validate(False if node["node"]["isPrivate"] else True),
            "primaryLanguage": string_validate(find_key('priLanguage', node)),
            "forks": int_validate(node["node"]["forks"]["totalCount"]),
            "issues": int_validate(node["node"]["issues"]["totalCount"]),
            "stargazers": int_validate(node["node"]["stargazers"]["totalCount"]),
            "watchers": int_validate(node["node"]["watchers"]["totalCount"]),
            "createdAt": convert_datetime(find_key('createdAt', node)),
            "nameWithOwner": string_validate(node["node"]["nameWithOwner"]),
            "licenseId": string_validate(find_key('licenseId', node)),
            "licenseType": string_validate(find_key('licenseType', node)),
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
