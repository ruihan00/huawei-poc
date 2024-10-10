resource "google_compute_instance" "server" {
  count = var.save-money ? 0 : 1
  name         = "server"
  machine_type = "g2-standard-32"
  allow_stopping_for_update = true  # Otherwise we can't update it inplace!

  network_interface {
    subnetwork = google_compute_subnetwork.this.name
    # Assign external IP
    access_config {}
  }

  boot_disk {
    source = google_compute_disk.boot-disk.self_link
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
  zone  = "asia-southeast1-a"
  image = "deeplearning-platform-release/common-gpu-v20240922-debian-11"
  size = 800  # 100 GB, the default of 50 GB is not enough
}

