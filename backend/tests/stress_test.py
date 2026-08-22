import time
import requests
import multiprocessing

__test__ = False  # Script de carga manual, no test unitario de CI

def consume_cpu():
    """Simula carga de CPU intensiva."""
    while True:
        _ = 2 ** 1000

def test_system_reaction():
    print("🚀 Iniciando prueba de estrés local...")
    # 1. Lanzamos procesos para elevar la carga
    processes = [multiprocessing.Process(target=consume_cpu) for _ in range(multiprocessing.cpu_count())]
    for p in processes: p.start()

    try:
        for _ in range(5):
            res = requests.get("http://localhost:8000/api/v1/system/health/hardware")
            data = res.json()
            print(f"📊 CPU: {data['cpu_usage_percent']}% | Saludable: {data['healthy']}")
            time.sleep(2)
    finally:
        # Limpieza absoluta de procesos
        for p in processes: p.terminate()
        print("✅ Prueba finalizada y recursos liberados.")

if __name__ == "__main__":
    test_system_reaction()
