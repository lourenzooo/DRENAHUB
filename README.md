# DrenaHub — Robotic Process Automation (RPA)

MVP demonstrativo para triagem automática de pontos de drenagem. Dados de entrada simulados: precipitação de 24 h, indicador de possível obstrução e água acumulada. A saída é um arquivo estruturado de prioridades consumível pela API do MVP. **Não representa previsão hidrológica validada**.

## Estrutura
- `src/rpa.py`: motor de classificação, validação e processamento de lote
- `src/app.py`: API FastAPI com `GET /priorities` para consumir saída
- `data/input.json`: lote de exemplo
- `data/priorities.json`: resultado gerado
- `tests/test_rpa.py`: três testes automatizados
- `docs/fluxo_rpa.png`: fluxograma simplificado do processo (não é BPMN formal)
- `logs/`: evidências textuais locais sem dados pessoais

## Como executar
Pré-requisito: Python 3.10+.

```bash
python src/rpa.py
python -m pytest tests/test_rpa.py -q
pip install fastapi uvicorn prometheus-client
OUTPUT_FILE=data/priorities.json uvicorn src.app:app --port 8000
```

Acesse `http://localhost:8000/priorities` após iniciar a API. No Windows PowerShell, defina o ambiente com `$env:OUTPUT_FILE='data/priorities.json'` antes do último comando. Para executar os testes, instale `pytest` se ainda não estiver disponível.

## Regras ilustrativas
- Crítico: chuva >= 50 mm/24 h com obstrução ou água acumulada
- Alto: chuva >= 20 mm/24 h com obstrução/água, ou dois sinais locais simultâneos
- Moderado: chuva >= 20 mm/24 h ou apenas um sinal local
- Baixo: demais casos

Os limiares são *hipóteses de demonstração*, sujeitos a validação com especialistas.

## Exceções e auditoria
- Lote ausente ou JSON inválido: erro fatal e saída 1.
- Item sem campo, dado inválido ou ID duplicado: item rejeitado, lote segue, saída 2 se houver falhas parciais.
- Logs informam data/hora, contagens e falhas sem divulgar fotos ou dados pessoais.

## Antes da entrega à FIAP
- Criar o BPMN **formal** com eventos, gateways e raias, se exigido pelo professor; o PNG fornecido é um fluxograma técnico.
- Registrar vídeo de até 3 minutos com início, decisão, erro, logs e consumo em `/priorities`.
- Capturar prints da API e teste de falha e colocá-los em `assets/`.
- Publicar repositório público GitHub e preencher integrantes/RMs, link do vídeo e PDF final.
- O endpoint de demonstração não possui autenticação: não publique dados reais ou sensíveis sem controles de acesso.

## Execução da API com Docker (Secure DevOps)

Na pasta principal do projeto, com o Docker Desktop em execução:

```powershell
docker compose up --build -d
docker compose ps
```

Verifique `http://localhost:8000/health`, `http://localhost:8000/priorities` e `http://localhost:8000/docs`.
O `compose.yaml` monta `./data` somente para leitura no contêiner; assim, a API lê as prioridades atualizadas pelo RPA executado no computador. A porta 8000 está exposta apenas no próprio computador para testes locais. Se houver outro Uvicorn rodando nessa porta, interrompa-o antes.

Para parar: `docker compose down`. Estes arquivos apenas preparam a etapa de contêiner; pipeline CI/CD, Terraform, publicação em nuvem e observabilidade com alerta ainda precisam ser configurados e testados.
