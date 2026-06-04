output "aks_cluster_id" {
  value = azurerm_kubernetes_cluster.aks.id
}

output "vnet_id" {
  value = azurerm_virtual_network.vnet.id
}

output "subnet_id" {
  value = azurerm_subnet.subnet.id
}
