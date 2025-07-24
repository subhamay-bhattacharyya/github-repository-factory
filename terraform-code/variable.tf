variable "repo_max" {
  description = "Maximum number of repositories to create"
  type        = number
  default     = 2

  validation {
    condition     = var.repo_max <= 10
    error_message = "Do not deploy more than 10 repos."
  }
}

variable "repos" {
  description = "List of repositories to create"
  type        = set(string)

  validation {
    condition     = length(var.repos) <= 10
    error_message = "The number of repositories must be less than or equal to the repo_max"
  }
}

variable "env" {
  description = "Environment for the repositories"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "The env variable must be either 'dev' or 'prod'."
  }
}
