from collectors_and_savers.collector import *


def org_collection(db, org, query, collection_name, edge_name="edges"):
    def content(**kwargs):
        page = kwargs.get('page')
        org_name = kwargs.get('org')
        save_content = {
            "collection_name": string_validate(collection_name, not_none=True),
            "org": string_validate(org_name, not_none=True),
            "_id": not_null(find_key('id', page)),
            "avatarUrl": string_validate(find_key('avatarUrl', page)),
            "description": string_validate(find_key('description', page)),
            "membersCount": int_validate(find_key('membersCount', page)),
            "teamsCount": int_validate(find_key('teamsCount', page)),
            "repoCount": int_validate(find_key('repoCount', page)),
            "projectCount": int_validate(find_key('projectCount', page)),
            "db_last_updated": datetime.datetime.utcnow(),
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
