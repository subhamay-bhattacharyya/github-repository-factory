locals {
  raw_repositories = jsondecode(file("${path.module}/repo-json/github-repo-test.json"))

  repositories = merge(
    # splat the flattened list into individual arguments for merge()
    # i.e., turn [map1, map2, ...] => merge(map1, map2, ...)
    flatten([
      for id, item in local.raw_repositories : [
        for iac_type in item.iac : {
          "${id}-${item.category}-${iac_type}" = {
            workshop    = item.workshop
            category    = item.category
            description = item.description
            template    = iac_type == "tf" ? "terraform-template" : "cloudformation-template"
            status      = item.status
            priority    = item.priority
            html_url    = item["html-url"]
            visibility  = item.visibility
          }
        }
      ]
    ])...
  )
}

output "repositories" {
  value = local.repositories
}

