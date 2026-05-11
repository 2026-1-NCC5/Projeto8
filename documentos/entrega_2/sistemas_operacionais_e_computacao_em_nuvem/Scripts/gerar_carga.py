"""
gerar_carga.py - Gera carga artificial no sistema para monitoramento.
Uso: python gerar_carga.py --tipo misto --duracao 300
"""
import multiprocessing, threading, time, argparse, os

def carga_cpu(duracao=30):
    print(f"  [CPU] Carga por {duracao}s...")
    fim = time.time() + duracao
    while time.time() < fim:
        _ = sum(i * i for i in range(100000))
    print(f"  [CPU] Finalizada.")

def carga_memoria(tamanho_mb=200, duracao=30):
    print(f"  [MEM] Alocando {tamanho_mb}MB por {duracao}s...")
    try:
        blocos = [bytearray(1024 * 1024) for _ in range(tamanho_mb)]
        time.sleep(duracao)
        del blocos
    except MemoryError:
        print("  [MEM] Erro: memoria insuficiente!")
    print(f"  [MEM] Liberada.")

def ciclo_normal(duracao=60):
    print(f"\n  MODO: NORMAL ({duracao}s)")
    time.sleep(duracao)

def ciclo_estresse(duracao=60):
    print(f"\n  MODO: ESTRESSE ({duracao}s)")
    threads = []
    for i in range(min(multiprocessing.cpu_count(), 4)):
        t = threading.Thread(target=carga_cpu, args=(duracao,))
        threads.append(t)
    t_mem = threading.Thread(target=carga_memoria, args=(150, duracao))
    threads.append(t_mem)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def ciclo_misto(duracao_total=300):
    print(f"\n  GERADOR DE CARGA MISTO - Duracao: {duracao_total}s")
    ciclo, tempo_gasto = 0, 0
    duracao_ciclo = duracao_total // 5
    while tempo_gasto < duracao_total:
        ciclo += 1
        d = min(duracao_ciclo, duracao_total - tempo_gasto)
        if ciclo % 2 == 1:
            ciclo_normal(d)
        else:
            ciclo_estresse(d)
        tempo_gasto += d
    print(f"\n  Carga finalizada!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gerador de Carga')
    parser.add_argument('--tipo', choices=['normal','estresse','misto'], default='misto')
    parser.add_argument('--duracao', type=int, default=300)
    args = parser.parse_args()
    if args.tipo == 'normal': ciclo_normal(args.duracao)
    elif args.tipo == 'estresse': ciclo_estresse(args.duracao)
    else: ciclo_misto(args.duracao)
