from flask import Flask, render_template, request, redirect, url_for, send_file
from spleeter.separator import Separator
import os
import shutil
import logging

app = Flask(__name__)

# Definir o diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurar as pastas de upload e saída no diretório do projeto
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'output')

# Garantir que as pastas de upload e saída existam
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    error = None
    download_link = None

    if request.method == 'POST':
        # Pegar o número de stems
        try:
            stems = int(request.form['stems'])
            if stems not in [2, 4, 5]:
                error = "Escolha um número de stems válido: 2, 4 ou 5."
                return render_template('dashboard.html', error=error)
        except ValueError:
            error = "Por favor, insira um número válido de stems (2, 4 ou 5)."
            return render_template('dashboard.html', error=error)

        # Obter o arquivo de áudio enviado
        audio_file = request.files['audio_file']
        if audio_file and audio_file.filename.endswith('.mp3'):
            # Salvar o arquivo de áudio
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
            audio_file.save(audio_path)

            # Usar o Spleeter para separar o áudio
            output_subdir = os.path.join(app.config['OUTPUT_FOLDER'], audio_file.filename.split('.')[0])
            os.makedirs(output_subdir, exist_ok=True)

            try:
                separator = Separator(f'spleeter:{stems}stems')
                separator.separate_to_file(audio_path, output_subdir)

                # Compactar os arquivos separados em um zip
                zip_filename = f"{audio_file.filename.split('.')[0]}.zip"
                zip_filepath = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
                shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', output_subdir)

                # Limpar o arquivo de áudio original
                os.remove(audio_path)

                download_link = url_for('download_zip', filename=zip_filename, _external=True)

            except Exception as e:
                error = f"Ocorreu um erro ao processar a música: {e}"
                return render_template('dashboard.html', error=error)

        else:
            error = "Por favor, envie um arquivo .mp3 válido."
            return render_template('dashboard.html', error=error)

    return render_template('dashboard.html', error=error, download_link=download_link)

@app.route('/download/<filename>')
def download_zip(filename):
    # Caminho do arquivo zip
    zip_filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)

    # Enviar o arquivo zip para download
    response = send_file(zip_filepath, as_attachment=True)

    # Excluir arquivos após o download
    try:
        stem_dir = os.path.join(app.config['OUTPUT_FOLDER'], filename.replace('.zip', ''))
        if os.path.exists(stem_dir):
            shutil.rmtree(stem_dir)  # Remover diretório dos stems
        if os.path.exists(zip_filepath):
            os.remove(zip_filepath)  # Remover o zip
    except Exception as e:
        print(f"Erro ao excluir arquivos: {e}")

    return response


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logging.info("Iniciando o servidor Flask...")
    app.run(host='0.0.0.0', port=port)
