import cv2
import pytesseract
import re

# Ajuste o caminho para o executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def nothing(x):
    pass

def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a webcam.")
        exit()
    return cap

def create_sliders():
    cv2.namedWindow('Controles')
    cv2.createTrackbar('Brilho', 'Controles', 0, 100, nothing)
    cv2.createTrackbar('Contraste', 'Controles', 100, 100, nothing)
    cv2.createTrackbar('Threshold', 'Controles', 101, 255, nothing)
    cv2.createTrackbar('Blur', 'Controles', 0, 10, nothing)
    cv2.createTrackbar('Dilatação', 'Controles', 0, 10, nothing)
    cv2.createTrackbar('Erosão', 'Controles', 0, 10, nothing)

def process_frame(frame, blur_value, dilation_value, erosion_value):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    block_size = 15
    C_value = 10
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C_value)

    if blur_value > 1:
        thresh = cv2.GaussianBlur(thresh, (blur_value * 2 + 1, blur_value * 2 + 1), 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=dilation_value)
    eroded = cv2.erode(dilated, kernel, iterations=erosion_value)
    
    return eroded

def extract_information(text):
    # Expressões regulares para encontrar COO (ou Controle), data e valor total
    coo_pattern = r'(COO|Controle)\s*:?(\s*\d{6})'
    date_pattern = r'(Data de Emissão\s*:?(\d{2}/\d{2}/\d{4})'
    value_pattern = r'(R\$\s*([\d.,]+)'

    coo = re.search(coo_pattern, text)
    date = re.search(date_pattern, text)
    values = re.findall(value_pattern, text)

    # Selecionar o maior valor encontrado
    max_value = max(values, key=lambda v: float(v.replace('.', '').replace(',', '.'))) if values else None

    extracted_info = {
        'COO': coo.group(2).strip() if coo else None,
        'Data de Emissão': date.group(1) if date else None,
        'Valor Total': max_value
    }

    return extracted_info

def perform_ocr(eroded):
    best_confidence = 0
    best_info = {}

    # Testar diferentes valores de PSM
    psm_values = range(3, 14)  # Valores de PSM de 3 a 13
    for psm in psm_values:
        custom_config = f'--oem 3 --psm {psm}'
        data = pytesseract.image_to_data(eroded, config=custom_config, lang='por', output_type=pytesseract.Output.DICT)

        # Concatenar texto reconhecido e calcular a confiança
        recognized_text = " ".join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 60])
        confidence = sum(int(data['conf'][i]) for i in range(len(data['conf'])) if int(data['conf'][i]) > 60)

        # Se a confiança for melhor, atualizar a melhor informação
        if confidence > best_confidence:
            best_confidence = confidence
            best_info = extract_information(recognized_text)

    return best_info

def main():
    cap = initialize_camera()
    create_sliders()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível capturar o quadro.")
            break

        # Obter valores dos sliders
        brightness = cv2.getTrackbarPos('Brilho', 'Controles')
        contrast = cv2.getTrackbarPos('Contraste', 'Controles')
        threshold = cv2.getTrackbarPos('Threshold', 'Controles')
        blur = cv2.getTrackbarPos('Blur', 'Controles')
        dilation = cv2.getTrackbarPos('Dilatação', 'Controles')
        erosion = cv2.getTrackbarPos('Erosão', 'Controles')

        # Processar o quadro
        processed_frame = process_frame(frame, blur, dilation, erosion)

        # Mostrar o quadro processado
        cv2.imshow('Frame Processado', processed_frame)

        # Verificar se a tecla 'b' foi pressionada
        if cv2.waitKey(1) & 0xFF == ord('b'):
            # Executar OCR e obter informações
            extracted_info = perform_ocr(processed_frame)
            # Exibir informações extraídas
            print(extracted_info)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()