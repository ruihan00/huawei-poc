# See https://cloud.google.com/load-balancing/docs/https/setting-up-http-https-redirect#for_existing_load_balancers


resource "google_compute_global_forwarding_rule" "http-redirect" {
  name       = "http-redirect"
  ip_address = google_compute_global_address.default.address
  target     = google_compute_target_http_proxy.http-redirect.self_link
  port_range = "80"
  load_balancing_scheme = "EXTERNAL"
}

resource "google_compute_target_http_proxy" "http-redirect" {
  name    = "http-redirect"
  url_map = google_compute_url_map.http-redirect.id
}

resource "google_compute_url_map" "http-redirect" {
  name = "http-redirect"

  default_url_redirect {
    https_redirect = true
    strip_query = false
  }
}

