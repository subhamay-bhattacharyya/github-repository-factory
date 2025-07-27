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

resource "github_repository_file" "readme" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = "README.md"
  overwrite_on_create = true
  content = templatefile("${path.module}/../../templates/README.tftpl",
    {
      gh-org    = "subhamay-bhattacharyya"
      heading   = each.value.workshop
      repo-name = github_repository.this[each.key].name
      iac       = each.value.iac
      gist-id   = each.value["gist-id"]
      email     = "subhamay.aws@gmail.com"
    }
  )
}

resource "github_repository_file" "contributing" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = "CONTRIBUTING.md"
  overwrite_on_create = true
  content = templatefile("${path.module}/../../templates/CONTRIBUTING.tftpl",
    {
      repo-name = github_repository.this[each.key].name
    }
  )
}

resource "github_repository_file" "package" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = "package.json"
  overwrite_on_create = true
  content = templatefile("${path.module}/../../templates/package.tftpl",
    {
      repo-name   = github_repository.this[each.key].name
      gh-org      = "subhamay-bhattacharyya"
      description = each.value.description

    }
  )
}

resource "github_repository_file" "changelog" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = "CHANGELOG.md"
  overwrite_on_create = true
  content             = file("${path.module}/../../templates/CHANGELOG.tftpl")
}

