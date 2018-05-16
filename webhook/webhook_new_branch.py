

class GetBranch:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def __parse_branch_string(data):
        return '/'.join(data.split("/")[2:])

    def __update_new_branch_commits(self, org, repo_name, base_branch, branch):
        existed_branch = self.db.query_find_to_dictionary_distinct("Commit", "_id", {"org": org, "repo_name": repo_name,
                                                                                     "branch_name": base_branch})
        self.db.update_generic(obj={"_id": {"$in": existed_branch}}, patch={"$addToSet": {"branch_name": {"$each": [branch]}}},
                               kind="Commit")

    def get_data(self, raw_json):
        import pprint
        pprint.pprint(raw_json)
        org_name = raw_json['organization']['login']
        repo_name = raw_json['repository']['name']
        base_branch = self.__parse_branch_string(raw_json['base_ref'])
        branch = self.__parse_branch_string(raw_json['ref'])
        self.__update_new_branch_commits(org_name, repo_name, base_branch, branch)
