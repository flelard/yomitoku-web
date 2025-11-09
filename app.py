import os
import uuid
import subprocess
import requests
import time
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-multilingue-yomitoku-ollama-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['OLLAMA_TIMEOUT'] = 300  # 5 minutes max pour traduction
app.config['OLLAMA_MODEL'] = 'qwen3:8b'  # Modèle par défaut

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

print(f"🚀 DÉMARRAGE SERVEUR YOMITOKU + OLLAMA")
print(f"📦 Modèle Ollama configuré: {app.config['OLLAMA_MODEL']}")
print(f"⏱️  Timeout: {app.config['OLLAMA_TIMEOUT']}s")

# Traductions complètes
TRANSLATIONS = {
    'fr': {
        'title': 'Yomitoku + Ollama',
        'subtitle': 'Analyse & Traduction de documents',
        'select_file': 'Sélectionnez un document',
        'formats': {
            'md': 'Markdown',
            'html': 'HTML',
            'json': 'JSON',
            'csv': 'CSV'
        },
        'device': 'Périphérique',
        'options': 'Options avancées',
        'trans_options': 'Options de traduction',
        'vis': 'Générer la visualisation',
        'lite': 'Mode léger (rapide)',
        'figure': 'Exporter les figures',
        'figure_letter': 'Texte dans les figures',
        'ignore_line_break': 'Ignorer sauts de ligne',
        'combine': 'Fusionner les pages',
        'ignore_meta': 'Ignorer en-têtes/pieds',
        'translate': 'Traduire avec Ollama',
        'target_lang': 'Langue cible',
        'target_langs': {
            'fr': 'Français',
            'en': 'Anglais',
            'es': 'Espagnol',
            'de': 'Allemand'
        },
        'ollama_model': 'Modèle Ollama',
        'launch': 'Lancer l\'analyse',
        'drag_drop': 'Glissez-déposez votre fichier ici ou cliquez pour sélectionner',
        'success': 'Analyse terminée !',
        'translating': 'Traduction en cours...',
        'error': 'Erreur',
        'error_ollama': 'Erreur Ollama (non démarré?)',
        'download': 'Télécharger',
        'view_results': 'Voir les résultats',
        'job_id': 'Job ID',
        'files_generated': 'Fichiers générés',
        'visualizations': 'Visualisations',
        'translated_files': 'Fichiers traduits',
        'no_files': 'Aucun fichier trouvé',
        'back': 'Retour',
        'recent_jobs': 'Analyses récentes'
    },
    'en': {
        'title': 'Yomitoku + Ollama',
        'subtitle': 'Document Analysis & Translation',
        'select_file': 'Select a document',
        'formats': {
            'md': 'Markdown',
            'html': 'HTML',
            'json': 'JSON',
            'csv': 'CSV'
        },
        'device': 'Device',
        'options': 'Advanced Options',
        'trans_options': 'Translation Options',
        'vis': 'Generate visualization',
        'lite': 'Lite mode (fast)',
        'figure': 'Export figures',
        'figure_letter': 'Text in figures',
        'ignore_line_break': 'Ignore line breaks',
        'combine': 'Merge pages',
        'ignore_meta': 'Ignore headers/footers',
        'translate': 'Translate with Ollama',
        'target_lang': 'Target language',
        'target_langs': {
            'fr': 'French',
            'en': 'English',
            'es': 'Spanish',
            'de': 'German'
        },
        'ollama_model': 'Ollama Model',
        'launch': 'Launch Analysis',
        'drag_drop': 'Drag & drop your file here or click to select',
        'success': 'Analysis completed!',
        'translating': 'Translation in progress...',
        'error': 'Error',
        'error_ollama': 'Ollama error (not started?)',
        'download': 'Download',
        'view_results': 'View Results',
        'job_id': 'Job ID',
        'files_generated': 'Generated Files',
        'visualizations': 'Visualizations',
        'translated_files': 'Translated Files',
        'no_files': 'No files found',
        'back': 'Back',
        'recent_jobs': 'Recent Analyses'
    },
    'ja': {
        'title': 'Yomitoku + Ollama',
        'subtitle': '文書分析 & 翻訳',
        'select_file': '文書を選択',
        'formats': {
            'md': 'Markdown',
            'html': 'HTML',
            'json': 'JSON',
            'csv': 'CSV'
        },
        'device': 'デバイス',
        'options': '高度なオプション',
        'trans_options': '翻訳オプション',
        'vis': '可視化を生成',
        'lite': 'ライトモード（高速）',
        'figure': '図をエクスポート',
        'figure_letter': '図内の文字',
        'ignore_line_break': '改行を無視',
        'combine': 'ページを結合',
        'ignore_meta': 'ヘッダー/フッターを無視',
        'translate': 'Ollamaで翻訳',
        'target_lang': 'ターゲット言語',
        'target_langs': {
            'fr': 'フランス語',
            'en': '英語',
            'es': 'スペイン語',
            'de': 'ドイツ語'
        },
        'ollama_model': 'Ollamaモデル',
        'launch': '分析を開始',
        'drag_drop': 'ここにファイルをドラッグ＆ドロップ、またはクリックして選択',
        'success': '分析が完了しました！',
        'translating': '翻訳中...',
        'error': 'エラー',
        'error_ollama': 'Ollamaエラー（起動していません？）',
        'download': 'ダウンロード',
        'view_results': '結果を表示',
        'job_id': 'ジョブID',
        'files_generated': '生成されたファイル',
        'visualizations': '可視化',
        'translated_files': '翻訳済みファイル',
        'no_files': 'ファイルが見つかりません',
        'back': '戻る',
        'recent_jobs': '最近の分析'
    }
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_job_path(job_id):
    return Path(app.config['OUTPUT_FOLDER']) / job_id

def get_lang():
    return session.get('lang', 'fr')

def translate_with_ollama(text, target_lang='fr', model=None):
    """Traduit le texte avec Ollama local"""
    print(f"\n{'='*60}")
    print(f"🔄 [TRADUCTION] Début pour langue: {target_lang}")
    print(f"📝 [TRADUCTION] Modèle: {model or app.config['OLLAMA_MODEL']}")
    print(f"📝 [TRADUCTION] Texte source (200 premiers car): {text[:200]}...")
    print(f"📊 [TRADUCTION] Taille totale: {len(text)} caractères")
    
    # Vérifier si le texte est vide
    if len(text.strip()) < 50:
        print("⚠️  [TRADUCTION] Texte trop court pour traduction (< 50 car)")
        return text
    
    # Compter les caractères japonais
    jap_chars = sum(1 for c in text if '\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF')
    print(f"🔍 [TRADUCTION] Caractères japonais détectés: {jap_chars}")
    
    if jap_chars < 50:
        print("⚠️  [TRADUCTION] Peu de caractères japonais, traduction annulée")
        return text + "\n\n[⚠️ Texte non-japonais détecté, traduction ignorée]"
    
    try:
        # Choisir le modèle
        model_to_use = model or app.config['OLLAMA_MODEL']
        
        # TEST CONNEXION
        print(f"🔌 [TRADUCTION] Test connexion Ollama sur localhost:11434...")
        ollama_check = requests.get('http://localhost:11434/api/tags', timeout=5)
        print(f"✅ [TRADUCTION] Ollama OK: {ollama_check.status_code}")
        
        # Vérifier modèle disponible
        models = ollama_check.json().get('models', [])
        model_names = [m['name'] for m in models]
        print(f"📦 [TRADUCTION] Modèles disponibles: {model_names}")
        
        if model_to_use not in model_names:
            print(f"❌ [TRADUCTION] Modèle {model_to_use} non trouvé !")
            return f"❌ ERROR: Model '{model_to_use}' not found. Available: {', '.join(model_names)}"
        
        # Prompt optimisé
        prompt = f"""You are a professional translator. Translate this Japanese text to {target_lang}.
        Return ONLY the translation, nothing else:
        
        {text[:4000]}"""  # Limiter à 4000 caractères pour performance
        
        print(f"⏱️  [TRADUCTION] Envoi à Ollama (modèle: {model_to_use})...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": model_to_use,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 3000
                }
            },
            timeout=app.config['OLLAMA_TIMEOUT']
        )
        
        elapsed = time.time() - start_time
        print(f"✅ [TRADUCTION] Réponse reçue en {elapsed:.2f}s")
        print(f"📊 [TRADUCTION] Statut: {response.status_code}")
        
        if response.status_code == 200:
            translated = response.json()['response'].strip()
            print(f"🎯 [TRADUCTION] Texte traduit (200 premiers car): {translated[:200]}")
            return translated
        else:
            print(f"❌ [TRADUCTION] Erreur Ollama: {response.status_code} - {response.text}")
            return f"❌ Translation failed: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        print("❌ [TRADUCTION] ERREUR: Ollama non accessible sur localhost:11434")
        return "❌ ERROR: Ollama not running. Start with 'sudo systemctl start ollama'"
    except Exception as e:
        print(f"❌ [TRADUCTION] Exception: {type(e).__name__}: {str(e)}")
        return f"❌ Translation error: {str(e)}"

