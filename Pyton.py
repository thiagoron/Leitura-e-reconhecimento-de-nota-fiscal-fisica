import cv2
import pytesseract

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
    cv2.createTrackbar('PSM', 'Controles', 4, 13, nothing)
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

def perform_ocr(eroded, frame):
    custom_config = f'--oem 3 --psm {cv2.getTrackbarPos("PSM", "Controles")}'
    data = pytesseract.image_to_data(eroded, config=custom_config, lang='por', output_type=pytesseract.Output.DICT)

    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, data['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    recognized_text = " ".join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 60])
    print("Texto Reconhecido:", recognized_text)
    return frame

def main():
    cap = initialize_camera()
    create_sliders()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            break

        threshold_value = cv2.getTrackbarPos('Threshold', 'Controles')
        blur_value = cv2.getTrackbarPos('Blur', 'Controles')
        dilation_value = cv2.getTrackbarPos('Dilatação', 'Controles')
        erosion_value = cv2.getTrackbarPos('Erosão', 'Controles')

        eroded = process_frame(frame, blur_value, dilation_value, erosion_value)
        cv2.imshow('Processado', eroded)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('b'):
            frame_with_text = perform_ocr(eroded, frame)
            cv2.imshow('Imagem Capturada', frame_with_text)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()