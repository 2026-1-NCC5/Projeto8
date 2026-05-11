"""
modelo_ia_docker.py - Modelo de IA para monitoramento no Docker
================================================================
Modelo 3: Logistic Regression - Classificar estado critico ou nao
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, precision_score, recall_score,
                             f1_score, roc_curve, auc)
from sklearn.preprocessing import StandardScaler
import warnings, os, json

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')

GRAFICOS_DIR = 'graficos_docker'
RESULTADOS_DIR = 'resultados_docker'

def criar_diretorios():
    os.makedirs(GRAFICOS_DIR, exist_ok=True)
    os.makedirs(RESULTADOS_DIR, exist_ok=True)

def carregar_dados(caminho_csv):
    print("=" * 60)
    print("  CARREGANDO DADOS DE MONITORAMENTO (DOCKER)")
    print("=" * 60)
    df = pd.read_csv(caminho_csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"  Registros: {len(df)}")
    print(f"  Periodo: {df['timestamp'].min()} a {df['timestamp'].max()}")
    print(df[['cpu_percent','memoria_percent','disco_percent']].describe().to_string())
    return df

def gerar_graficos_exploratoria(df):
    print("\n  Gerando graficos exploratorios (Docker)...")

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle('Monitoramento de Recursos - Docker Container', fontsize=16, fontweight='bold')
    for ax, col, cor, nome in zip(axes,
        ['cpu_percent','memoria_percent','disco_percent'],
        ['#e74c3c','#3498db','#2ecc71'],
        ['CPU (%)','Memoria (%)','Disco (%)']):
        ax.plot(df['timestamp'], df[col], color=cor, linewidth=1.2)
        ax.fill_between(df['timestamp'], df[col], alpha=0.3, color=cor)
        ax.set_ylabel(nome); ax.set_title(f'{nome} ao Longo do Tempo')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '01_serie_temporal_docker.png'), dpi=150, bbox_inches='tight')
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot([df['cpu_percent'], df['memoria_percent'], df['disco_percent']],
               labels=['CPU','Memoria','Disco'], patch_artist=True,
               boxprops=dict(facecolor='#3498db', alpha=0.6))
    ax.set_ylabel('Porcentagem (%)')
    ax.set_title('Boxplot - Recursos Docker', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '02_boxplot_docker.png'), dpi=150, bbox_inches='tight')
    plt.close()

def treinar_logistic_regression(df):
    """Treina Logistic Regression para classificar estado critico."""
    print("\n" + "=" * 60)
    print("  MODELO 3: LOGISTIC REGRESSION")
    print("  Objetivo: Classificar se o estado atual e critico ou nao")
    print("=" * 60)

    df_lr = df.copy()
    # Estado critico: CPU > 75% OU Memoria > 80%
    df_lr['estado_critico'] = ((df_lr['cpu_percent'] > 75) | (df_lr['memoria_percent'] > 80)).astype(int)

    features = ['cpu_percent', 'memoria_percent', 'disco_percent']
    if 'processos_ativos' in df_lr.columns:
        features.append('processos_ativos')
    X = df_lr[features]
    y = df_lr['estado_critico']

    print(f"\n  Distribuicao de classes:")
    print(f"    Normal (0):  {(y==0).sum()} ({(y==0).sum()/len(y)*100:.1f}%)")
    print(f"    Critico (1): {(y==1).sum()} ({(y==1).sum()/len(y)*100:.1f}%)")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42,
        stratify=y if y.nunique() > 1 else None
    )

    modelo_lr = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
    modelo_lr.fit(X_train, y_train)
    y_pred = modelo_lr.predict(X_test)
    y_proba = modelo_lr.predict_proba(X_test)[:, 1] if y.nunique() > 1 else np.zeros(len(y_test))

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n  Metricas:")
    print(f"    Acuracia:  {acc:.4f} ({acc*100:.1f}%)")
    print(f"    Precisao:  {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal','Critico'], zero_division=0))

    # Coeficientes
    print(f"  Coeficientes do modelo:")
    for feat, coef in zip(features, modelo_lr.coef_[0]):
        print(f"    {feat}: {coef:.4f}")
    print(f"    Intercepto: {modelo_lr.intercept_[0]:.4f}")

    # Gráfico: Coeficientes
    fig, ax = plt.subplots(figsize=(10, 6))
    coefs = modelo_lr.coef_[0]
    cores = ['#e74c3c' if c > 0 else '#3498db' for c in coefs]
    ax.barh(features, coefs, color=cores)
    ax.set_xlabel('Coeficiente'); ax.set_title('Logistic Regression - Coeficientes', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    for i, v in enumerate(coefs):
        ax.text(v + 0.01 if v > 0 else v - 0.15, i, f'{v:.3f}', va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '03_logistic_coeficientes.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # Gráfico: Matriz de confusão
    fig, ax = plt.subplots(figsize=(7, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
                xticklabels=['Normal','Critico'], yticklabels=['Normal','Critico'], ax=ax)
    ax.set_xlabel('Previsto'); ax.set_ylabel('Real')
    ax.set_title('Logistic Regression - Matriz de Confusao', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '04_logistic_confusao.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # Gráfico: Curva ROC
    if y.nunique() > 1 and y_test.nunique() > 1:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color='#e74c3c', lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
        ax.plot([0,1], [0,1], 'k--', lw=1)
        ax.set_xlabel('False Positive Rate'); ax.set_ylabel('True Positive Rate')
        ax.set_title('Logistic Regression - Curva ROC', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        plt.tight_layout()
        plt.savefig(os.path.join(GRAFICOS_DIR, '05_logistic_roc.png'), dpi=150, bbox_inches='tight')
        plt.close()

    # Gráfico: Classificação no espaço CPU x Memória
    fig, ax = plt.subplots(figsize=(10, 7))
    X_original = df_lr[features].values
    scatter = ax.scatter(X_original[:, 0], X_original[:, 1],
                         c=df_lr['estado_critico'], cmap='RdYlGn_r', s=20, alpha=0.7)
    plt.colorbar(scatter, label='Estado (0=Normal, 1=Critico)')
    ax.set_xlabel('CPU (%)'); ax.set_ylabel('Memoria (%)')
    ax.set_title('Logistic Regression - Classificacao CPU vs Memoria', fontsize=14, fontweight='bold')
    ax.axvline(x=75, color='red', linestyle='--', alpha=0.5, label='Limiar CPU 75%')
    ax.axhline(y=80, color='blue', linestyle='--', alpha=0.5, label='Limiar Mem 80%')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS_DIR, '06_logistic_classificacao.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # Salvar resultados
    resultado = {
        'modelo': 'Logistic Regression',
        'ambiente': 'Docker Container',
        'metricas': {'acuracia': round(acc,4), 'precisao': round(prec,4),
                     'recall': round(rec,4), 'f1_score': round(f1,4)},
        'coeficientes': {feat: round(float(c),4) for feat, c in zip(features, modelo_lr.coef_[0])},
        'intercepto': round(float(modelo_lr.intercept_[0]), 4),
        'limiar_critico': {'cpu_percent': 75, 'memoria_percent': 80}
    }
    with open(os.path.join(RESULTADOS_DIR, 'resultado_logistic_regression.json'), 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return modelo_lr

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Modelo de IA - Docker')
    parser.add_argument('--dados', type=str, default='dados_monitoramento_docker.csv')
    args = parser.parse_args()

    criar_diretorios()
    df = carregar_dados(args.dados)
    gerar_graficos_exploratoria(df)
    modelo_lr = treinar_logistic_regression(df)

    print("\n" + "=" * 60)
    print("  MODELO DOCKER TREINADO COM SUCESSO!")
    print(f"  Graficos: {GRAFICOS_DIR}/")
    print(f"  Resultados: {RESULTADOS_DIR}/")
    print("=" * 60)
