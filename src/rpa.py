"""DrenaHub: avaliação determinística e auditável de pontos de drenagem."""
import json, logging, os, sys
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger('drenahub.rpa')

def classify(precip_mm_24h: float, obstruction: bool, accumulated_water: bool) -> tuple[str, list[str]]:
    if precip_mm_24h < 0 or precip_mm_24h > 1000:
        raise ValueError('Precipitação fora da faixa válida')
    factors = []
    if precip_mm_24h >= 50: factors.append('chuva_intensa')
    elif precip_mm_24h >= 20: factors.append('chuva_moderada')
    if obstruction: factors.append('possivel_obstrucao')
    if accumulated_water: factors.append('agua_acumulada')
    if precip_mm_24h >= 50 and (obstruction or accumulated_water): level = 'critico'
    elif (precip_mm_24h >= 20 and (obstruction or accumulated_water)) or (obstruction and accumulated_water): level = 'alto'
    elif precip_mm_24h >= 20 or obstruction or accumulated_water: level = 'moderado'
    else: level = 'baixo'
    return level, factors

def process(items: list[dict], timestamp: str | None = None) -> dict:
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    results, errors, seen = [], [], set()
    for idx, item in enumerate(items):
        try:
            point = str(item['point_id']).strip()
            if not point: raise ValueError('point_id vazio')
            if point in seen: raise ValueError('point_id duplicado')
            seen.add(point)
            rain = float(item['precip_mm_24h'])
            if not isinstance(item['obstruction'], bool) or not isinstance(item['accumulated_water'], bool):
                raise ValueError('Indicadores devem ser booleanos')
            priority, factors = classify(rain, item['obstruction'], item['accumulated_water'])
            results.append({'point_id': point, 'priority': priority, 'factors': factors, 'evaluated_at': timestamp})
        except (KeyError, TypeError, ValueError) as err:
            errors.append({'item_index': idx, 'error_type': type(err).__name__, 'message': str(err)})
    summary = {'processed': len(items), 'succeeded': len(results), 'failed': len(errors)}
    LOG.info('rpa_batch %s', json.dumps(summary))
    return {'summary': summary, 'results': results, 'errors': errors}

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    source = Path(os.getenv('INPUT_FILE', 'data/input.json'))
    dest = Path(os.getenv('OUTPUT_FILE', 'data/priorities.json'))
    try:
        raw = json.loads(source.read_text(encoding='utf-8'))
        if not isinstance(raw, list): raise ValueError('Entrada deve ser lista JSON')
        outcome = process(raw)
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_suffix(dest.suffix + '.tmp')
        temp.write_text(json.dumps(outcome, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(dest)
        print(json.dumps(outcome['summary']))
        return 0 if outcome['summary']['failed'] == 0 else 2
    except (OSError, ValueError, json.JSONDecodeError) as err:
        LOG.exception('Falha do lote: %s', type(err).__name__)
        return 1

if __name__ == '__main__': sys.exit(main())
