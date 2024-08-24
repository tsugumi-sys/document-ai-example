locals {
  roles_for_ocr = ["roles/documentai.admin", "roles/storage.admin", "roles/serviceusage.serviceUsageConsumer"]
}

data "google_project" "project" {}

resource "google_service_account" "default" {
  account_id = "ocr-example"
}

resource "google_project_iam_member" "default" {
  for_each = toset(local.roles_for_ocr)

  project = data.google_project.project.id
  role    = each.value
  member  = "serviceAccount:${google_service_account.default.email}"
}
