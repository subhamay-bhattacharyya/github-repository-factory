resource "github_repository" "this" {
  for_each               = var.repos
  name                   = each.key
  description            = "${each.value.description} using ${each.value.iac}."
  visibility             = each.value.visibility
  homepage_url           = each.value.html-url
  auto_init              = true
  has_issues             = true
  has_projects           = true
  delete_branch_on_merge = true
  topics                 = each.value.topics

  template {
    owner      = "subhamay-bhattacharyya"
    repository = each.value.template
  }
}
