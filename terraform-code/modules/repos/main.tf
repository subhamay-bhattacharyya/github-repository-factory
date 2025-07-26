resource "github_repository" "mtc_repo" {
  for_each    = var.repos
  name        = "${each.key}-${each.value.category}-${each.value.iac}"
  description = "${each.value.description}"
  visibility  = each.value.visibility
  auto_init   = true
}