@app.route('/')
def index():
    lang = get_lang()
    print(f"🌐 Page chargée en: {lang}")
    return render_template('index.html', lang=lang, translations=TRANSLATIONS[lang])

@app.route('/set_lang/<lang>')
def set_language(lang):
    if lang in ['fr', 'en', 'ja']:
        session['lang'] = lang
        print(f"🌐 Changement langue: {lang}")
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File format not allowed'}), 400
    
    job_id = str(uuid.uuid4())[:8]
    job_path = get_job_path(job_id)
    job_path.mkdir(exist_ok=True)
    
    filename = secure_filename(file.filename)
    input_path = job_path / filename
    file.save(input_path)
    
    print(f"\n{'='*70}")
    print(f"📄 NOUVELLE ANALYSE - Job ID: {job_id}")
    print(f"📝 Fichier: {filename}")
    
    # Options
    output_format = request.form.get('format', 'md')
    visualization = 'vis' in request.form
    lite_mode = 'lite' in request.form
    figure_export = 'figure' in request.form
    figure_letter_export = 'figure_letter' in request.form
    ignore_line_break = 'ignore_line_break' in request.form
    combine_pages = 'combine' in request.form
    ignore_meta = 'ignore_meta' in request.form
    device = request.form.get('device', 'cpu')
    translate_enabled = 'translate' in request.form
    target_lang = request.form.get('target_lang', 'fr')
    ollama_model = request.form.get('ollama_model', app.config['OLLAMA_MODEL'])
    
    print(f"⚙️  Options: format={output_format}, device={device}, translate={translate_enabled}, model={ollama_model}")
    
    # Construire commande Yomitoku
    cmd = ['yomitoku', str(input_path), '-f', output_format, '-o', str(job_path / 'results'), '-d', device]
    
    if visualization:
        cmd.append('-v')
    if lite_mode:
        cmd.append('-l')
    if figure_export:
        cmd.append('--figure')
    if figure_letter_export:
        cmd.append('--figure_letter')
    if ignore_line_break:
        cmd.append('--ignore_line_break')
    if combine_pages:
        cmd.append('--combine')
    if ignore_meta:
        cmd.append('--ignore_meta')
    
    print(f"🔧 Commande Yomitoku: {' '.join(cmd)}")
    
    try:
        # Analyse Yomitoku
        print("⏳ Analyse Yomitoku en cours...")
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        elapsed = time.time() - start_time
        
        print(f"✅ Analyse terminée en {elapsed:.2f} secondes")
        
        if result.returncode != 0:
            print(f"❌ Erreur Yomitoku: {result.stderr}")
            return jsonify({'error': f'Yomitoku error: {result.stderr}'}), 500
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout Yomitoku (1 heure)")
        return jsonify({'error': 'Analysis timeout (1 hour)'}), 500
    except Exception as e:
        print(f"❌ Exception Yomitoku: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500
    
    results_dir = job_path / 'results'
    print(f"📁 Dossier résultats: {results_dir}")
    
    # Lister TOUS les fichiers créés
    print("📁 Fichiers créés par Yomitoku:")
    all_files = list(results_dir.iterdir()) if results_dir.exists() else []
    for f in all_files:
        print(f"   - {f.name} ({f.stat().st_size} octets)")
    
    # Traduction si demandée
    if translate_enabled:
        print(f"\n🌍 TRADUCTION demandée vers {target_lang} avec {ollama_model}")
        
        # Chercher TOUS les fichiers texte
        files_to_translate = []
        for ext in ['*.md', '*.html', '*.txt', '*.json', '*.csv']:
            files_to_translate.extend(results_dir.glob(ext))
        
        print(f"📄 Fichiers trouvés pour traduction: {len(files_to_translate)}")
        
        if not files_to_translate:
            print("❌ Aucun fichier texte trouvé !")
            print("💡 Conseil: Essayez de générer un format différent (ex: md)")
        else:
            print("📄 Fichiers à traduire:")
            for f in files_to_translate:
                print(f"   - {f.name}")
        
        for i, file_path in enumerate(files_to_translate[:2]):  # Max 2
            print(f"\n📝 Traduction fichier {i+1}/{len(files_to_translate)}: {file_path.name}")
            
            try:
                text = file_path.read_text(encoding='utf-8', errors='ignore')
                print(f"📊 Taille texte: {len(text)} caractères")
                
                if len(text) > 10000:
                    print("⚠️  Texte très long, limitation à 10000 caractères")
                    text = text[:10000]
                
                translated = translate_with_ollama(text, target_lang, ollama_model)
                
                if translated and not translated.startswith('❌'):
                    translated_file = results_dir / f"translated_{target_lang}_{file_path.name}"
                    translated_file.write_text(translated, encoding='utf-8')
                    print(f"✅ Sauvegardé: {translated_file.name}")
                else:
                    print(f"❌ Échec: {translated}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    else:
        print("\n🌍 Traduction non demandée")
    
    # Préparer liste des fichiers
    files_info = []
    if results_dir.exists():
        for file in results_dir.iterdir():
            if file.is_file():
                files_info.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'url': f'/download/{job_id}/{file.name}'
                })
    
    print(f"✅ Job {job_id} terminé avec {len(files_info)} fichiers")
    print(f"{'='*70}\n")
    
    return jsonify({'job_id': job_id, 'files': files_info, 'success': True})

