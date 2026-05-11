"""
food_detector_headless.py
==========================
Versão headless do food-detector do ContaCerto.
Adaptada para rodar em VM e Docker (sem câmera, sem interface gráfica).

Funciona de 2 modos:
  1. Com imagens locais: processa imagens de uma pasta
  2. Com imagens sintéticas: gera imagens aleatórias para simular carga

Faz chamadas à API Roboflow para inferência, gerando carga real de
CPU, memória e rede — exatamente como o sistema em produção.

Uso:
    python food_detector_headless.py --modo sintetico --duracao 300
    python food_detector_headless.py --modo imagens --pasta ./imagens_teste --duracao 300
"""

import cv2
import numpy as np
import threading
import time
import os
import json
import argparse
from collections import Counter
from datetime import datetime

# ============================================================
#  CONFIGURAÇÃO DO MODELO ROBOFLOW
# ============================================================
try:
    from inference_sdk import InferenceHTTPClient
    ROBOFLOW_DISPONIVEL = True
except ImportError:
    ROBOFLOW_DISPONIVEL = False
    print("[AVISO] inference_sdk não instalado. Rodando em modo simulação local.")

API_URL = "https://detect.roboflow.com"
API_KEY = "TadbagVLz73yXH0tRlyT"
MODEL_ID = "first-deliver-model-version/1"
CLASSES_ALVO = ['rice', 'bean', 'pasta']


def criar_cliente_roboflow():
    """Cria o cliente de inferência do Roboflow."""
    if ROBOFLOW_DISPONIVEL:
        return InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)
    return None


