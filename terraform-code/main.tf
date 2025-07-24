resource "github_repository" "mtc_repo" {
  name        = "mtc-repo"
  description = "Code for MTC"

  visibility = "public"
  auto_init  = true
}

resource "github_repository_file" "readme" {
  repository          = github_repository.mtc_repo.name
  branch              = "main"
  file                = "README.md"
  content             = "# This repository is for infra developers."
  overwrite_on_create = true
}


resource "github_repository_file" "index_html" {
  repository          = github_repository.mtc_repo.name
  branch              = "main"
  file                = "index.html"
  content             = "Hello, World! This is the MTC repository."
  overwrite_on_create = true
}