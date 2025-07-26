module "repositories" {
  source = "./modules/repos"
  repos  = local.repositories
}
