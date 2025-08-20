terraform {
  backend "local" {
    path = "../terraform-state-4/terraform.tfstate"
  }
}