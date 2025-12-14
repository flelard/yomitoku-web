import os
import uuid
import subprocess
import requests
import time
import pypdfium2 as pdfium
import json
import threading
from collections import deque
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for, Response
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import atexit
import gc

# Tentative d'import de torch pour surveillance précise (optionnel)
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-multilingue-yomitoku-ollama-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
app.config['OLLAMA_TIMEOUT'] = 900
app.config['OLLAMA_MODEL'] = 'qwen2.5:latest'

# Configuration critique pour la mémoire GPU
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

AVAILABLE_OLLAMA_MODELS = []

# Stockage des données de job
job_data = {}
data_lock = threading.Lock()

# SEMAPHORE pour limiter les jobs GPU à 1 à la fois
gpu_semaphore = threading.Semaphore(1)

# ===== INITIALISATION DE L'EXECUTEUR =====
executor = ThreadPoolExecutor(max_workers=2)

def shutdown_executor():
    print("🛑 Stopping executor...")
    executor.shutdown(wait=True)

atexit.register(shutdown_executor)

# =======================================================================
# GESTION AVANCÉE DE LA MÉMOIRE
# =======================================================================

def get_gpu_memory_info():
    """Retourne (free_mem_gb, total_mem_gb)"""
    if HAS_TORCH and torch.cuda.is_available():
        try:
            free, total = torch.cuda.mem_get_info()
            return free / 1024**3, total / 1024**3
        except:
            pass
            
    # Fallback nvidia-smi
    try:
        cmd = "nvidia-smi --query-gpu=memory.free,memory.total --format=csv,nounits,noheader"
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        free_mb, total_mb = map(float, result.split(','))
        return free_mb / 1024, total_mb / 1024
    except:
        return 0, 0

def force_unload_ollama(job_id=None):
    """Décharge TOUS les modèles chargés dans Ollama"""
    unloaded_count = 0
    try:
        running_models = []
        try:
            ps_response = requests.get('http://127.0.0.1:11434/api/ps', timeout=2)
            if ps_response.status_code == 200:
                data = ps_response.json()
                if 'models' in data:
                    running_models = [m['name'] for m in data['models']]
        except:
            pass 

        if app.config['OLLAMA_MODEL'] not in running_models:
            running_models.append(app.config['OLLAMA_MODEL'])

        for model in running_models:
            payload = {"model": model, "keep_alive": 0}
            try:
                requests.post('http://127.0.0.1:11434/api/chat', json=payload, timeout=1)
                unloaded_count += 1
            except:
                try:
                    requests.post('http://127.0.0.1:11434/api/generate', json=payload, timeout=1)
                    unloaded_count += 1
                except:
                    pass
                    
        if job_id and unloaded_count > 0:
            log_to_job(job_id, f"🧠 Ollama Cleanup: {len(running_models)} model(s) unloaded", 'info')
            
    except Exception as e:
        if job_id: log_to_job(job_id, f"⚠️ Unload error: {e}", 'warning')

def wait_for_vram(required_gb=3.0, timeout=30, job_id=None):
    """Boucle d'attente active qui bloque tant que la VRAM n'est pas libre"""
    start_time = time.time()
    
    # Nettoyage immédiat
    force_unload_ollama(job_id)
    gc.collect()
    if HAS_TORCH and torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    while (time.time() - start_time) < timeout:
        free_gb, total_gb = get_gpu_memory_info()
        
        if total_gb == 0: # Pas de GPU ou erreur détection
            return True
            
        if free_gb >= required_gb:
            if job_id:
                log_to_job(job_id, f"🔋 Available VRAM: {free_gb:.2f}GB", 'success')
            return True
            
        if int(time.time() - start_time) % 5 == 0 and job_id:
            log_to_job(job_id, f"⏳ Waiting for VRAM... Free: {free_gb:.2f}GB / {total_gb:.2f}GB", 'warning')
            force_unload_ollama(job_id)
            
        time.sleep(2)
        
    return False

def cleanup_gpu_memory(job_id=None, aggressive=False):
    force_unload_ollama(job_id)
    gc.collect()
    if HAS_TORCH and torch.cuda.is_available():
        torch.cuda.empty_cache()
    return True

# =======================================================================

