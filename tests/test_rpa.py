from src.rpa import classify, process

def test_critical():
    assert classify(65, True, False)[0] == 'critico'

def test_low():
    assert classify(0, False, False)[0] == 'baixo'

def test_mixed_batch():
    res = process([
        {'point_id': 'A', 'precip_mm_24h': 55, 'obstruction': True, 'accumulated_water': False},
        {'point_id': 'A', 'precip_mm_24h': 0, 'obstruction': False, 'accumulated_water': False},
        {'point_id': 'B', 'precip_mm_24h': -1, 'obstruction': False, 'accumulated_water': False}])
    assert res['summary'] == {'processed': 3, 'succeeded': 1, 'failed': 2}
