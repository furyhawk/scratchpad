terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "rabbitmq" {
  name         = "rabbitmq:3.12-management"
  keep_locally = false
}

resource "docker_container" "rabbitmq" {
  image = docker_image.rabbitmq.image_id
  name  = "rabbitmq"
  ports {
    internal = 5672
    external = 5672
  }
  ports {
    internal = 15672
    external = 15672
  }
}
