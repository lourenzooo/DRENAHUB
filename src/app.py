"""API demonstrativa do MVP; consome arquivo de saída do RPA."""
import json, os, time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

app = FastAPI(title='DrenaHub MVP - API demonstrativa')
REQUESTS = Counter('drenahub_http_requests_total', 'Número de requisições', ['route', 'status'])
LATENCY = Histogram('drenahub_http_request_duration_seconds', 'Latência de requisições', ['route'])
START = time.monotonic()

@app.get('/health')
def health():
    REQUESTS.labels('health', '200').inc()
    return {'status': 'ok'}

@app.get('/priorities')
def priorities():
    start=time.monotonic()
    path=Path(os.getenv('OUTPUT_FILE', '/app/data/priorities.json'))
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        REQUESTS.labels('priorities','200').inc()
        return data
    except (OSError, json.JSONDecodeError):
        REQUESTS.labels('priorities','503').inc()
        raise HTTPException(503, 'Arquivo de prioridades indisponível')
    finally: LATENCY.labels('priorities').observe(time.monotonic()-start)

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
