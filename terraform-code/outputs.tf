# output "repos-to-create" {
#   value = local.repos-to-create
# }

output "repositories" {
  value = local.repositories
}

output "repository-names" {
  value = module.repositories.repository-names
}