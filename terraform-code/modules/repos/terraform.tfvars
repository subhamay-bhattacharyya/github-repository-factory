repo_max = 2
env      = "dev"
repos = {
  infra = {
    lang     = "terraform",
    filename = "main.tf"
  },
  backend = {
    lang     = "python",
    filename = "main.py"
  },
}