import cv2
import threading
from collections import Counter
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TadbagVLz73yXH0tRlyT"
)

MODEL_ID = "first-deliver-model-version/1"
CLASSES_ALVO = ['rice', 'bean', 'pasta']

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Erro: câmera não encontrada!")
    exit()

latest_frame = None
latest_result = {"predictions": []}
lock = threading.Lock()

def inference_worker():
    global latest_result
    while True:
        with lock:
            frame = latest_frame

        if frame is None:
            continue

        result = client.infer(frame, model_id=MODEL_ID)

        with lock:
            latest_result = result

thread = threading.Thread(target=inference_worker, daemon=True)
thread.start()

print("Câmera iniciada. Pressione 'q' para sair.")

while True:
    sucesso, frame = camera.read()
    if not sucesso:
        break

    with lock:
        latest_frame = frame.copy()
        result = latest_result

    itens_frame = []
    frame_anotado = frame.copy()

    for pred in result.get("predictions", []):
        classe = pred["class"]
        conf = pred["confidence"]
        x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
        x1, y1 = x - w // 2, y - h // 2
        x2, y2 = x + w // 2, y + h // 2

        cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame_anotado, f"{classe} {conf:.2f}", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if classe in CLASSES_ALVO:
            itens_frame.append(classe)

    contagem = Counter(itens_frame)
    cv2.rectangle(frame_anotado, (10, 10), (380, 130), (0, 0, 0), -1)

    y_pos = 35
    for classe in CLASSES_ALVO:
        quantidade = contagem.get(classe, 0)
        texto = f"{classe}: {quantidade} unidade(s)"
        cor = (0, 255, 0) if quantidade > 0 else (150, 150, 150)
        cv2.putText(frame_anotado, texto, (20, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
        y_pos += 30

    cv2.imshow("Detector de Pacotes", frame_anotado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
