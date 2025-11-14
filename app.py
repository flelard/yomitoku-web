import os
import uuid
import subprocess
import requests
import time
import json
import threading
from collections import deque
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, session, redirect, url_for, Response
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-multilingue-yomitoku-ollama-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['OLLAMA_TIMEOUT'] = 300
app.config['OLLAMA_MODEL'] = 'qwen3:8b'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

AVAILABLE_OLLAMA_MODELS = []

# Thread pool pour exécuter les jobs en arrière-plan
executor = ThreadPoolExecutor(max_workers=3)
atexit.register(lambda: executor.shutdown(wait=True))

# Stockage des données de job
job_data = {}
data_lock = threading.Lock()

def log_to_job(job_id, message, level='info', progress=None):
    """Ajoute un log et/ou une progression au job avec thread safety"""
    with data_lock:
        if job_id not in job_data:
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
        
        # Détecter la progression dans le message
        if 'Processing page' in message:
            parts = message.split()
            try:
                current = int(parts[2].split('/')[0])
                total = int(parts[2].split('/')[1])
                job_data[job_id]['progress'] = (current / total) * 100
                job_data[job_id]['current_page'] = current
                job_data[job_id]['total_pages'] = total
            except:
                pass
    
    print(f"[{job_id}] {message}")

def detect_ollama_models():
    """Détecte les modèles Ollama disponibles au démarrage"""
    global AVAILABLE_OLLAMA_MODELS
    print(f"\n{'='*60}")
    print("🔍 DÉTECTION DES MODÈLES OLLAMA...")
    
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            AVAILABLE_OLLAMA_MODELS = [m['name'] for m in models]
            print(f"✅ {len(AVAILABLE_OLLAMA_MODELS)} modèles détectés:")
            for model in AVAILABLE_OLLAMA_MODELS:
                print(f"   📦 {model}")
            print(f"{'='*60}\n")
            return True
        else:
            print(f"❌ Erreur Ollama: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama n'est pas accessible sur 127.0.0.1:11434")
        print("💡 Démarrez Ollama avec: sudo systemctl start ollama")
        print(f"{'='*60}\n")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"{'='*60}\n")
        return False

def cleanup_gpu_memory(job_id=None):
    """Libère la mémoire GPU (CUDA) pour éviter les OutOfMemory"""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # Obtenir les stats mémoire
            allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            reserved = torch.cuda.memory_reserved() / 1024**3    # GB
            
            if job_id:
                log_to_job(job_id, f"🧹 GPU nettoyé - Alloué: {allocated:.2f}GB, Réservé: {reserved:.2f}GB", 'info')
            else:
                print(f"🧹 GPU nettoyé - Alloué: {allocated:.2f}GB, Réservé: {reserved:.2f}GB")
            
            return True
    except ImportError:
        if job_id:
            log_to_job(job_id, "ℹ️ PyTorch non disponible, skip nettoyage GPU", 'info')
        return False
    except Exception as e:
        if job_id:
            log_to_job(job_id, f"⚠️ Erreur nettoyage GPU: {e}", 'warning')
        else:
            print(f"⚠️ Erreur nettoyage GPU: {e}")
        return False

# Détection des modèles au démarrage
print(f"🚀 DÉMARRAGE SERVEUR YOMITOKU + OLLAMA")
detect_ollama_models()

