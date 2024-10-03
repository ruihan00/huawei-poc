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

# SSL certificates
resource "google_certificate_manager_certificate" "cert-mooo" {
  name        = "cert-mooo"
  location = "global"

  managed {
    domains = [var.domain-mooo]
    dns_authorizations = [google_certificate_manager_dns_authorization.dns-auth-mooo.id]
  }
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
resource "google_certificate_manager_dns_authorization" "dns-auth-mooo" {
  name        = "dns-auth-mooo"
  location    = "global"
  domain      = var.domain-mooo
}
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

resource "google_certificate_manager_certificate_map_entry" "cert-map-entry-dedyn" {
  name        = "cert-map-entry-dedyn"
  map = google_certificate_manager_certificate_map.default.name 
  certificates = [ google_certificate_manager_certificate.cert-dedyn.id ]
  matcher = "PRIMARY"
}


