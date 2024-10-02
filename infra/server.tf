resource "google_compute_instance" "server" {
  name         = "server"
  machine_type = "g2-standard-16"

  network_interface {
    subnetwork = google_compute_subnetwork.this.name
    # Assign external IP
    access_config {}
  }

  boot_disk {
    source = resource.google_compute_disk.boot-disk.self_link
    auto_delete = false
  }

  metadata_startup_script = file("server-startup.sh")


  # Required by provider because our instance is GPU
  scheduling {
    on_host_maintenance = "TERMINATE"
  }

  tags         = [ "server" ]
}

resource "google_compute_disk" "boot-disk" {
  name = "server-disk"
  image = "deeplearning-platform-release/common-gpu-v20240922-debian-11"
}