@app.route('/download/<job_id>/<filename>')
def download_file(job_id, filename):
    job_path = get_job_path(job_id)
    file_path = job_path / 'results' / filename
    
    if not file_path.exists():
        return "File not found", 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/results/<job_id>')
def view_results(job_id):
    lang = get_lang()
    job_path = get_job_path(job_id)
    results_dir = job_path / 'results'
    
    if not results_dir.exists():
        return "Results not found", 404
    
    files = []
    visualizations = []
    translated_files = []
    
    for file in results_dir.iterdir():
        if file.is_file():
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png'] and 'vis' in file.name:
                visualizations.append(file.name)
            elif file.name.startswith('translated_'):
                translated_files.append(file.name)
            else:
                files.append({
                    'name': file.name,
                    'size': f"{file.stat().st_size / 1024:.1f} KB"
                })
    
    return render_template('results.html', job_id=job_id, files=files, visualizations=visualizations,
                         translated_files=translated_files, lang=lang, translations=TRANSLATIONS[lang])

@app.route('/api/jobs')
def list_jobs():
    jobs = []
    output_path = Path(app.config['OUTPUT_FOLDER'])
    
    for job_dir in output_path.iterdir():
        if job_dir.is_dir():
            created = job_dir.stat().st_ctime
            files_count = len(list((job_dir / 'results').glob('*'))) if (job_dir / 'results').exists() else 0
            
            jobs.append({
                'id': job_dir.name,
                'created': created,
                'files_count': files_count
            })
    
    jobs.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(jobs)

if __name__ == '__main__':
    print("🚀 DÉMARRAGE DU SERVEUR...")
    print(f"🌐 Accédez à: http://<IP_VOTRE_SERVEUR>:5000")
    print(f"📦 Modèle Ollama: {app.config['OLLAMA_MODEL']}")
    app.run(debug=False, host='0.0.0.0', port=5000)
