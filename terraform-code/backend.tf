terraform {
  backend "local" {
    path = "../terraform-state-5/terraform.tfstate"
  }
}