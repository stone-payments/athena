query ($org: String!, $next: String!) {
  organization(login: $org) {
    repository(name: $next) {
      id
      defaultBranchRef {
        target {
          ... on Commit {
            blame(path: "README.md") {
              ranges {
                endingLine
              }
            }
          }
        }
      }
    }
  }
  rateLimit{
    remaining
    resetAt
  }
}