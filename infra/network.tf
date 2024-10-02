resource "google_compute_network" "this" {
  auto_create_subnetworks = false
  name                    = "sg-transit-aid-network"
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "this" {
  name          = "sg-transit-aid-subnet"
  ip_cidr_range = "192.168.24.0/24"
  region        = "asia-southeast1"
  network       = google_compute_network.this.id
}
