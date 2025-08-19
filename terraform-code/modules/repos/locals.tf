locals {
  readme-template       = "${path.module}/../../templates/README.tftpl"
  contributing-template = "${path.module}/../../templates/CONTRIBUTING.tftpl"
  package-template      = "${path.module}/../../templates/package.tftpl"
  changelog-template    = "${path.module}/../../templates/CHANGELOG.tftpl"

  # tf-create-branch-template           = "${path.module}/../../templates/tf-workflows/create-branch.tftpl"
  # tf-ci-workflow-template             = "${path.module}/../../templates/tf-workflows/ci.tftpl"
  # tf-create-release-workflow-template = "${path.module}/../../templates/tf-workflows/create-release.tftpl"
  # tf-apply-workflow-template          = "${path.module}/../../templates/tf-workflows/terraform-apply.tftpl"
  # tf-destroy-workflow-template        = "${path.module}/../../templates/tf-workflows/terraform-destroy.tftpl"

  # cfn-create-branch-template           = "${path.module}/../../templates/cfn-workflows/create-branch.tftpl"
  # cfn-ci-workflow-template             = "${path.module}/../../templates/cfn-workflows/ci.tftpl"
  # cfn-create-release-workflow-template = "${path.module}/../../templates/cfn-workflows/create-release.tftpl"
  # cfn-deploy-workflow-template         = "${path.module}/../../templates/cfn-workflows/cloudformation-deploy.tftpl"
  # cfn-delete-workflow-template         = "${path.module}/../../templates/cfn-workflows/cloudformation-delete.tftpl"

  slack-notification-template = "${path.module}/../../templates/notify.tftpl"
  setup-environment-template  = "${path.module}/../../templates/setup-environments.tftpl"
  dependabot-template         = "${path.module}/../../templates/dependabot.tftpl"
}