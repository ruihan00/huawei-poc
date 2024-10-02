# Create a Google-managed SSL certificate for the Load Balancer
resource "google_compute_managed_ssl_certificate" "default" {
  name = "binacloud-ssl-cert"
  
  managed {
    domains = [
      # "binacloud.mooo.com"
      "binacloud.heyzec.dedyn.io"
    ]
  }
}

# Create an unmanaged instance group and add your existing Compute Engine instance
resource "google_compute_instance_group" "default" {
  name = "minimal-instance-group"
  instances = [
    google_compute_instance.server.self_link
  ]
  named_port {
    name = "http"
    port = 8000
  }
}

# Create a backend service that uses the instance group as its backend
resource "google_compute_backend_service" "default" {
  name                  = "minimal-backend-service"
  load_balancing_scheme = "EXTERNAL"
  protocol              = "HTTP"
  timeout_sec           = 30
  backend {
    group = google_compute_instance_group.default.self_link
  }
  # Use the named port defined in the instance group
  port_name = "http"
  health_checks = [google_compute_http_health_check.default.self_link]
}

# Create a URL map to route traffic to the backend service
resource "google_compute_url_map" "default" {
  name            = "minimal-url-map"
  default_service = google_compute_backend_service.default.self_link
}

# Create a target HTTPS proxy for SSL termination
resource "google_compute_target_https_proxy" "default" {
  name             = "minimal-https-proxy"
  url_map          = google_compute_url_map.default.self_link
  ssl_certificates = [google_compute_managed_ssl_certificate.default.self_link]
}

# Create a global forwarding rule to listen on port 443 (HTTPS)
resource "google_compute_global_forwarding_rule" "default" {
  name       = "minimal-https-forwarding-rule"
  target     = google_compute_target_https_proxy.default.self_link
  port_range = "443"
  load_balancing_scheme = "EXTERNAL"
}

# Create a basic HTTP health check to monitor instance health
resource "google_compute_http_health_check" "default" {
  name               = "minimal-health-check"
  port               = 8000
  request_path       = "/"
  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold  = 2
  unhealthy_threshold = 2
}