# Traductions complètes
TRANSLATIONS = {
    'fr': {
        'title': 'Yomitoku + Ollama',
        'subtitle': 'Analyse & Traduction de documents',
        'select_file': 'Sélectionnez un document',
        'format_label': 'Format de sortie',
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
        'custom_prompt': 'Prompt personnalisé (optionnel)',
        'custom_prompt_help': 'Laissez vide pour utiliser le prompt par défaut. Variables disponibles: {text}, {target_lang}',
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
        'recent_jobs': 'Analyses récentes',
        'no_models': 'Aucun modèle Ollama détecté',
        'refresh_models': 'Actualiser les modèles',
        # Tooltips
        'tooltip_vis': 'Génère une image avec les zones de texte détectées encadrées',
        'tooltip_lite': 'Utilise un modèle plus rapide mais moins précis pour l\'OCR',
        'tooltip_figure': 'Extrait les graphiques et images du document en fichiers séparés',
        'tooltip_figure_letter': 'Détecte et extrait le texte présent à l\'intérieur des figures',
        'tooltip_ignore_line_break': 'Supprime les sauts de ligne pour créer un texte continu',
        'tooltip_combine': 'Combine toutes les pages en un seul fichier de résultat',
        'tooltip_ignore_meta': 'Ignore les en-têtes, pieds de page et numéros de page',
        'tooltip_translate': 'Active la traduction automatique via Ollama après l\'OCR',
        # Progression
        'progress_processing': 'Traitement en cours...',
        'progress_page': 'Page',
        'progress_of': 'sur',
        'progress_complete': 'Analyse terminée !'
    },
    'en': {
        'title': 'Yomitoku + Ollama',
        'subtitle': 'Document Analysis & Translation',
        'select_file': 'Select a document',
        'format_label': 'Output Format',
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
        'custom_prompt': 'Custom prompt (optional)',
        'custom_prompt_help': 'Leave empty for default prompt. Available variables: {text}, {target_lang}',
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
        'recent_jobs': 'Recent Analyses',
        'no_models': 'No Ollama models detected',
        'refresh_models': 'Refresh models',
        # Tooltips
        'tooltip_vis': 'Generates an image with detected text areas framed',
        'tooltip_lite': 'Uses a faster but less accurate model for OCR',
        'tooltip_figure': 'Extracts charts and images from the document as separate files',
        'tooltip_figure_letter': 'Detects and extracts text inside figures and charts',
        'tooltip_ignore_line_break': 'Removes line breaks to create continuous text',
        'tooltip_combine': 'Combines all pages into a single result file',
        'tooltip_ignore_meta': 'Ignores headers, footers and page numbers',
        'tooltip_translate': 'Enables automatic translation via Ollama after OCR',
        # Progression
        'progress_processing': 'Processing...',
        'progress_page': 'Page',
        'progress_of': 'of',
        'progress_complete': 'Analysis completed!'
    },
    'ja': {
        'title': 'Yomitoku + Ollama',
        'subtitle': '文書分析 & 翻訳',
        'select_file': '文書を選択',
        'format_label': '出力形式',
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
        'lite': 'ライトモード(高速)',
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
        'custom_prompt': 'カスタムプロンプト(オプション)',
        'custom_prompt_help': 'デフォルトプロンプトを使用する場合は空白のままにします。利用可能な変数: {text}, {target_lang}',
        'launch': '分析を開始',
        'drag_drop': 'ここにファイルをドラッグ&ドロップ、またはクリックして選択',
        'success': '分析が完了しました!',
        'translating': '翻訳中...',
        'error': 'エラー',
        'error_ollama': 'Ollamaエラー(起動していません?)',
        'download': 'ダウンロード',
        'view_results': '結果を表示',
        'job_id': 'ジョブID',
        'files_generated': '生成されたファイル',
        'visualizations': '可視化',
        'translated_files': '翻訳済みファイル',
        'no_files': 'ファイルが見つかりません',
        'back': '戻る',
        'recent_jobs': '最近の分析',
        'no_models': 'Ollamaモデルが検出されません',
        'refresh_models': 'モデルを更新',
        # Tooltips
        'tooltip_vis': '検出されたテキストエリアをフレームで囲んだ画像を生成します',
        'tooltip_lite': 'OCR用により高速ですが精度の低いモデルを使用します',
        'tooltip_figure': 'ドキュメントからグラフや画像を別ファイルとして抽出します',
        'tooltip_figure_letter': '図やグラフ内のテキストを検出して抽出します',
        'tooltip_ignore_line_break': '改行を削除して連続テキストを作成します',
        'tooltip_combine': 'すべてのページを1つの結果ファイルに結合します',
        'tooltip_ignore_meta': 'ヘッダー、フッター、ページ番号を無視します',
        'tooltip_translate': 'OCR後にOllamaによる自動翻訳を有効にします',
        # Progression
        'progress_processing': '処理中...',
        'progress_page': 'ページ',
        'progress_of': '／',
        'progress_complete': '分析が完了しました!'
    }
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_job_path(job_id):
    return Path(app.config['OUTPUT_FOLDER']) / job_id

def get_lang():
    return session.get('lang', 'fr')

def translate_with_ollama(text, target_lang='fr', model=None, custom_prompt=None, job_id=None):
    """Traduit le texte avec Ollama local"""
    
    # ✅ Mapper les codes de langue vers les noms complets
    LANG_NAMES = {
        'fr': 'French',
        'en': 'English',
        'es': 'Spanish',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    }
    
    target_lang_full = LANG_NAMES.get(target_lang, target_lang)
    
    log_to_job(job_id, f"📄 Début traduction vers {target_lang_full}", 'info')
    log_to_job(job_id, f"🔧 Modèle: {model or app.config['OLLAMA_MODEL']}", 'info')
    
    if len(text.strip()) < 50:
        log_to_job(job_id, "⚠️ Texte trop court pour traduction (< 50 car)", 'warning')
        return text
    
    jap_chars = sum(1 for c in text if '\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF')
    log_to_job(job_id, f"🔍 Caractères japonais détectés: {jap_chars}", 'info')
    
    if jap_chars < 50:
        log_to_job(job_id, "⚠️ Peu de caractères japonais, traduction annulée", 'warning')
        return text + "\n\n[⚠️ Texte non-japonais détecté, traduction ignorée]"
    
    try:
        model_to_use = model or app.config['OLLAMA_MODEL']
        
        # ✅ CORRECTION : Utiliser le prompt personnalisé s'il existe
        if custom_prompt and custom_prompt.strip():
            # Remplacer les variables dans le prompt personnalisé avec le nom complet
            final_prompt = custom_prompt.replace('{text}', text).replace('{target_lang}', target_lang_full)
            log_to_job(job_id, "✨ Utilisation du prompt personnalisé", 'info')
        else:
            # Prompt par défaut si aucun prompt personnalisé
            final_prompt = f"Translate this Japanese text to {target_lang_full}. Return ONLY the translation:\n\n{text}"
            log_to_job(job_id, "📝 Utilisation du prompt par défaut", 'info')
        
        # Log du prompt utilisé (tronqué pour lisibilité)
        prompt_preview = final_prompt[:200] + "..." if len(final_prompt) > 200 else final_prompt
        log_to_job(job_id, f"💬 Prompt: {prompt_preview}", 'info')
        
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                "model": model_to_use,
                "prompt": final_prompt,  # ✅ Utiliser le prompt préparé
                "stream": False,
                "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 8000}
            },
            timeout=app.config['OLLAMA_TIMEOUT']
        )
        
        if response.status_code == 200:
            translated = response.json()['response'].strip()
            log_to_job(job_id, f"✅ Traduction terminée ({len(translated)} car)", 'success')
            
            # ✅ Libérer la VRAM GPU après traduction Ollama
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                    log_to_job(job_id, "🧹 VRAM GPU libérée", 'info')
            except Exception as cleanup_error:
                log_to_job(job_id, f"⚠️ Nettoyage GPU échoué: {cleanup_error}", 'warning')
            
            return translated
        else:
            log_to_job(job_id, f"❌ Erreur Ollama: {response.status_code}", 'error')
            return f"❌ Translation failed: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        log_to_job(job_id, "❌ ERREUR: Ollama non accessible", 'error')
        return "❌ ERROR: Ollama not running"
    except Exception as e:
        log_to_job(job_id, f"❌ Exception: {type(e).__name__}: {str(e)}", 'error')
        return f"❌ Translation error: {str(e)}"

