import cv2
import threading
from collections import Counter
from ultralytics import YOLO

MODEL_PATH = "best.pt"
CLASSES_ALVO = ['feijao', 'arroz', 'oleo']

model = YOLO(MODEL_PATH)

camera = None
for index in range(3):
    for backend in (cv2.CAP_MSMF, cv2.CAP_DSHOW, 0):
        cap = cv2.VideoCapture(index, backend) if backend else cv2.VideoCapture(index)
        if cap.isOpened():
            camera = cap
            print(f"Câmera encontrada: index={index}")
            break
    if camera:
        break

if camera is None:
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

        results = model(frame, verbose=False)[0]
        predictions = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            predictions.append({
                "class": results.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            })

        with lock:
            latest_result = {"predictions": predictions}

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
        x1, y1, x2, y2 = pred["x1"], pred["y1"], pred["x2"], pred["y2"]

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
