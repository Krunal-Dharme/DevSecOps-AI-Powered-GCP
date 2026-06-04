resource "google_container_cluster" "gke" {

  name     = "quantam-gke"
  location = var.region

  deletion_protection = false

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
}

resource "google_container_node_pool" "primary_nodes" {

  name     = "primary-nodepool"
  cluster  = google_container_cluster.gke.name
  location = var.region

  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }

  node_config {

    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
