import cv2
import pytesseract

# Ajuste o caminho para o executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Função de callback para os sliders (não faz nada, apenas um placeholder)
def nothing(x):
    pass

# Inicialize a webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam.")
    exit()

# Crie uma janela para os sliders
cv2.namedWindow('Controles')

# Crie sliders para ajustar brilho, contraste e PSM
cv2.createTrackbar('Brilho', 'Controles', 0, 100, nothing)  # Valor padrão 50
cv2.createTrackbar('Contraste', 'Controles', 100, 100, nothing)  # Valor padrão 50
cv2.createTrackbar('PSM', 'Controles', 4, 13, nothing)  # PSM de 0 a 13
cv2.createTrackbar('Threshold', 'Controles', 101, 255, nothing)  # Ajuste inicial para threshold
cv2.createTrackbar('Blur', 'Controles', 0, 10, nothing)  # Ajuste inicial para blur
cv2.createTrackbar('Dilatação', 'Controles', 0, 10, nothing)  # Ajuste inicial para dilatação
cv2.createTrackbar('Erosão', 'Controles', 0, 10, nothing)  # Ajuste inicial para erosão

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Erro: Não foi possível ler o frame.")
        break

    # Obtenha os valores dos sliders
    threshold_value = cv2.getTrackbarPos('Threshold', 'Controles')
    blur_value = cv2.getTrackbarPos('Blur', 'Controles')
    dilation_value = cv2.getTrackbarPos('Dilatação', 'Controles')
    erosion_value = cv2.getTrackbarPos('Erosão', 'Controles')

    # Converta para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplique o threshold adaptativo
    block_size = 15  # Tamanho da vizinhança (deve ser ímpar)
    C_value = 10     # Valor subtraído da média
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, block_size, C_value)

    # Aplique o blur
    if blur_value > 1:
        thresh = cv2.GaussianBlur(thresh, (blur_value * 2 + 1, blur_value * 2 + 1), 0)

    # Aplique dilatação e erosão
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=dilation_value)
    eroded = cv2.erode(dilated, kernel, iterations=erosion_value)

    # Exiba a imagem processada
    cv2.imshow('Processado', eroded)

    # Saia do loop quando a tecla 'q' for pressionada
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('b'):  # Pressione 'b' para capturar a imagem
        # Realize OCR
        custom_config = f'--oem 3 --psm {cv2.getTrackbarPos("PSM", "Controles")}'
        data = pytesseract.image_to_data(eroded, config=custom_config, lang='por', output_type=pytesseract.Output.DICT)

        # Exiba o texto reconhecido e desenhe caixas ao redor do texto
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:
                # Obtenha as coordenadas da caixa delimitadora
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                # Desenhe a caixa delimitadora na imagem original
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # Coloque o texto reconhecido acima da caixa
                cv2.putText(frame, data['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,  0), 1)

        # Exiba a imagem com as caixas delimitadoras e o texto reconhecido
        cv2.imshow('Imagem Capturada', frame)
        print("Texto Reconhecido:", " ".join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 60]))

# Libere a captura e feche as janelas
cap.release()
cv2.destroyAllWindows()