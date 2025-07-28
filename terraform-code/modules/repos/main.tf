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
  content = templatefile(local.readme-template,
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
  content = templatefile(local.contributing-template,
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
  content = templatefile(local.package-template,
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
  content = templatefile(local.changelog-template,
    {
      repo-name = github_repository.this[each.key].name
    }
  )
}

# CI Build workflow
resource "github_repository_file" "ci-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/workflows/ci.yaml"
  overwrite_on_create = true
  content = file(
    each.value.template == "terraform-template" ? local.tf-ci-workflow-template : local.cfn-ci-workflow-template
  )
}

# Create branch workflow
resource "github_repository_file" "create-branch-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/workflows/create-branch.yaml"
  overwrite_on_create = true
  content = file(
    each.value.template == "terraform-template" ? local.tf-create-branch-template : local.cfn-create-branch-template
  )
}


# Create release workflow
resource "github_repository_file" "create-release-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/workflows/create-release.yaml"
  overwrite_on_create = true
  content = file(
    each.value.template == "terraform-template" ? local.tf-create-release-workflow-template : local.cfn-create-release-workflow-template
  )
}

# Create stack workflow
resource "github_repository_file" "deploy-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = each.value.template == "terraform-template" ? ".github/workflows/terraform-apply.yaml" : ".github/workflows/cloudformation-deploy.yaml"
  overwrite_on_create = true
  content = file(
    each.value.template == "terraform-template" ? local.tf-apply-workflow-template : local.cfn-deploy-workflow-template
  )
}


# Destroy stack workflow
resource "github_repository_file" "destroy-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = each.value.template == "terraform-template" ? ".github/workflows/terraform-destroy.yaml" : ".github/workflows/cloudformation-delete.yaml"
  overwrite_on_create = true
  content = file(
    each.value.template == "terraform-template" ? local.tf-destroy-workflow-template : local.cfn-delete-workflow-template
  )
}

# Slack notification workflow
resource "github_repository_file" "slack-notification-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/workflows/notify.yaml"
  overwrite_on_create = true
  content             = file(local.slack-notification-template)
}

# Setup environment workflow
resource "github_repository_file" "setup-environment-workflow" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/workflows/setup-environments.yaml"
  overwrite_on_create = true
  content             = file(local.setup-environment-template)
}

# Dependabot workflow
resource "github_repository_file" "dependabot" {

  for_each            = var.repos
  repository          = github_repository.this[each.key].name
  branch              = "main"
  file                = ".github/dependabot.yaml"
  overwrite_on_create = true
  content             = file(local.dependabot-template)
}