def run_yomitoku_job(job_id, input_path, cmd, translate_enabled, target_lang, ollama_model, custom_prompt, job_path):
    """Exécute Yomitoku et la traduction en arrière-plan"""
    try:
        log_to_job(job_id, f"📄 NOUVELLE ANALYSE - Job ID: {job_id}", 'info')
        log_to_job(job_id, f"📝 Fichier: {input_path.name} ({input_path.stat().st_size} bytes)", 'info')
        log_to_job(job_id, f"🔧 Commande: {' '.join(cmd)}", 'info')
        
        # Nettoyage GPU avant Yomitoku
        cleanup_gpu_memory(job_id)
        
        # Démarrer Yomitoku
        log_to_job(job_id, "⏳ Démarrage d'Yomitoku...", 'info')
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Lire la sortie EN TEMPS RÉEL
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                
                # Capturer la progression
                if 'Processing page' in line:
                    parts = line.split()
                    try:
                        current = int(parts[2].split('/')[0])
                        total = int(parts[2].split('/')[1])
                        progress = (current / total) * 100
                        log_to_job(job_id, line, 'info', progress)
                    except:
                        log_to_job(job_id, line, 'info')
                else:
                    log_to_job(job_id, line, 'info')
        
        returncode = process.wait()
        
        # Nettoyage GPU après Yomitoku
        cleanup_gpu_memory(job_id)
        
        if returncode != 0:
            log_to_job(job_id, f"❌ Erreur Yomitoku (code {returncode})", 'error')
            with data_lock:
                job_data[job_id]['status'] = 'error'
            return
        
        log_to_job(job_id, "✅ Analyse Yomitoku terminée", 'success')
        
        # TRADUCTION
        if translate_enabled:
            log_to_job(job_id, f"\n🌐 TRADUCTION vers {target_lang} avec {ollama_model}", 'info')
            
            # Nettoyage GPU avant traduction
            cleanup_gpu_memory(job_id)
            
            results_dir = job_path / 'results'
            
            files_to_translate = []
            for ext in ['*.md', '*.html', '*.txt', '*.json', '*.csv']:
                files_to_translate.extend(results_dir.glob(ext))
            
            log_to_job(job_id, f"📄 Fichiers à traduire: {len(files_to_translate)}", 'info')
            
            if not files_to_translate:
                log_to_job(job_id, "❌ Aucun fichier texte trouvé !", 'error')
            
            for i, file_path in enumerate(files_to_translate[:2]):
                log_to_job(job_id, f"\n📝 Traduction fichier {i+1}/{len(files_to_translate)}: {file_path.name}", 'info')
                
                try:
                    text = file_path.read_text(encoding='utf-8', errors='ignore')
                    log_to_job(job_id, f"📊 Taille texte: {len(text)} caractères", 'info')
                    
                    translated = translate_with_ollama(text, target_lang, ollama_model, custom_prompt, job_id)
                    
                    if translated and not translated.startswith('❌'):
                        translated_file = results_dir / f"translated_{target_lang}_{file_path.name}"
                        translated_file.write_text(translated, encoding='utf-8')
                        log_to_job(job_id, f"✅ Sauvegardé: {translated_file.name}", 'success')
                    else:
                        log_to_job(job_id, f"❌ Échec: {translated}", 'error')
                        
                except Exception as e:
                    log_to_job(job_id, f"❌ Exception: {e}", 'error')
                
                # Nettoyage GPU après chaque fichier
                cleanup_gpu_memory(job_id)
        
        # Nettoyage GPU final
        cleanup_gpu_memory(job_id)
        
        # Finaliser
        with data_lock:
            job_data[job_id]['status'] = 'complete'
            job_data[job_id]['progress'] = 100
            
    except Exception as e:
        log_to_job(job_id, f"❌ Exception générale: {str(e)}", 'error')
        with data_lock:
            job_data[job_id]['status'] = 'error'
        
        # Nettoyage GPU même en cas d'erreur
        cleanup_gpu_memory(job_id)

