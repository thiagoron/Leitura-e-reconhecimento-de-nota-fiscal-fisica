import cv2
import pytesseract

# Ajuste o caminho do executável Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Inicializar a webcam
cap = cv2.VideoCapture(0)

fps = 90
cap.set(cv2.CAP_PROP_FPS, fps)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    exit()

while True:
    # Captura frame a frame
    ret, frame = cap.read()
    
    if not ret:
        print("Erro: Não foi possível ler o frame.")
        break

    # Converter frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Realizar OCR no frame
    try:
        text = pytesseract.image_to_string(gray, "por")
    except pytesseract.TesseractError as e:
        print("Erro no Tesseract:", e)
        break

    # Exibir o frame resultante
    cv2.imshow('Webcam', frame)

    # Imprimir o texto reconhecido
    print("Texto Reconhecido:", text)

    # Encerra o loop ao pressionar a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a captura e fecha as janelas
cap.release()
cv2.destroyAllWindows()
