FROM python:3.11-slim

LABEL maintainer="Radonix - ContaCerto"
LABEL description="ContaCerto Food Detector + Monitoramento de Recursos com IA"

WORKDIR /app

# Instalar dependências do sistema (OpenCV precisa de libGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os scripts
COPY food_detector_headless.py .
COPY monitor_recursos.py .
COPY gerar_carga.py .
COPY modelo_ia_docker.py .

# Criar diretórios de saída
RUN mkdir -p /app/dados /app/graficos_docker /app/resultados_docker

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Comando padrão: rodar o food detector headless (a carga principal)
CMD ["python", "food_detector_headless.py", "--modo", "sintetico", "--duracao", "300"]
