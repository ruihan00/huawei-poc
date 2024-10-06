# Due to a bug, specify all regions here as global
# https://github.com/hashicorp/terraform-provider-google/issues/19437
variable "domain-mooo" {
  type        = string
  default     = "binacloud.mooo.com"
}
variable "domain-dedyn" {
  type        = string
  default     = "binacloud.heyzec.dedyn.io"
}

resource "google_certificate_manager_certificate" "cert-dedyn" {
  name        = "cert-dedyn"
  location = "global"

  managed {
    domains = [var.domain-dedyn]
    dns_authorizations = [google_certificate_manager_dns_authorization.dns-auth-dedyn.id]
  }
}

# Validate certificates with DNS authorisation
resource "google_certificate_manager_dns_authorization" "dns-auth-dedyn" {
  name        = "dns-auth-dedyn"
  location    = "global"
  domain      = var.domain-dedyn
}

# Create a map with entries to be used by proxy
resource "google_certificate_manager_certificate_map" "default" {
  name        = "cert-map"
  labels      = {
    "terraform" : true,
    "acc-test"  : true,
  }
}

resource "google_certificate_manager_certificate_map_entry" "cert-map-entry-mooo" {
  name         = "cert-map-entry-mooo"
  map          = google_certificate_manager_certificate_map.default.name
  certificates = [
    # This is a self-managed cert, it is added from the console
    "projects/${var.project_id}/locations/global/certificates/cert-mooo"
  ]
  hostname = var.domain-mooo
}

resource "google_certificate_manager_certificate_map_entry" "cert-map-entry-dedyn" {
  name         = "cert-map-entry-dedyn"
  map          = google_certificate_manager_certificate_map.default.name
  certificates = [
    google_certificate_manager_certificate.cert-dedyn.id,
  ]
  hostname = var.domain-dedyn
}


