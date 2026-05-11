"""
monitor_recursos.py
====================
Script de monitoramento de recursos do sistema (CPU, memória, disco, rede).
Coleta métricas a cada intervalo configurável e salva em CSV.
Funciona tanto na VM Azure quanto em contêineres Docker.

Uso:
    python monitor_recursos.py --intervalo 2 --duracao 300 --saida dados_monitoramento.csv
"""

import psutil
import time
import csv
import argparse
import os
import platform
from datetime import datetime


def coletar_metricas():
    """Coleta métricas atuais de CPU, memória, disco e rede."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    rede = psutil.net_io_counters()

    metricas = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_percent': cpu_percent,
        'cpu_count': psutil.cpu_count(),
        'memoria_total_mb': round(memoria.total / (1024 ** 2), 2),
        'memoria_usada_mb': round(memoria.used / (1024 ** 2), 2),
        'memoria_percent': memoria.percent,
        'memoria_disponivel_mb': round(memoria.available / (1024 ** 2), 2),
        'disco_total_gb': round(disco.total / (1024 ** 3), 2),
        'disco_usado_gb': round(disco.used / (1024 ** 3), 2),
        'disco_percent': disco.percent,
        'rede_bytes_enviados': rede.bytes_sent,
        'rede_bytes_recebidos': rede.bytes_recv,
        'rede_pacotes_enviados': rede.packets_sent,
        'rede_pacotes_recebidos': rede.packets_recv,
        'processos_ativos': len(psutil.pids()),
        'sistema_operacional': platform.system(),
        'hostname': platform.node()
    }

    return metricas


def monitorar(intervalo=2, duracao=300, arquivo_saida='dados_monitoramento.csv'):
    """
    Executa o monitoramento contínuo por uma duração especificada.

    Args:
        intervalo: segundos entre cada coleta
        duracao: duração total do monitoramento em segundos
        arquivo_saida: caminho do arquivo CSV de saída
    """
    # Garantir que o diretório de saída existe
    os.makedirs(os.path.dirname(arquivo_saida) if os.path.dirname(arquivo_saida) else '.', exist_ok=True)

    campos = [
        'timestamp', 'cpu_percent', 'cpu_count',
        'memoria_total_mb', 'memoria_usada_mb', 'memoria_percent', 'memoria_disponivel_mb',
        'disco_total_gb', 'disco_usado_gb', 'disco_percent',
        'rede_bytes_enviados', 'rede_bytes_recebidos',
        'rede_pacotes_enviados', 'rede_pacotes_recebidos',
        'processos_ativos', 'sistema_operacional', 'hostname'
    ]

    arquivo_existe = os.path.exists(arquivo_saida)

    print("=" * 70)
    print("  MONITOR DE RECURSOS - ContaCerto / Radonix")
    print("=" * 70)
    print(f"  Hostname:          {platform.node()}")
    print(f"  Sistema:           {platform.system()} {platform.release()}")
    print(f"  CPUs:              {psutil.cpu_count()}")
    print(f"  Memória Total:     {round(psutil.virtual_memory().total / (1024**2), 2)} MB")
    print(f"  Intervalo Coleta:  {intervalo}s")
    print(f"  Duração Total:     {duracao}s ({duracao // 60} min)")
    print(f"  Arquivo Saída:     {arquivo_saida}")
    print("=" * 70)
    print()

    inicio = time.time()
    contagem = 0

    with open(arquivo_saida, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if not arquivo_existe:
            writer.writeheader()

        try:
            while (time.time() - inicio) < duracao:
                metricas = coletar_metricas()
                writer.writerow(metricas)
                f.flush()  # Garantir escrita imediata
                contagem += 1

                # Exibir no console
                print(f"[{metricas['timestamp']}] "
                      f"CPU: {metricas['cpu_percent']:5.1f}% | "
                      f"MEM: {metricas['memoria_percent']:5.1f}% ({metricas['memoria_usada_mb']:.0f}MB) | "
                      f"DISCO: {metricas['disco_percent']:5.1f}% | "
                      f"PROCS: {metricas['processos_ativos']}")

                time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\n\n[!] Monitoramento interrompido pelo usuário.")

    tempo_total = time.time() - inicio
    print(f"\n{'=' * 70}")
    print(f"  Monitoramento finalizado!")
    print(f"  Total de coletas:  {contagem}")
    print(f"  Tempo total:       {tempo_total:.1f}s")
    print(f"  Arquivo salvo em:  {arquivo_saida}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor de Recursos do Sistema')
    parser.add_argument('--intervalo', type=int, default=2,
                        help='Intervalo entre coletas em segundos (padrão: 2)')
    parser.add_argument('--duracao', type=int, default=300,
                        help='Duração total do monitoramento em segundos (padrão: 300 = 5 min)')
    parser.add_argument('--saida', type=str, default='dados_monitoramento.csv',
                        help='Arquivo CSV de saída (padrão: dados_monitoramento.csv)')

    args = parser.parse_args()
    monitorar(intervalo=args.intervalo, duracao=args.duracao, arquivo_saida=args.saida)
