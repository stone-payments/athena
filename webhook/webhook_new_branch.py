from collection_modules.module import find_key


class GetBranch:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def __parse_branch_string(data):
        return '/'.join(data.split("/")[2:])

    def __update_new_branch_commits(self, org, repo_name, base_branch, branch):
        existed_branch = self.db.query_find_to_dictionary_distinct("Commit", "_id", {"org": org, "repo_name": repo_name,
                                                                                     "branchName": base_branch})
        self.db.update_generic(obj={"_id": {"$in": existed_branch}}, patch={"$addToSet": {"branchName": {"$each": [branch]}}},
                               kind="Commit")

    def get_data(self, raw_json):
        org_name = find_key('login', find_key('organization', raw_json))
        repo_name = find_key('name', find_key('repository', raw_json))
        base_branch = self.__parse_branch_string(find_key('base_ref', raw_json))
        branch = self.__parse_branch_string(find_key('ref', raw_json))
        self.__update_new_branch_commits(org_name, repo_name, base_branch, branch)