@app.route('/')
def index():
    lang = get_lang()
    return render_template('index.html', 
                         lang=lang, 
                         translations=TRANSLATIONS[lang],
                         ollama_models=AVAILABLE_OLLAMA_MODELS)

@app.route('/set_lang/<lang>')
def set_language(lang):
    if lang in ['fr', 'en', 'ja']:
        session['lang'] = lang
        print(f"🌐 Changement langue: {lang}")
    return redirect(request.referrer or url_for('index'))

@app.route('/api/ollama/models')
def get_ollama_models():
    """API pour récupérer la liste des modèles Ollama"""
    try:
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            global AVAILABLE_OLLAMA_MODELS
            AVAILABLE_OLLAMA_MODELS = model_names
            print(f"✅ API /api/ollama/models : {len(model_names)} modèles trouvés")
            
            return jsonify({
                'models': model_names,
                'count': len(model_names),
                'status': 'ok'
            })
        else:
            print(f"❌ Ollama API erreur: {response.status_code}")
            return jsonify({
                'models': [],
                'count': 0,
                'status': 'error',
                'message': f'Ollama returned status {response.status_code}'
            }), 500
    except requests.exceptions.ConnectionError:
        print("❌ Ollama non accessible sur 127.0.0.1:11434")
        return jsonify({
            'models': [],
            'count': 0,
            'status': 'error',
            'message': 'Ollama is not running on the server (127.0.0.1:11434)'
        }), 503
    except Exception as e:
        print(f"❌ Exception API: {e}")
        return jsonify({
            'models': [],
            'count': 0,
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/logs/<job_id>')
def stream_logs(job_id):
    """Stream les logs en temps réel via Server-Sent Events"""
    def generate():
        timeout = 0
        while job_id not in job_data and timeout < 30:
            time.sleep(0.1)
            timeout += 0.1
        
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
                current_page = data.get('current_page')
                total_pages = data.get('total_pages')
            
            # Envoyer nouveaux logs
            if len(logs) > last_log_count:
                for log in logs[last_log_count:]:
                    yield f"data: {json.dumps({'type': 'log', 'log': log})}\n\n"
                last_log_count = len(logs)
            
            # Envoyer progression si changée
            if progress != last_progress:
                yield f"data: {json.dumps({'type': 'progress', 'progress': progress, 'current_page': current_page, 'total_pages': total_pages})}\n\n"
                last_progress = progress
            
            # Vérifier fin
            if status in ['complete', 'error']:
                yield f"data: {json.dumps({'type': 'status', 'status': status})}\n\n"
                break
            
            time.sleep(0.2)
    
    return Response(generate(), mimetype='text/event-stream')

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
    
    # Construire la commande
    output_format = request.form.get('format', 'md')
    device = request.form.get('device', 'cpu')
    translate_enabled = 'translate' in request.form
    target_lang = request.form.get('target_lang', 'fr')
    ollama_model = request.form.get('ollama_model', app.config['OLLAMA_MODEL'])
    custom_prompt = request.form.get('custom_prompt', '').strip()
    
    cmd = ['yomitoku', str(input_path), '-f', output_format, '-o', str(job_path / 'results'), '-d', device]
    
    if 'vis' in request.form: cmd.append('-v')
    if 'lite' in request.form: cmd.append('-l')
    if 'figure' in request.form: cmd.append('--figure')
    if 'figure_letter' in request.form: cmd.append('--figure_letter')
    if 'ignore_line_break' in request.form: cmd.append('--ignore_line_break')
    if 'combine' in request.form: cmd.append('--combine')
    if 'ignore_meta' in request.form: cmd.append('--ignore_meta')
    
    # DÉMARRER LE TRAITEMENT EN ARRIÈRE-PLAN (libère immédiatement la route)
    executor.submit(run_yomitoku_job, job_id, input_path, cmd, translate_enabled, target_lang, ollama_model, custom_prompt, job_path)
    
    # RETOURNER IMMÉDIATEMENT avec le job_id
    return jsonify({'job_id': job_id, 'success': True, 'files': []})

@app.route('/download/<job_id>/<filename>')
def download_file(job_id, filename):
    job_path = get_job_path(job_id)
    file_path = job_path / 'results' / filename
    
    if not file_path.exists():
        return "File not found", 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/view/<job_id>/<filename>')
def view_file(job_id, filename):
    """Affiche un fichier dans le navigateur (au lieu de le télécharger)"""
    job_path = get_job_path(job_id)
    file_path = job_path / 'results' / filename
    
    if not file_path.exists():
        return "File not found", 404
    
    # Détecter le type MIME
    mime_types = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.html': 'text/html',
        '.json': 'application/json',
        '.csv': 'text/csv',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.pdf': 'application/pdf'
    }
    
    ext = file_path.suffix.lower()
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    # Pour les fichiers texte, forcer l'encodage UTF-8
    if ext in ['.txt', '.md', '.html', '.json', '.csv']:
        return send_file(file_path, mimetype=mime_type, as_attachment=False)
    
    # Pour les images et PDFs, afficher dans le navigateur
    return send_file(file_path, mimetype=mime_type, as_attachment=False)

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

# ===== NOUVELLES ROUTES =====

@app.route('/jobs')
def list_jobs_page():
    """Page de navigation entre tous les jobs"""
    lang = get_lang()
    return render_template('jobs.html', 
                         lang=lang, 
                         translations=TRANSLATIONS[lang])

@app.route('/api/jobs')
def list_jobs():
    """API améliorée pour lister les jobs avec plus d'infos"""
    jobs = []
    output_path = Path(app.config['OUTPUT_FOLDER'])
    
    for job_dir in output_path.iterdir():
        if job_dir.is_dir() and (job_dir / 'results').exists():
            created = job_dir.stat().st_ctime
            files_count = len(list((job_dir / 'results').glob('*')))
            
            jobs.append({
                'id': job_dir.name,
                'created': created,
                'files_count': files_count,
                'has_visualizations': len(list((job_dir / 'results').glob('*.png'))) > 0,
                'has_translations': len(list((job_dir / 'results').glob('translated_*'))) > 0
            })
    
    jobs.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(jobs)

@app.route('/api/job/<job_id>')
def get_job_info(job_id):
    """Obtenir les détails d'un job spécifique"""
    job_path = get_job_path(job_id)
    if not job_path.exists():
        return jsonify({'error': 'Job not found'}), 404
    
    results_dir = job_path / 'results'
    if not results_dir.exists():
        return jsonify({'error': 'No results found'}), 404
    
    files = []
    visualizations = []
    translated_files = []
    
    for file in results_dir.iterdir():
        if file.is_file():
            file_info = {
                'name': file.name,
                'size': file.stat().st_size,
                'url': url_for('download_file', job_id=job_id, filename=file.name),
                'view_url': url_for('view_file', job_id=job_id, filename=file.name)
            }
            
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png'] and 'vis' in file.name:
                visualizations.append(file_info)
            elif file.name.startswith('translated_'):
                translated_files.append(file_info)
            else:
                files.append(file_info)
    
    return jsonify({
        'job_id': job_id,
        'files': files,
        'visualizations': visualizations,
        'translated_files': translated_files,
        'created': job_path.stat().st_ctime
    })

if __name__ == '__main__':
    print("🚀 DÉMARRAGE DU SERVEUR...")
    print(f"🌐 Accédez à : http://<IP_VOTRE_SERVEUR>:5000")
    if AVAILABLE_OLLAMA_MODELS:
        print(f"📦 {len(AVAILABLE_OLLAMA_MODELS)} modèles Ollama détectés")
    else:
        print("⚠️  Aucun modèle Ollama détecté")
    app.run(debug=False, host='0.0.0.0', port=5000)
