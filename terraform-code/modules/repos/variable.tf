
variable "repos" {
  description = "List of repositories to create"
  type        = map(any)

  validation {
    condition     = length(var.repos) <= 1000
    error_message = "The number of repositories must be less than or equal to 1000"
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
