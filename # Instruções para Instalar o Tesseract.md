# Instruções para Instalar o Tesseract

1. Baixe o Tesseract OCR a partir do [repositório oficial do Tesseract](https://github.com/tesseract-ocr/tesseract).
2. Siga as instruções de instalação para o seu sistema operacional.
3. Após a instalação, certifique-se de que o caminho para o executável `tesseract.exe` esteja corretamente configurado no seu código.

   Por exemplo, se você instalou o Tesseract no diretório padrão no Windows, o caminho deve ser:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'