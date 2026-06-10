resource "google_compute_network" "vpc" {
  name                    = "quantam-vpc-new"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "quantam-subnet-new"
  ip_cidr_range = "10.0.1.0/24"

  region  = var.region
  network = google_compute_network.vpc.id
}
