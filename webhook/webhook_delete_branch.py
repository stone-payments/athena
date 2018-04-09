from collection_modules.module import find_key


class DeleteBranch:

    def __init__(self, db):
        self.db = db

    def __update_deleted_branch_commits(self, org, repo_name, branch):
        existed_branch_id = self.db.query_find_to_dictionary_distinct("Commit", "_id", {"org": org,
                                                                                        "repoName": repo_name,
                                                                                        "branchName": branch})
        self.db.update_generic(obj={"_id": {"$in": existed_branch_id}}, patch={"$pull": {"branchName": branch}},
                               kind="Commit")

    def get_data(self, raw_json):
        org_name = find_key('login', find_key('owner', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        branch = find_key('ref', raw_json)
        self.__update_deleted_branch_commits(org_name, repo_name, branch)