def run_yomitoku_job_with_lock(job_id, input_filenames, base_cmd, translate_enabled, target_lang, ollama_model, custom_prompt, num_ctx, job_path, output_format, gpu_lock):
    """Wrapper pour exécuter le job avec verrou GPU et surveillance VRAM"""
    if gpu_lock:
        acquired = False
        try:
            acquired = gpu_lock.acquire(timeout=600)
            if acquired:
                log_to_job(job_id, "🔒 GPU Lock acquired (batch processing)", 'info')
                
                vram_ok = wait_for_vram(required_gb=3.0, timeout=45, job_id=job_id)
                
                if not vram_ok:
                    free_gb, _ = get_gpu_memory_info()
                    log_to_job(job_id, f"❌ CRITICAL ERROR: Insufficient VRAM ({free_gb:.2f}GB). Ollama is blocking.", 'error')
                    with data_lock:
                        job_data[job_id]['status'] = 'error'
                    return

                run_yomitoku_job(job_id, input_filenames, base_cmd, translate_enabled, target_lang, ollama_model, custom_prompt, num_ctx, job_path, output_format)
            else:
                log_to_job(job_id, "❌ Timeout: Unable to acquire GPU lock", 'error')
                with data_lock:
                    job_data[job_id]['status'] = 'error'
        finally:
            if acquired:
                log_to_job(job_id, "🏁 Job finished, cleaning up...", 'info')
                force_unload_ollama(job_id)
                gpu_lock.release()
                log_to_job(job_id, "🔓 GPU lock released", 'info')
    else:
        run_yomitoku_job(job_id, input_filenames, base_cmd, translate_enabled, target_lang, ollama_model, custom_prompt, num_ctx, job_path, output_format)

def log_to_job(job_id, message, level='info', progress=None):
    with data_lock:
        if job_id not in job_data or 'logs' not in job_data[job_id]:
            job_data[job_id] = {
                'logs': deque(maxlen=1000),
                'progress': 0,
                'status': 'running',
                'current_page': None,
                'total_pages': None
            }
        
        job_data[job_id]['logs'].append({
            'timestamp': time.time(),
            'message': message,
            'level': level
        })
        
        if progress is not None:
            job_data[job_id]['progress'] = progress
    
    print(f"[{job_id}] {message}")

def detect_ollama_models():
    global AVAILABLE_OLLAMA_MODELS
    print(f"\n{'='*60}")
    print("🔍 DETECTING OLLAMA MODELS...")
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            AVAILABLE_OLLAMA_MODELS = [m['name'] for m in models]
            print(f"✅ {len(AVAILABLE_OLLAMA_MODELS)} models detected: {AVAILABLE_OLLAMA_MODELS}")
            return True
    except:
        print("❌ Ollama is not accessible")
    return False

# Démarrage
print(f"🚀 STARTING YOMITOKU + OLLAMA SERVER")
detect_ollama_models()

