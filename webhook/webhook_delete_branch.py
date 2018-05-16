

class DeleteBranch:

    def __init__(self, db):
        self.db = db

    def __update_deleted_branch_commits(self, org, repo_name, branch):
        existed_branch_id = self.db.query_find_to_dictionary_distinct("Commit", "_id", {"org": org,
                                                                                        "repo_name": repo_name,
                                                                                        "branch_name": branch})
        self.db.update_generic(obj={"_id": {"$in": existed_branch_id}}, patch={"$pull": {"branch_name": branch}},
                               kind="Commit")

    def get_data(self, raw_json):
        org_name = raw_json['repository']['owner']['login']
        repo_name = raw_json['repository']['name']
        branch = raw_json['ref']
        self.__update_deleted_branch_commits(org_name, repo_name, branch)
