# Escolha a imagem oficial do Python 3.10
FROM python:3.10-slim

# Atualize o pip
RUN pip install --upgrade pip

# Copie os arquivos do seu projeto
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie o resto do código da aplicação
COPY . /app

# Defina o diretório de trabalho
WORKDIR /app

# Comando para rodar o seu app (ajuste conforme necessário)
CMD ["python", "app.py"]
