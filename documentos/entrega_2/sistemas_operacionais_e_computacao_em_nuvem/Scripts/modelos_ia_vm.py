"""
modelos_ia_vm.py - Modelos de IA para monitoramento na VM Azure
================================================================
Modelo 1: Isolation Forest - Detecção de anomalias em tempo real
Modelo 2: Random Forest - Previsão de esgotamento de recursos
Executa treinamento, avaliação e gera gráficos.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, precision_score, recall_score, f1_score)
from sklearn.preprocessing import StandardScaler
import warnings, os, json
from datetime import datetime

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')

GRAFICOS_DIR = 'graficos_vm'
RESULTADOS_DIR = 'resultados_vm'

def criar_diretorios():
    os.makedirs(GRAFICOS_DIR, exist_ok=True)
    os.makedirs(RESULTADOS_DIR, exist_ok=True)

def carregar_dados(caminho_csv):
    """Carrega e prepara os dados de monitoramento."""
    print("=" * 60)
    print("  CARREGANDO DADOS DE MONITORAMENTO")
    print("=" * 60)
    df = pd.read_csv(caminho_csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"  Registros carregados: {len(df)}")
    print(f"  Periodo: {df['timestamp'].min()} a {df['timestamp'].max()}")
    print(f"  Colunas: {list(df.columns)}")
    print(f"\n  Estatisticas descritivas:")
    print(df[['cpu_percent','memoria_percent','disco_percent']].describe().to_string())
    return df

def gerar_graficos_exploratoria(df):
    """Gera gráficos de análise exploratória dos dados."""
    print("\n  Gerando graficos de analise exploratoria...")

    # 1. Série temporal de CPU, Memória e Disco
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle('Monitoramento de Recursos - VM Azure', fontsize=16, fontweight='bold')

    axes[0].plot(df['timestamp'], df['cpu_percent'], color='#e74c3c', linewidth=1.2)
    axes[0].fill_between(df['timestamp'], df['cpu_percent'], alpha=0.3, color='#e74c3c')
    axes[0].set_ylabel('CPU (%)')
    axes[0].set_title('Uso de CPU ao Longo do Tempo')
    axes[0].axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Limiar Critico (80%)')
    axes[0].legend()

    axes[1].plot(df['timestamp'], df['memoria_percent'], color='#3498db', linewidth=1.2)
    axes[1].fill_between(df['timestamp'], df['memoria_percent'], alpha=0.3, color='#3498db')
    axes[1].set_ylabel('Memoria (%)')
    axes[1].set_title('Uso de Memoria ao Longo do Tempo')
    axes[1].axhline(y=85, color='red', linestyle='--', alpha=0.5, label='Limiar Critico (85%)')
    axes[1].legend()

    axes[2].plot(df['timestamp'], df['disco_percent'], color='#2ecc71', linewidth=1.2)
    axes[2].fill_between(df['timestamp'], df['disco_percent'], alpha=0.3, color='#2ecc71')
    axes[2].set_ylabel('Disco (%)')
    axes[2].set_title('Uso de Disco ao Longo do Tempo')
    axes[2].set_xlabel('Tempo')

    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '01_serie_temporal_recursos.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Salvo: {caminho}")

    # 2. Histogramas
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Distribuicao dos Recursos', fontsize=14, fontweight='bold')
    for ax, col, cor, nome in zip(axes,
        ['cpu_percent','memoria_percent','disco_percent'],
        ['#e74c3c','#3498db','#2ecc71'],
        ['CPU (%)','Memoria (%)','Disco (%)']):
        ax.hist(df[col], bins=30, color=cor, alpha=0.7, edgecolor='black')
        ax.set_xlabel(nome); ax.set_ylabel('Frequencia'); ax.set_title(f'Distribuicao {nome}')
        ax.axvline(df[col].mean(), color='black', linestyle='--', label=f'Media: {df[col].mean():.1f}%')
        ax.legend()
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '02_histogramas_recursos.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Salvo: {caminho}")

    # 3. Correlação
    fig, ax = plt.subplots(figsize=(8, 6))
    cols_num = ['cpu_percent','memoria_percent','disco_percent','processos_ativos']
    cols_existem = [c for c in cols_num if c in df.columns]
    corr = df[cols_existem].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f')
    ax.set_title('Matriz de Correlacao dos Recursos', fontsize=14, fontweight='bold')
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '03_correlacao_recursos.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Salvo: {caminho}")

# ====================================================================
#  MODELO 1: ISOLATION FOREST - Deteccao de Anomalias
# ====================================================================
def treinar_isolation_forest(df):
    """Treina o modelo Isolation Forest para detectar anomalias."""
    print("\n" + "=" * 60)
    print("  MODELO 1: ISOLATION FOREST")
    print("  Objetivo: Detectar comportamentos anomalos nos recursos")
    print("=" * 60)

    features = ['cpu_percent', 'memoria_percent', 'disco_percent']
    if 'processos_ativos' in df.columns:
        features.append('processos_ativos')
    X = df[features].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    modelo_if = IsolationForest(
        n_estimators=100,
        contamination=0.1,  # 10% anomalias esperadas
        random_state=42,
        max_samples='auto'
    )
    df_result = df.copy()
    df_result['anomalia'] = modelo_if.fit_predict(X_scaled)
    df_result['anomalia_label'] = df_result['anomalia'].map({1: 'Normal', -1: 'Anomalia'})
    df_result['anomalia_score'] = modelo_if.decision_function(X_scaled)

    n_anomalias = (df_result['anomalia'] == -1).sum()
    n_normais = (df_result['anomalia'] == 1).sum()
    print(f"\n  Resultados:")
    print(f"    Normais:   {n_normais} ({n_normais/len(df)*100:.1f}%)")
    print(f"    Anomalias: {n_anomalias} ({n_anomalias/len(df)*100:.1f}%)")

    # Gráfico: Anomalias na série temporal
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle('Isolation Forest - Deteccao de Anomalias (VM Azure)', fontsize=16, fontweight='bold')

    normais = df_result[df_result['anomalia'] == 1]
    anomalias = df_result[df_result['anomalia'] == -1]

    axes[0].scatter(normais['timestamp'], normais['cpu_percent'], c='#2ecc71', s=10, label='Normal', alpha=0.6)
    axes[0].scatter(anomalias['timestamp'], anomalias['cpu_percent'], c='#e74c3c', s=30, label='Anomalia', marker='x', zorder=5)
    axes[0].set_ylabel('CPU (%)'); axes[0].set_title('CPU - Pontos Normais vs Anomalias')
    axes[0].legend()

    axes[1].scatter(normais['timestamp'], normais['memoria_percent'], c='#3498db', s=10, label='Normal', alpha=0.6)
    axes[1].scatter(anomalias['timestamp'], anomalias['memoria_percent'], c='#e74c3c', s=30, label='Anomalia', marker='x', zorder=5)
    axes[1].set_ylabel('Memoria (%)'); axes[1].set_title('Memoria - Pontos Normais vs Anomalias')
    axes[1].set_xlabel('Tempo'); axes[1].legend()

    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '04_isolation_forest_anomalias.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Grafico salvo: {caminho}")

    # Gráfico: Score de anomalia
    fig, ax = plt.subplots(figsize=(14, 5))
    cores = ['#e74c3c' if a == -1 else '#2ecc71' for a in df_result['anomalia']]
    ax.bar(range(len(df_result)), df_result['anomalia_score'], color=cores, width=1.0)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Amostra'); ax.set_ylabel('Score de Anomalia')
    ax.set_title('Isolation Forest - Score de Anomalia por Amostra', fontsize=14, fontweight='bold')
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '05_isolation_forest_scores.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Grafico salvo: {caminho}")

    # Scatter plot 2D
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(df_result['cpu_percent'], df_result['memoria_percent'],
                         c=df_result['anomalia_score'], cmap='RdYlGn', s=20, alpha=0.7)
    plt.colorbar(scatter, label='Score Anomalia')
    ax.scatter(anomalias['cpu_percent'], anomalias['memoria_percent'],
               c='red', s=60, marker='x', linewidths=2, label='Anomalias', zorder=5)
    ax.set_xlabel('CPU (%)'); ax.set_ylabel('Memoria (%)')
    ax.set_title('Isolation Forest - CPU vs Memoria', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '06_isolation_forest_scatter.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Grafico salvo: {caminho}")

    # Salvar resultados
    resultado = {
        'modelo': 'Isolation Forest',
        'ambiente': 'VM Azure',
        'total_amostras': len(df),
        'normais': int(n_normais),
        'anomalias': int(n_anomalias),
        'taxa_anomalia_percent': round(n_anomalias/len(df)*100, 2),
        'parametros': {'n_estimators': 100, 'contamination': 0.1},
        'estatisticas_anomalias': {
            'cpu_media': round(anomalias['cpu_percent'].mean(), 2) if len(anomalias) > 0 else 0,
            'mem_media': round(anomalias['memoria_percent'].mean(), 2) if len(anomalias) > 0 else 0
        }
    }
    with open(os.path.join(RESULTADOS_DIR, 'resultado_isolation_forest.json'), 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return df_result, modelo_if

# ====================================================================
#  MODELO 2: RANDOM FOREST - Previsao de Esgotamento
# ====================================================================
def treinar_random_forest(df):
    """Treina Random Forest para prever quando recursos vão esgotar."""
    print("\n" + "=" * 60)
    print("  MODELO 2: RANDOM FOREST CLASSIFIER")
    print("  Objetivo: Prever quando um recurso vai esgotar")
    print("=" * 60)

    df_rf = df.copy()
    # Criar label: 1 = recurso vai ficar critico em breve, 0 = normal
    # "Critico" = CPU > 80% OU Memoria > 85%
    df_rf['critico_futuro'] = 0
    for i in range(len(df_rf) - 3):
        futuro = df_rf.iloc[i+1:i+4]
        if (futuro['cpu_percent'].max() > 80) or (futuro['memoria_percent'].max() > 85):
            df_rf.loc[df_rf.index[i], 'critico_futuro'] = 1

    features = ['cpu_percent', 'memoria_percent', 'disco_percent']
    if 'processos_ativos' in df_rf.columns:
        features.append('processos_ativos')
    X = df_rf[features]
    y = df_rf['critico_futuro']

    print(f"\n  Distribuicao de classes:")
    print(f"    Normal (0):  {(y==0).sum()} ({(y==0).sum()/len(y)*100:.1f}%)")
    print(f"    Critico (1): {(y==1).sum()} ({(y==1).sum()/len(y)*100:.1f}%)")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y if y.nunique() > 1 else None)

    modelo_rf = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, class_weight='balanced'
    )
    modelo_rf.fit(X_train, y_train)
    y_pred = modelo_rf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n  Metricas de Desempenho:")
    print(f"    Acuracia:  {acc:.4f} ({acc*100:.1f}%)")
    print(f"    Precisao:  {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal','Critico'], zero_division=0))

    # Gráfico: Importância das features
    fig, ax = plt.subplots(figsize=(10, 6))
    importancias = modelo_rf.feature_importances_
    indices = np.argsort(importancias)[::-1]
    cores = ['#e74c3c','#3498db','#2ecc71','#f39c12'][:len(features)]
    ax.bar(range(len(features)), importancias[indices], color=[cores[i] for i in indices])
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels([features[i] for i in indices], rotation=45)
    ax.set_ylabel('Importancia'); ax.set_title('Random Forest - Importancia das Features', fontsize=14, fontweight='bold')
    for i, v in enumerate(importancias[indices]):
        ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '07_random_forest_importancia.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Grafico salvo: {caminho}")

    # Gráfico: Matriz de confusão
    fig, ax = plt.subplots(figsize=(7, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal','Critico'],
                yticklabels=['Normal','Critico'], ax=ax)
    ax.set_xlabel('Previsto'); ax.set_ylabel('Real')
    ax.set_title('Random Forest - Matriz de Confusao', fontsize=14, fontweight='bold')
    plt.tight_layout()
    caminho = os.path.join(GRAFICOS_DIR, '08_random_forest_confusao.png')
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    Grafico salvo: {caminho}")

    # Salvar resultados
    resultado = {
        'modelo': 'Random Forest Classifier',
        'ambiente': 'VM Azure',
        'metricas': {'acuracia': round(acc, 4), 'precisao': round(prec, 4),
                     'recall': round(rec, 4), 'f1_score': round(f1, 4)},
        'features': features,
        'importancia_features': {features[i]: round(float(importancias[i]), 4) for i in range(len(features))},
        'parametros': {'n_estimators': 100, 'max_depth': 10}
    }
    with open(os.path.join(RESULTADOS_DIR, 'resultado_random_forest.json'), 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return modelo_rf

# ====================================================================
#  MAIN
# ====================================================================
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Modelos de IA - VM Azure')
    parser.add_argument('--dados', type=str, default='dados_monitoramento_vm.csv',
                        help='Arquivo CSV com dados de monitoramento')
    args = parser.parse_args()

    criar_diretorios()
    df = carregar_dados(args.dados)
    gerar_graficos_exploratoria(df)
    df_anomalias, modelo_if = treinar_isolation_forest(df)
    modelo_rf = treinar_random_forest(df)

    print("\n" + "=" * 60)
    print("  TODOS OS MODELOS DA VM TREINADOS COM SUCESSO!")
    print(f"  Graficos salvos em: {GRAFICOS_DIR}/")
    print(f"  Resultados salvos em: {RESULTADOS_DIR}/")
    print("=" * 60)
