# Reserve a global static IP address
resource "google_compute_global_address" "default" {
  name = "default"
}

# ================================================================================
# 1. Global forwarding rule to listen on port 443 (HTTPS)
# ================================================================================
resource "google_compute_global_forwarding_rule" "default" {
  name       = "default"
  ip_address = google_compute_global_address.default.address
  target     = google_compute_target_https_proxy.default.self_link
  port_range = "443"
  load_balancing_scheme = "EXTERNAL"
}

# ================================================================================
# 2. HTTPS proxy for SSL termination
# ================================================================================
resource "google_compute_target_https_proxy" "default" {
  name             = "default"
  url_map          = google_compute_url_map.default.self_link
  certificate_map = "//certificatemanager.googleapis.com/${google_certificate_manager_certificate_map.default.id}"
}

# ================================================================================
# 3. Route (unencrypted) traffic to respective backend service based on hosts and path
# ================================================================================
resource "google_compute_url_map" "default" {
  name            = "default"
  default_service = google_compute_backend_service.client-service.self_link

  host_rule {
    hosts        = ["*"]
    path_matcher = "default"
  }

  path_matcher {
    name            = "default"
    default_service = google_compute_backend_service.client-service.self_link

    path_rule {
      paths   = ["/server/*"]
      service = google_compute_backend_service.server-service.self_link
    }
  }
}

# ================================================================================
# 4a. Client (cloud run) backend service
# ================================================================================
resource "google_compute_backend_service" "client-service" {
  name                  = "client-service"
  protocol              = "HTTP"
  timeout_sec           = 3600
  backend {
    group = google_compute_region_network_endpoint_group.client-group.self_link
  }
  port_name = "http"
}
resource "google_compute_region_network_endpoint_group" "client-group" {
  name = "client-group"
  region = var.region
  cloud_run {
    service = google_cloud_run_v2_service.client.name
  }
}


# ================================================================================
# 4b. Server (compute engine) backend service
# ================================================================================
resource "google_compute_backend_service" "server-service" {
  name                  = "server-service"
  protocol              = "HTTP"
  timeout_sec           = 30
  backend {
    group = google_compute_instance_group.server-group.self_link
  }
  port_name = "http"
  health_checks = [google_compute_http_health_check.server-health-check.self_link]
}
resource "google_compute_instance_group" "server-group" {
  name = "server-group"
  instances = var.save-money ? [] : [
    google_compute_instance.server.0.self_link
  ]
  named_port {
    name = "http"
    port = 8000
  }
}
# Health check is needed for compute instances
resource "google_compute_http_health_check" "server-health-check" {
  name               = "server-health-check"
  port               = 8000
  request_path       = "/server/healthcheck"
  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold  = 2
  unhealthy_threshold = 2
}

