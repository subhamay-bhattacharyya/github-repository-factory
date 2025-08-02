locals {
  raw-repositories = jsondecode(file("${path.module}/repo-json/github-repo-test.json"))

  gist-ids = jsondecode(file("${path.module}/repo-json/gist-id.json"))

  repositories = merge(
    # splat the flattened list into individual arguments for merge()
    # i.e., turn [map1, map2, ...] => merge(map1, map2, ...)
    flatten([
      for id, item in local.raw-repositories : [
        for iac-type in item.iac : {
          "${id}-${item.category}-${iac-type}" = {
            workshop    = item.workshop
            category    = item.category
            description = item.description
            template    = iac-type == "tf" ? "terraform-template" : "cloudformation-template"
            iac         = iac-type == "tf" ? "Terraform" : "CloudFormation"
            gist-id     = local.gist-ids["${id}-${item.category}-${iac-type}"]["id"]
            status      = item.status
            priority    = item.priority
            html-url    = item["html-url"]
            visibility  = item.visibility
            topics = [
              "auto-generated",
              iac-type == "tf" ? "terraform" : "cloudformation",
              "aws-workshop",
              item.category
            ]
          }
        }
      ]
    ])...
  )
}

# output "gist-ids" {
#   value = local.gist-ids
# }


# output "repositories" {
#   value = local.repositories
# }

