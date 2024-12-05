# Escolha a imagem oficial do Python 3.10
FROM python:3.10-slim

# Instala as dependências do sistema, incluindo o ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Atualize o pip
RUN pip install --upgrade pip

# Copie os arquivos do seu projeto
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação
COPY . /app

# Defina o diretório de trabalho
WORKDIR /app

# Comando para rodar o seu app (ajuste conforme necessário)
CMD ["python", "app.py"]
