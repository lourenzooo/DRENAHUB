
resource "render_web_service" "drenahub" {
  name   = "drenahub-api"
  plan   = "free"
  region = "virginia"

  # Ambiente existente no Render
  environment_id = "evm-dbv10p8m7kps739to6d0"

  # Endpoint de verificacao da API
  health_check_path = "/health"

  # Configuracao do projeto no GitHub
  runtime_source = {
    docker = {
      repo_url        = "https://github.com/lourenzooo/DRENAHUB"
      branch          = "main"
      dockerfile_path = "Dockerfile"
      context         = "."
      auto_deploy     = false
    }
  }

  # Variavel de ambiente existente no Render
  env_vars = {
    port = {
      value = "8000"
    }
  }

  # Protecao contra exclusao acidental
  lifecycle {
    prevent_destroy = true

    # Preserva as variaveis existentes
    ignore_changes = [
      env_vars
    ]
  }
}
