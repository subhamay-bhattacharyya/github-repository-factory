output "repository-names" {
  value = [for repo in github_repository.this : repo.name]
}

# output "repos" {
#   value = var.repos
# }