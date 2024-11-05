import cv2
import pytesseract
import pandas as pd
import os

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def initialize_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Erro: Não foi possível abrir a webcam.")
    return cap

def process_frame(frame):
    # Processamento da imagem
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    block_size = 15
    C_value = 10
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C_value)
    return thresh

def perform_ocr(processed_image):
    custom_config = '--oem 3 --psm 6'  # Ajuste conforme necessário
    data = pytesseract.image_to_data(processed_image, config=custom_config, lang='por', output_type=pytesseract.Output.DICT)
    return data

def update_excel(data):
    # Cria um DataFrame a partir dos dados reconhecidos
    recognized_text = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Filtra resultados com confiança acima de 60
            recognized_text.append(data['text'][i])

    # Cria um DataFrame
    df = pd.DataFrame(recognized_text, columns=['Texto Reconhecido'])

    # Verifica se o arquivo Excel já existe
    file_path = 'texto_reconhecido.xlsx'
    if os.path.exists(file_path):
        # Se existir, carrega o arquivo existente e adiciona os novos dados
        existing_df = pd.read_excel(file_path)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(file_path, index=False)
    else:
        # Se não existir, cria um novo arquivo
        df.to_excel(file_path, index=False)

def main():
    cap = initialize_webcam()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            break
        
        processed_image = process_frame(frame)
        cv2.imshow('Processado', processed_image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('b'):  # Pressione 'b' para capturar a imagem
            data = perform_ocr(processed_image)
            update_excel(data)  # Atualiza a tabela do Excel
            print("Texto reconhecido e atualizado na tabela do Excel.")

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()