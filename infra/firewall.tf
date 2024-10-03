resource "google_compute_firewall" "server_ingress" {
  name    = "server-http"
  network = google_compute_network.this.id

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags = [ "server" ]
}

resource "google_compute_firewall" "server_allow_ssh" {
  name      = "server-allow-ssh"
  network   = google_compute_network.this.id
  direction = "INGRESS"

  allow {
    ports    = ["22"]
    protocol = "tcp"
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags = [ "server" ]
}