def gerar_imagem_sintetica(largura=640, altura=480):
    """
    Gera uma imagem sintética com formas coloridas que simulam
    pacotes de alimentos. Isso gera carga real de CPU (processamento
    de imagem com OpenCV/numpy).
    """
    # Fundo com ruído (simula textura)
    img = np.random.randint(180, 230, (altura, largura, 3), dtype=np.uint8)

    # Adicionar formas que simulam pacotes de alimentos
    num_objetos = np.random.randint(3, 8)
    for _ in range(num_objetos):
        # Retângulos coloridos (simulando pacotes)
        x1 = np.random.randint(0, largura - 100)
        y1 = np.random.randint(0, altura - 100)
        x2 = x1 + np.random.randint(60, 150)
        y2 = y1 + np.random.randint(60, 150)

        cor = tuple(int(c) for c in np.random.randint(0, 255, 3))
        cv2.rectangle(img, (x1, y1), (x2, y2), cor, -1)

        # Adicionar texto simulando rótulos
        cv2.putText(img, "PKG", (x1 + 10, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Aplicar blur para parecer mais natural
    img = cv2.GaussianBlur(img, (5, 5), 0)

    return img


def carregar_imagens_pasta(pasta):
    """Carrega imagens de uma pasta local."""
    extensoes = ('.jpg', '.jpeg', '.png', '.bmp')
    imagens = []
    if os.path.exists(pasta):
        for arquivo in os.listdir(pasta):
            if arquivo.lower().endswith(extensoes):
                caminho = os.path.join(pasta, arquivo)
                img = cv2.imread(caminho)
                if img is not None:
                    imagens.append((arquivo, img))
    return imagens


def processar_resultado(resultado, nome_imagem=""):
    """Processa e exibe o resultado da inferência."""
    predictions = resultado.get("predictions", [])
    itens = []

    for pred in predictions:
        classe = pred.get("class", "desconhecido")
        conf = pred.get("confidence", 0.0)
        if classe in CLASSES_ALVO:
            itens.append(classe)

    contagem = Counter(itens)
    return contagem, len(predictions)


def inferencia_simulada(imagem):
    """
    Simulação local de inferência quando a API Roboflow não está disponível.
    Executa processamento de imagem pesado para gerar carga real.
    """
    # Processamento pesado para simular carga de IA
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Operações de processamento de imagem adicionais (geram carga CPU)
    blur = cv2.GaussianBlur(imagem, (15, 15), 0)
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])

    # Operações numpy pesadas
    resized = cv2.resize(imagem, (640, 640))
    normalized = resized.astype(np.float32) / 255.0
    batch = np.stack([normalized] * 4)  # Simular batch processing
    _ = np.mean(batch, axis=0)
    _ = np.std(batch, axis=0)

    # Simular resultado
    num_deteccoes = min(len(contours) // 10, 5)
    predictions = []
    for i in range(num_deteccoes):
        classe = np.random.choice(CLASSES_ALVO)
        predictions.append({
            "class": classe,
            "confidence": round(np.random.uniform(0.6, 0.98), 2),
            "x": int(np.random.randint(50, 500)),
            "y": int(np.random.randint(50, 400)),
            "width": int(np.random.randint(50, 150)),
            "height": int(np.random.randint(50, 150))
        })

    return {"predictions": predictions}


def executar_detector(modo='sintetico', pasta_imagens=None, duracao=300, log_file='food_detector_log.json'):
    """
    Executa o detector de alimentos em modo headless.

    Args:
        modo: 'sintetico' (gera imagens) ou 'imagens' (usa pasta)
        pasta_imagens: pasta com imagens (modo 'imagens')
        duracao: duração em segundos
        log_file: arquivo de log JSON
    """
    cliente = criar_cliente_roboflow()

    print("=" * 70)
    print("  FOOD DETECTOR HEADLESS - ContaCerto / Radonix")
    print("=" * 70)
    print(f"  Modo:           {modo}")
    print(f"  API Roboflow:   {'Conectada' if cliente else 'Simulação local'}")
    print(f"  Modelo:         {MODEL_ID}")
    print(f"  Classes alvo:   {CLASSES_ALVO}")
    print(f"  Duração:        {duracao}s ({duracao // 60} min)")
    print("=" * 70)
    print()

    # Carregar imagens se modo 'imagens'
    imagens_locais = []
    if modo == 'imagens' and pasta_imagens:
        imagens_locais = carregar_imagens_pasta(pasta_imagens)
        print(f"  Imagens carregadas: {len(imagens_locais)}")
        if len(imagens_locais) == 0:
            print("  [AVISO] Nenhuma imagem encontrada. Usando modo sintético.")
            modo = 'sintetico'

    inicio = time.time()
    contagem_total = Counter()
    total_inferencias = 0
    total_deteccoes = 0
    logs = []

    try:
        while (time.time() - inicio) < duracao:
            iteracao_inicio = time.time()

            # Obter imagem
            if modo == 'imagens' and imagens_locais:
                idx = total_inferencias % len(imagens_locais)
                nome_img, imagem = imagens_locais[idx]
            else:
                imagem = gerar_imagem_sintetica()
                nome_img = f"sintetica_{total_inferencias:04d}.jpg"

            # Executar inferência
            try:
                if cliente:
                    # Salvar imagem temporariamente para enviar à API
                    temp_path = '/tmp/temp_inference.jpg'
                    cv2.imwrite(temp_path, imagem)
                    resultado = cliente.infer(temp_path, model_id=MODEL_ID)
                else:
                    resultado = inferencia_simulada(imagem)
            except Exception as e:
                print(f"  [ERRO API] {e} — Usando simulação local")
                resultado = inferencia_simulada(imagem)

            # Processar resultado
            contagem, n_detectados = processar_resultado(resultado, nome_img)
            contagem_total.update(contagem)
            total_inferencias += 1
            total_deteccoes += n_detectados

            tempo_inferencia = time.time() - iteracao_inicio

            # Log da iteração
            log_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'imagem': nome_img,
                'deteccoes': n_detectados,
                'contagem': dict(contagem),
                'tempo_inferencia_ms': round(tempo_inferencia * 1000, 2)
            }
            logs.append(log_entry)

            # Exibir progresso
            tempo_decorrido = time.time() - inicio
            print(f"  [{log_entry['timestamp']}] "
                  f"Img: {nome_img:30s} | "
                  f"Detectados: {n_detectados:2d} | "
                  f"Tempo: {tempo_inferencia*1000:6.1f}ms | "
                  f"Total: {total_inferencias} ({tempo_decorrido:.0f}s/{duracao}s)")

            # Intervalo entre inferências (simular processamento contínuo)
            time.sleep(max(0, 0.5 - tempo_inferencia))

    except KeyboardInterrupt:
        print("\n  [!] Interrompido pelo usuário.")

    # Relatório final
    tempo_total = time.time() - inicio
    print(f"\n{'=' * 70}")
    print(f"  RELATÓRIO FINAL")
    print(f"{'=' * 70}")
    print(f"  Tempo total:        {tempo_total:.1f}s")
    print(f"  Total inferências:  {total_inferencias}")
    print(f"  Total detecções:    {total_deteccoes}")
    print(f"  Contagem por classe:")
    for classe in CLASSES_ALVO:
        qtd = contagem_total.get(classe, 0)
        print(f"    {classe:10s}: {qtd} unidade(s)")

    if total_inferencias > 0:
        fps = total_inferencias / tempo_total
        print(f"  FPS médio:          {fps:.2f}")

    # Salvar log
    resultado_final = {
        'configuracao': {
            'modo': modo,
            'modelo': MODEL_ID,
            'duracao_configurada': duracao,
            'duracao_real': round(tempo_total, 2),
            'api_roboflow': bool(cliente)
        },
        'metricas': {
            'total_inferencias': total_inferencias,
            'total_deteccoes': total_deteccoes,
            'contagem_total': dict(contagem_total),
            'fps_medio': round(total_inferencias / max(tempo_total, 1), 2)
        },
        'log_inferencias': logs[-20:]  # Últimas 20 entradas
    }

    with open(log_file, 'w') as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)
    print(f"  Log salvo em:       {log_file}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Food Detector Headless - ContaCerto')
    parser.add_argument('--modo', choices=['sintetico', 'imagens'],
                        default='sintetico',
                        help='Modo de operação (padrão: sintetico)')
    parser.add_argument('--pasta', type=str, default=None,
                        help='Pasta com imagens (modo imagens)')
    parser.add_argument('--duracao', type=int, default=300,
                        help='Duração em segundos (padrão: 300)')
    parser.add_argument('--log', type=str, default='food_detector_log.json',
                        help='Arquivo de log JSON')

    args = parser.parse_args()
    executar_detector(
        modo=args.modo,
        pasta_imagens=args.pasta,
        duracao=args.duracao,
        log_file=args.log
    )
