# 📊 ContaCerto - Análise e Resumo dos resultados

---

## 1. Configuração do experimento

O modelo utilizado foi o **YOLO11s** (small), treinado por **85 épocas**. O dataset foi dividido em **90% treino / 10% validação**, totalizando **694 instâncias anotadas** distribuídas entre as cinco classes:

| Classe   | Instâncias totais |
|----------|-------------------|
| arroz    | 86                |
| acucar   | 78                |
| fubá     | 79                |
| feijao   | 151               |
| macarrao | 151               |
| Leite em Pó | 57             |
| Óleo | 92                    |

## 2. Métricas Finais

| Métrica      | Entrega 02 | Interpretação
|--------------|------------|---------------|
| Precisão     | 0.988      | Taxa de acerto nas detecções realizadas.
| Recall       | 0.989      | Capacidade de encontrar os objetos presentes.
| mAP@0.5      | 0.985      | Média de precisão com IoU de 50%.
| mAP@0.5:0.95 | 0.902      | Média de precisão em diferentes limiares de rigor geométrico.

---