# TRADUCTIONS (Interface Utilisateur uniquement)
TRANSLATIONS = {
    'fr': {
        'title': 'Yomitoku + Ollama', 'subtitle': 'Analyse & Traduction de documents',
        'select_file': 'Sélectionnez vos documents', 'format_label': 'Format de sortie',
        'formats': {'md': 'Markdown', 'html': 'HTML', 'json': 'JSON', 'csv': 'CSV', 'pdf': 'PDF (Traduction → HTML)'},
        'device': 'Périphérique', 'options': 'Options avancées', 'trans_options': 'Options de traduction',
        'vis': 'Générer la visualisation', 'lite': 'Mode léger (rapide)',
        'figure': 'Exporter les figures', 'figure_letter': 'Texte dans les figures',
        'ignore_line_break': 'Ignorer sauts de ligne', 'combine': 'Fusionner les pages',
        'ignore_meta': 'Ignorer en-têtes/pieds', 'translate': 'Traduire avec Ollama',
        'target_lang': 'Langue cible', 'target_langs': {'fr': 'Français', 'en': 'Anglais', 'es': 'Espagnol', 'de': 'Allemand'},
        'ollama_model': 'Modèle Ollama', 'custom_prompt': 'Prompt personnalisé (optionnel)',
        'custom_prompt_help': 'Laissez vide pour utiliser le prompt par défaut.',
        'ctx_label': 'Taille du contexte',
        'ctx_help': 'Mémoire de travail de l\'IA (en tokens). Plus elle est élevée, plus le traitement est lent mais accepte de longs textes. 4096 est recommandé pour la vitesse.',
        'launch': 'Lancer l\'analyse', 'drag_drop': 'Glissez-déposez vos fichiers ici ou cliquez',
        'success': 'Analyse terminée !', 'translating': 'Traduction en cours...',
        'error': 'Erreur', 'error_ollama': 'Erreur Ollama', 'download': 'Télécharger',
        'view_results': 'Voir les résultats', 'job_id': 'Job ID', 'files_generated': 'Fichiers générés',
        'visualizations': 'Visualisations', 'translated_files': 'Fichiers traduits',
        'no_files': 'Aucun fichier trouvé', 'back': 'Retour', 'recent_jobs': 'Analyses récentes',
        'no_models': 'Aucun modèle Ollama détecté', 'refresh_models': 'Actualiser les modèles',
        'tooltip_vis': 'Génère une image avec les zones de texte détectées encadrées',
        'tooltip_lite': 'Utilise un modèle plus rapide mais moins précis pour l\'OCR',
        'tooltip_figure': 'Extrait les graphiques et images du document en fichiers séparés',
        'tooltip_figure_letter': 'Détecte et extrait le texte présent à l\'intérieur des figures',
        'tooltip_ignore_line_break': 'Supprime les sauts de ligne pour créer un texte continu',
        'tooltip_combine': 'Combine toutes les pages en un seul fichier de résultat',
        'tooltip_ignore_meta': 'Ignore les en-têtes, pieds de page et numéros de page',
        'tooltip_translate': 'Active la traduction automatique via Ollama après l\'OCR',
        'progress_processing': 'Traitement en cours...', 'progress_page': 'Page',
        'progress_of': 'sur', 'progress_complete': 'Analyse terminée !',
        'view_btn': 'Voir', 'calculating': 'Calcul...', 'total_size': 'Total',
        'no_jobs_found': 'Aucune analyse trouvée', 'click_view': 'Cliquez pour voir les résultats',
        'file_count_label': 'fichier(s)', 'multi_files': 'Fichiers multiples autorisés (Max: 200MB)',
        'modify_prompt': 'Modifiez le prompt ci-dessous selon vos besoins',
        'models_detected': 'modèle(s) détecté(s)',
        'variables': 'Variables',
        'p_default': 'Défaut', 'p_manga': 'Manga', 'p_game': 'Jeux vidéo',
        'p_famitsu': 'Famitsu', 'p_tech': 'Technique', 'p_admin': 'Administratif',
        'please_wait': 'Veuillez patienter'
    },
    'en': {
        'title': 'Yomitoku + Ollama', 'subtitle': 'Document Analysis & Translation',
        'select_file': 'Select documents', 'format_label': 'Output Format',
        'formats': {'md': 'Markdown', 'html': 'HTML', 'json': 'JSON', 'csv': 'CSV', 'pdf': 'PDF (Translation → HTML)'},
        'device': 'Device', 'options': 'Advanced Options', 'trans_options': 'Translation Options',
        'vis': 'Generate visualization', 'lite': 'Lite mode (fast)',
        'figure': 'Export figures', 'figure_letter': 'Text in figures',
        'ignore_line_break': 'Ignore line breaks', 'combine': 'Merge pages',
        'ignore_meta': 'Ignore headers/footers', 'translate': 'Translate with Ollama',
        'target_lang': 'Target language', 'target_langs': {'fr': 'French', 'en': 'English', 'es': 'Spanish', 'de': 'German'},
        'ollama_model': 'Ollama Model', 'custom_prompt': 'Custom prompt (optional)',
        'custom_prompt_help': 'Leave empty for default prompt.',
        'ctx_label': 'Context Size',
        'ctx_help': 'AI working memory (in tokens). Higher values are slower but handle longer texts. 4096 is recommended for speed.',
        'launch': 'Launch Analysis', 'drag_drop': 'Drag & drop your files here or click',
        'success': 'Analysis completed!', 'translating': 'Translation in progress...',
        'error': 'Error', 'error_ollama': 'Ollama error', 'download': 'Download',
        'view_results': 'View Results', 'job_id': 'Job ID', 'files_generated': 'Generated Files',
        'visualizations': 'Visualizations', 'translated_files': 'Translated Files',
        'no_files': 'No files found', 'back': 'Back', 'recent_jobs': 'Recent Analyses',
        'no_models': 'No Ollama models detected', 'refresh_models': 'Refresh models',
        'tooltip_vis': 'Generates an image with detected text areas framed',
        'tooltip_lite': 'Uses a faster but less accurate model for OCR',
        'tooltip_figure': 'Extracts charts and images from the document as separate files',
        'tooltip_figure_letter': 'Detects and extracts text inside figures and charts',
        'tooltip_ignore_line_break': 'Removes line breaks to create continuous text',
        'tooltip_combine': 'Combines all pages into a single result file',
        'tooltip_ignore_meta': 'Ignores headers, footers and page numbers',
        'tooltip_translate': 'Enables automatic translation via Ollama after OCR',
        'progress_processing': 'Processing...', 'progress_page': 'Page',
        'progress_of': 'of', 'progress_complete': 'Analysis completed!',
        'view_btn': 'View', 'calculating': 'Calculating...', 'total_size': 'Total',
        'no_jobs_found': 'No analysis found', 'click_view': 'Click to view results',
        'file_count_label': 'file(s)', 'multi_files': 'Multi-files allowed (Max: 200MB total)',
        'modify_prompt': 'Modify the prompt below according to your needs',
        'models_detected': 'model(s) detected',
        'variables': 'Variables',
        'p_default': 'Default', 'p_manga': 'Manga', 'p_game': 'Video Games',
        'p_famitsu': 'Famitsu', 'p_tech': 'Technical', 'p_admin': 'Administrative',
        'please_wait': 'Please wait'        
    },
    'ja': {
        'title': 'Yomitoku + Ollama', 'subtitle': '文書分析 & 翻訳',
        'select_file': '文書を選択', 'format_label': '出力形式',
        'formats': {'md': 'Markdown', 'html': 'HTML', 'json': 'JSON', 'csv': 'CSV', 'pdf': 'PDF (翻訳 → HTML)'},
        'device': 'デバイス', 'options': '高度なオプション', 'trans_options': '翻訳オプション',
        'vis': '可視化を生成', 'lite': 'ライトモード(高速)',
        'figure': '図をエクスポート', 'figure_letter': '図内の文字',
        'ignore_line_break': '改行を無視', 'combine': 'ページを結合',
        'ignore_meta': 'ヘッダー/フッターを無視', 'translate': 'Ollamaで翻訳',
        'target_lang': 'ターゲット言語', 'target_langs': {'fr': 'フランス語', 'en': '英語', 'es': 'スペイン語', 'de': 'ドイツ語'},
        'ollama_model': 'Ollamaモデル', 'custom_prompt': 'カスタムプロンプト(オプション)',
        'custom_prompt_help': 'デフォルトプロンプトを使用する場合は空白のままにします。',
        'ctx_label': 'コンテキストサイズ',
        'ctx_help': 'AIの作業メモリ（トークン単位）。値が高いほど長文を扱えますが、処理は遅くなります。速度重視なら4096が推奨です。',
        'launch': '分析を開始', 'drag_drop': 'ここにファイルをドラッグ&ドロップ',
        'success': '分析が完了しました!', 'translating': '翻訳中...',
        'error': 'エラー', 'error_ollama': 'Ollamaエラー', 'download': 'ダウンロード',
        'view_results': '結果を表示', 'job_id': 'ジョブID', 'files_generated': '生成されたファイル',
        'visualizations': '可視化', 'translated_files': '翻訳済みファイル',
        'no_files': 'ファイルが見つかりません', 'back': '戻る', 'recent_jobs': '最近の分析',
        'no_models': 'Ollamaモデルが検出されません', 'refresh_models': 'モデルを更新',
        'tooltip_vis': '検出されたテキストエリアをフレームで囲んだ画像を生成します',
        'tooltip_lite': 'OCR用により高速ですが精度の低いモデルを使用します',
        'tooltip_figure': 'ドキュメントからグラフや画像を別ファイルとして抽出します',
        'tooltip_figure_letter': '図やグラフ内のテキストを検出して抽出します',
        'tooltip_ignore_line_break': '改行を削除して連続テキストを作成します',
        'tooltip_combine': 'すべてのページを1つの結果ファイルに結合します',
        'tooltip_ignore_meta': 'ヘッダー、フッター、ページ番号を無視します',
        'tooltip_translate': 'OCR後にOllamaによる自動翻訳を有効にします',
        'progress_processing': '処理中...', 'progress_page': 'ページ', 'progress_of': '／', 'progress_complete': '分析が完了しました!',
        'view_btn': '表示', 'calculating': '計算中...', 'total_size': '合計',
        'no_jobs_found': '分析履歴がありません', 'click_view': '結果を表示するにはクリック',
        'file_count_label': 'ファイル', 'multi_files': '複数ファイル対応 (最大合計: 200MB)',
        'modify_prompt': '必要に応じて以下のプロンプトを修正してください',
        'models_detected': '個のモデルを検出',
        'variables': '変数',
        'p_default': 'デフォルト', 'p_manga': 'マンガ', 'p_game': 'ビデオゲーム',
        'p_famitsu': 'ファミ通', 'p_tech': '技術書', 'p_admin': '行政文書',
        'please_wait': 'お待ちください'
    }
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_job_path(job_id):
    return Path(app.config['OUTPUT_FOLDER']) / job_id

def get_lang():
    return session.get('lang', 'fr')

def translate_with_ollama(text, target_lang='fr', model=None, custom_prompt=None, num_ctx=4096, job_id=None, output_format='md'):
    """Traduit avec Ollama en surveillant la VRAM"""
    
    if not wait_for_vram(required_gb=4.0, timeout=20, job_id=job_id):
         log_to_job(job_id, "⚠️ Low VRAM before translation, risk of failure...", 'warning')

    # Dictionnaire des formats pour le prompt
    FORMAT_NAMES = {
        'md': 'Markdown', 
        'html': 'HTML', 
        'json': 'JSON', 
        'csv': 'CSV',
        'pdf': 'text extracted from a PDF'
    }
    
    format_name = FORMAT_NAMES.get(output_format, output_format)
    
    LANG_NAMES = {
        'fr': 'French', 'en': 'English', 'es': 'Spanish', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'ru': 'Russian',
        'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean'
    }
    target_lang_full = LANG_NAMES.get(target_lang, target_lang)
    
    if len(text.strip()) < 10:
        return text
    
    try:
        model_to_use = model or app.config['OLLAMA_MODEL']
        
        messages = []
        if custom_prompt and custom_prompt.strip():
            # Injection des variables dans le prompt perso
            safe_prompt = custom_prompt.replace('{target_lang}', target_lang_full).replace('{format}', format_name)
            messages.append({"role": "system", "content": safe_prompt})
        else:
            # Prompt système par défaut
            messages.append({
                "role": "system",
                "content": f"""You are a professional translator. 
Translate the following {format_name} from Japanese to {target_lang_full}.
Maintain the original meaning and nuances.
Return ONLY the translated text."""
            })
        
        messages.append({"role": "user", "content": text})
        
        response = requests.post(
            'http://127.0.0.1:11434/api/chat',
            json={
                "model": model_to_use, 
                "messages": messages, 
                "stream": False,
                "options": {
                    "temperature": 0.1, 
                    "top_p": 0.9, 
                    "num_ctx": num_ctx, 
                    "num_predict": -1 
                }
            },
            timeout=app.config['OLLAMA_TIMEOUT']
        )
        
        if response.status_code == 200:
            result = response.json()
            translated = result['message']['content'].strip()
            return translated
        else:
            log_to_job(job_id, f"❌ Ollama Error: {response.status_code}", 'error')
            return f"❌ Translation failed: {response.status_code}"
            
    except Exception as e:
        log_to_job(job_id, f"❌ Exception: {str(e)}", 'error')
        return f"❌ Translation error: {str(e)}"
    finally:
        force_unload_ollama(job_id)

def run_yomitoku_job(job_id, input_filenames, base_cmd, translate_enabled, target_lang, ollama_model, custom_prompt, num_ctx, job_path, output_format):
    """Exécute Yomitoku SÉQUENTIELLEMENT pour chaque fichier"""
    process = None
    try:
        log_to_job(job_id, f"📄 NEW BATCH ANALYSIS - Job ID: {job_id}", 'info')
        total_files = len(input_filenames)
        
        # Variable d'environnement
        my_env = os.environ.copy()
        my_env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        
        for file_idx, filename in enumerate(input_filenames):
            input_path = job_path / filename
            log_to_job(job_id, f"⏳ Processing file {file_idx + 1}/{total_files}: {filename}", 'info')
            
            # Construction de la commande pour CE fichier
            current_cmd = list(base_cmd)
            current_cmd.insert(1, str(input_path))
            
            process = subprocess.Popen(
                current_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, bufsize=1, env=my_env
            )
            
            # Lecture des logs
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    if 'Processing page' in line:
                        parts = line.split()
                        try:
                            current = int(parts[2].split('/')[0])
                            total = int(parts[2].split('/')[1])
                            # Calcul progression globale (pourcentage de fichier + pourcentage de page)
                            file_progress = (current / total)
                            global_progress = ((file_idx + file_progress) / total_files) * 100
                            
                            log_to_job(job_id, f"[{filename}] {line}", 'info', global_progress)
                        except:
                            log_to_job(job_id, line, 'info')
                    else:
                        log_to_job(job_id, f"[{filename}] {line}", 'info')
            
            returncode = process.wait()
            process.stdout.close()
            
            if returncode != 0:
                log_to_job(job_id, f"❌ Error on file {filename} (code {returncode})", 'error')
                # On continue quand même les autres fichiers
        
        log_to_job(job_id, "✅ All files processed", 'success')
        
        # TRADUCTION
        if translate_enabled:
            log_to_job(job_id, f"\n🌐 TRANSLATION to {target_lang} (Ctx: {num_ctx})", 'info')
            results_dir = job_path / 'results'
            files_to_translate = []
            
            # On inclut *.pdf dans la recherche
            for ext in ['*.md', '*.html', '*.txt', '*.json', '*.csv', '*.pdf']:
                files_to_translate.extend(results_dir.glob(ext))
            
            for i, file_path in enumerate(files_to_translate):
                # On saute les fichiers déjà traduits
                if file_path.name.startswith('translated_'): continue

                log_to_job(job_id, f"📝 Translating ({i+1}/{len(files_to_translate)}): {file_path.name}", 'info')
                
                try:
                    text = ""
                    is_pdf_source = (file_path.suffix.lower() == '.pdf')

                    # 1. Extraction du texte
                    if is_pdf_source:
                        try:
                            pdf = pdfium.PdfDocument(str(file_path))
                            text_pages = []
                            for page in pdf:
                                text_page = page.get_textpage()
                                text_pages.append(text_page.get_text_range())
                                text_page.close()
                            text = "\n\n".join(text_pages)
                            pdf.close()
                        except Exception as pdf_err:
                            log_to_job(job_id, f"⚠️ PDF Read Error: {pdf_err}", 'warning')
                            continue
                    else:
                        text = file_path.read_text(encoding='utf-8', errors='replace')

                    if not text.strip(): continue

                    # 2. Envoi à Ollama
                    translated = translate_with_ollama(text, target_lang, ollama_model, custom_prompt, num_ctx, job_id, output_format)
                    
                    if translated and not translated.startswith('❌'):
                        
                        # 3. Sauvegarde
                        if is_pdf_source:
                            # CAS SPÉCIAL : Source PDF -> Sortie HTML
                            new_name = f"translated_{target_lang}_{file_path.name}.html"
                            translated_file = results_dir / new_name
                            
                            # Traduction du titre du document HTML
                            titles_map = {
                                'fr': 'Traduction', 'en': 'Translation', 'ja': '翻訳', 
                                'es': 'Traducción', 'de': 'Übersetzung'
                            }
                            doc_title = titles_map.get(target_lang, 'Translation')
                            
                            # Template HTML simple pour un rendu propre
                            html_content = f"""<!DOCTYPE html>
<html lang="{target_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{doc_title}: {file_path.name}</title>
<style>
    body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: auto; background: #f4f4f9; }}
    .content {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); white-space: pre-wrap; }}
</style>
</head>
<body>
    <div class="content">{translated}</div>
</body>
</html>"""
                            translated_file.write_text(html_content, encoding='utf-8')
                            log_to_job(job_id, f"✅ Translated (Saved as HTML): {translated_file.name}", 'success')
                        
                        else:
                            # CAS STANDARD (Markdown, JSON, etc.)
                            new_name = f"translated_{target_lang}_{file_path.name}"
                            translated_file = results_dir / new_name
                            translated_file.write_text(translated, encoding='utf-8')
                            log_to_job(job_id, f"✅ Translated: {translated_file.name}", 'success')
                            
                except Exception as e:
                    log_to_job(job_id, f"❌ File error: {e}", 'error')

        with data_lock:
            job_data[job_id]['status'] = 'complete'
            job_data[job_id]['progress'] = 100
            
    except Exception as e:
        log_to_job(job_id, f"❌ General Exception: {str(e)}", 'error')
        with data_lock: job_data[job_id]['status'] = 'error'
    finally:
        if process and process.poll() is None:
            try: process.kill()
            except: pass
        force_unload_ollama(job_id)

@app.route('/')
def index():
    lang = get_lang()
    return render_template('index.html', lang=lang, translations=TRANSLATIONS[lang], ollama_models=AVAILABLE_OLLAMA_MODELS)

@app.route('/set_lang/<lang>')
def set_language(lang):
    if lang in ['fr', 'en', 'ja']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/api/ollama/models')
def get_ollama_models():
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            global AVAILABLE_OLLAMA_MODELS
            AVAILABLE_OLLAMA_MODELS = model_names
            return jsonify({'models': model_names, 'count': len(model_names), 'status': 'ok'})
        return jsonify({'models': [], 'count': 0, 'status': 'error'})
    except Exception as e:
        return jsonify({'models': [], 'count': 0, 'status': 'error', 'message': str(e)})

@app.route('/api/logs/<job_id>')
def stream_logs(job_id):
    def generate():
        timeout = 0
        while job_id not in job_data and timeout < 30:
            time.sleep(0.1); timeout += 0.1
        if job_id not in job_data:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return
        last_log_count = 0
        last_progress = 0
        while True:
            with data_lock:
                data = job_data.get(job_id, {})
                logs = list(data.get('logs', []))
                progress = data.get('progress', 0)
                status = data.get('status', 'running')
                cp, tp = data.get('current_page'), data.get('total_pages')
            if len(logs) > last_log_count:
                for log in logs[last_log_count:]: yield f"data: {json.dumps({'type': 'log', 'log': log})}\n\n"
                last_log_count = len(logs)
            if progress != last_progress:
                yield f"data: {json.dumps({'type': 'progress', 'progress': progress, 'current_page': cp, 'total_pages': tp})}\n\n"
                last_progress = progress
            if status in ['complete', 'error']:
                yield f"data: {json.dumps({'type': 'status', 'status': status})}\n\n"
                break
            time.sleep(0.2)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Gestion des messages d'erreur traduits
    lang = session.get('lang', 'fr')
    err_msgs = {
        'fr': {'no_file': 'Aucun fichier fourni', 'empty': 'Aucun fichier sélectionné', 'invalid': 'Aucun fichier valide'},
        'en': {'no_file': 'No file provided', 'empty': 'No file selected', 'invalid': 'No valid files'},
        'ja': {'no_file': 'ファイルがありません', 'empty': 'ファイルが選択されていません', 'invalid': '有効なファイルがありません'}
    }
    msgs = err_msgs.get(lang, err_msgs['en'])

    if 'file' not in request.files: return jsonify({'error': msgs['no_file']}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '': return jsonify({'error': msgs['empty']}), 400
    
    job_id = str(uuid.uuid4())[:8]
    job_path = get_job_path(job_id)
    job_path.mkdir(exist_ok=True)
    
    valid_filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(job_path / filename)
            valid_filenames.append(filename)
    
    if not valid_filenames:
        return jsonify({'error': msgs['invalid']}), 400
    
    output_format = request.form.get('format', 'md')
    device = request.form.get('device', 'cpu')
    translate_enabled = 'translate' in request.form
    target_lang = request.form.get('target_lang', 'fr')
    ollama_model = request.form.get('ollama_model', app.config['OLLAMA_MODEL'])
    custom_prompt = request.form.get('custom_prompt', '').strip()
    
    # Récupération de num_ctx avec fallback
    try:
        num_ctx = int(request.form.get('num_ctx', 4096))
    except ValueError:
        num_ctx = 4096

    base_cmd = ['yomitoku', '-f', output_format, '-o', str(job_path / 'results'), '-d', device]
    if 'vis' in request.form: base_cmd.append('-v')
    if 'lite' in request.form: base_cmd.append('-l')
    if 'figure' in request.form: base_cmd.append('--figure')
    if 'figure_letter' in request.form: base_cmd.append('--figure_letter')
    if 'ignore_line_break' in request.form: base_cmd.append('--ignore_line_break')
    if 'combine' in request.form: base_cmd.append('--combine')
    if 'ignore_meta' in request.form: base_cmd.append('--ignore_meta')
    
    gpu_lock = gpu_semaphore if device == 'cuda' else None
    executor.submit(run_yomitoku_job_with_lock, job_id, valid_filenames, base_cmd, translate_enabled, 
                   target_lang, ollama_model, custom_prompt, num_ctx, job_path, output_format, gpu_lock)
    
    return jsonify({'job_id': job_id, 'success': True, 'files': []})

@app.route('/download/<job_id>/<filename>')
def download_file(job_id, filename):
    return send_file(get_job_path(job_id) / 'results' / filename, as_attachment=True)

@app.route('/view/<job_id>/<filename>')
def view_file(job_id, filename):
    p = get_job_path(job_id) / 'results' / filename
    mt = {
        '.txt': 'text/plain', 
        '.md': 'text/markdown', 
        '.html': 'text/html', 
        '.json': 'application/json', 
        '.csv': 'text/csv', 
        '.png': 'image/png', 
        '.jpg': 'image/jpeg',
        '.pdf': 'application/pdf'
    }
    return send_file(p, mimetype=mt.get(p.suffix.lower(), 'application/octet-stream'))

@app.route('/results/<job_id>')
def view_results(job_id):
    rd = get_job_path(job_id) / 'results'
    if not rd.exists(): return "Results not found", 404
    files, vis, trans = [], [], []
    for f in rd.iterdir():
        if f.is_file():
            if 'vis' in f.name and f.suffix in ['.jpg','.png']: vis.append(f.name)
            elif f.name.startswith('translated_'): trans.append(f.name)
            else: files.append({'name': f.name, 'size': f"{f.stat().st_size/1024:.1f} KB"})
    return render_template('results.html', job_id=job_id, files=files, visualizations=vis, translated_files=trans, lang=get_lang(), translations=TRANSLATIONS[get_lang()])

@app.route('/jobs')
def list_jobs_page(): return render_template('jobs.html', lang=get_lang(), translations=TRANSLATIONS[get_lang()])

@app.route('/api/jobs')
def list_jobs():
    jobs = []
    for d in Path(app.config['OUTPUT_FOLDER']).iterdir():
        if d.is_dir() and (d/'results').exists():
            jobs.append({'id': d.name, 'created': d.stat().st_ctime, 'files_count': len(list((d/'results').glob('*'))), 'has_visualizations': len(list((d/'results').glob('*.png')))>0, 'has_translations': len(list((d/'results').glob('translated_*')))>0})
    return jsonify(sorted(jobs, key=lambda x: x['created'], reverse=True))

@app.route('/api/job/<job_id>')
def get_job_info(job_id):
    jp = get_job_path(job_id)
    if not jp.exists(): return jsonify({'error': 'Not found'}), 404
    rd = jp / 'results'
    files, vis, trans = [], [], []
    for f in rd.iterdir():
        if f.is_file():
            fi = {'name': f.name, 'size': f.stat().st_size, 'url': url_for('download_file', job_id=job_id, filename=f.name), 'view_url': url_for('view_file', job_id=job_id, filename=f.name)}
            if 'vis' in f.name and f.suffix in ['.jpg','.png']: vis.append(fi)
            elif f.name.startswith('translated_'): trans.append(fi)
            else: files.append(fi)
    return jsonify({'job_id': job_id, 'files': files, 'visualizations': vis, 'translated_files': trans, 'created': jp.stat().st_ctime})

if __name__ == '__main__':
    print("🚀 SERVER STARTING (V3.2 - CTX OPTION)")
    if AVAILABLE_OLLAMA_MODELS: print(f"📦 Models: {AVAILABLE_OLLAMA_MODELS}")
    app.run(debug=False, host='0.0.0.0', port=5000)