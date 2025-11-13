# Yomitoku-Web 🚀

A web interface for the powerful command-line Japanese OCR tool, [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku).

This project provides a user-friendly UI to access all of Yomitoku's features and adds an automatic translation layer using a locally-run [Ollama](https://ollama.com/) instance with real-time progress tracking.

---

<details>
<summary>🇬🇧 English Instructions</summary>

## Acknowledgements

This project is a web-based wrapper built upon the excellent work of **Kotaro Kinoshita** on the original **Yomitoku** project.

- **Original Project:** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
- **License:** As a derivative work, this project is also distributed under the [CC BY-NC-SA 4.0 License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Prerequisites

- Python 3.10+
- The [Ollama](https://ollama.com/) application must be installed and running on your machine to use the translation feature.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Features

### Real-time Progress Tracking
- **Live logs streaming** via Server-Sent Events (SSE)
- **Visual progress bar** showing page-by-page processing
- **Detailed console output** with color-coded log levels (info, success, warning, error)
- **Processing status indicator** during analysis

### Specialized Translation Prompts
The interface offers six optimized translation profiles:
- **Default**: General-purpose translation
- **Manga**: Preserves style and cultural nuances specific to manga, adapts sound effects naturally
- **Video Games**: Uses gaming terminology and maintains an immersive style, preserves character names
- **Famitsu**: Specialized for retro gaming magazines (1980s-1990s style), preserves the editorial tone of classic Japanese gaming press
- **Technical**: Precise terminology for IT and software documentation, preserves code snippets
- **Administrative**: Formal language for official Japanese documents, preserves dates and titles

### Job Management System
- **Unique job IDs** for each analysis with thread-safe processing
- **Job history page** (`/jobs`) to browse all previous analyses
- **Persistent results** stored in organized folders by job ID
- **Background processing** with ThreadPoolExecutor (max 3 concurrent jobs)

### File Management & Viewing
- **Direct browser viewing** with the "View" button for all file types
- **Download individual files** or browse complete job results
- **Image visualization** with automatic thumbnail generation
- **Multi-format support**: Markdown, HTML, JSON, CSV, PNG, JPEG

### API Endpoints
- **`/api/jobs`** - List all completed jobs with metadata
- **`/api/job/<job_id>`** - Get detailed information about a specific job
- **`/api/ollama/models`** - Retrieve available Ollama models
- **`/api/logs/<job_id>`** - Real-time log streaming (SSE)

### Advanced Options
- **Visualization generation** - Creates images with detected text areas framed
- **Lite mode** - Faster but less accurate OCR model
- **Figure extraction** - Extracts charts and images as separate files
- **Figure text detection** - Detects and extracts text inside figures
- **Line break handling** - Option to remove line breaks for continuous text
- **Page merging** - Combines all pages into a single output file
- **Metadata filtering** - Ignores headers, footers, and page numbers

## Usage

1.  **Launch the Flask application:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternatively, you can run `python app.py`)*

2.  **Open your web browser:**
    Navigate to `http://<YOUR_SERVER_IP>:5000`.

3.  **Use the interface:**
    - Upload an image or PDF file (max 50MB)
    - Select your desired analysis options
    - Choose output format (Markdown, HTML, JSON, CSV)
    - Enable translation and select a specialized prompt if needed
    - Launch the process and monitor real-time progress
    - View or download results directly from the interface
    - Access previous analyses via "Recent Analyses" menu

## Architecture Notes

- **Thread-safe job management** with data locks for concurrent access
- **Automatic Ollama model detection** on server startup
- **Session-based language preferences** (French, English, Japanese)
- **Bootstrap 5 responsive UI** with Font Awesome icons
- **Server-Sent Events** for real-time log streaming without polling

</details>

---

<details>
<summary>🇫🇷 Instructions en Français</summary>

## Remerciements

Ce projet est une interface web construite sur l'excellent travail de **Kotaro Kinoshita** sur le projet original **Yomitoku**.

- **Projet original :** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
- **Licence :** En tant que travail dérivé, ce projet est également distribué sous la licence [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Prérequis

- Python 3.10+
- L'application [Ollama](https://ollama.com/) doit être installée et en cours d'exécution sur votre machine pour utiliser la fonction de traduction.

## Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```

2.  **Créez et activez un environnement virtuel :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

## Fonctionnalités

### Suivi de progression en temps réel
- **Streaming de logs en direct** via Server-Sent Events (SSE)
- **Barre de progression visuelle** affichant le traitement page par page
- **Console détaillée** avec niveaux de logs colorés (info, succès, avertissement, erreur)
- **Indicateur de statut** pendant l'analyse

### Prompts de traduction spécialisés
L'interface propose six profils de traduction optimisés :
- **Défaut** : Traduction polyvalente générale
- **Manga** : Préserve le style et les nuances culturelles propres aux mangas, adapte les bruitages naturellement
- **Jeux vidéo** : Utilise la terminologie gaming et maintient un style immersif, préserve les noms de personnages
- **Famitsu** : Spécialisé pour les magazines gaming rétro (style années 1980-1990), préserve le ton éditorial de la presse japonaise classique
- **Technique** : Terminologie précise pour la documentation IT, préserve les extraits de code
- **Administratif** : Langage formel pour documents officiels japonais, préserve les dates et titres

### Système de gestion des jobs
- **IDs uniques** pour chaque analyse avec traitement thread-safe
- **Page d'historique** (`/jobs`) pour consulter toutes les analyses précédentes
- **Résultats persistants** stockés dans des dossiers organisés par ID
- **Traitement en arrière-plan** avec ThreadPoolExecutor (max 3 jobs simultanés)

### Gestion et visualisation des fichiers
- **Visualisation directe** dans le navigateur avec le bouton "Voir"
- **Téléchargement individuel** ou navigation complète des résultats
- **Visualisation d'images** avec génération automatique de miniatures
- **Support multi-formats** : Markdown, HTML, JSON, CSV, PNG, JPEG

### Points d'accès API
- **`/api/jobs`** - Liste tous les jobs terminés avec métadonnées
- **`/api/job/<job_id>`** - Informations détaillées sur un job spécifique
- **`/api/ollama/models`** - Récupère les modèles Ollama disponibles
- **`/api/logs/<job_id>`** - Streaming de logs en temps réel (SSE)

### Options avancées
- **Génération de visualisation** - Crée des images avec zones de texte détectées encadrées
- **Mode léger** - Modèle OCR plus rapide mais moins précis
- **Extraction de figures** - Extrait graphiques et images en fichiers séparés
- **Détection de texte dans figures** - Détecte et extrait le texte dans les figures
- **Gestion des sauts de ligne** - Option pour supprimer les retours à la ligne
- **Fusion de pages** - Combine toutes les pages en un seul fichier
- **Filtrage métadonnées** - Ignore en-têtes, pieds de page et numéros

## Utilisation

1.  **Lancez l'application Flask :**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternativement, vous pouvez lancer `python app.py`)*

2.  **Ouvrez votre navigateur web :**
    Rendez-vous à l'adresse `http://<IP_DE_VOTRE_SERVEUR>:5000`.

3.  **Utilisez l'interface :**
    - Uploadez une image ou un fichier PDF (max 50MB)
    - Choisissez les options d'analyse désirées
    - Sélectionnez le format de sortie (Markdown, HTML, JSON, CSV)
    - Activez la traduction et choisissez un prompt spécialisé si nécessaire
    - Lancez le traitement et suivez la progression en temps réel
    - Visualisez ou téléchargez les résultats directement
    - Accédez aux analyses précédentes via "Analyses récentes"

## Notes d'architecture

- **Gestion thread-safe des jobs** avec verrous pour accès concurrent
- **Détection automatique** des modèles Ollama au démarrage
- **Préférences linguistiques** par session (français, anglais, japonais)
- **Interface Bootstrap 5** responsive avec icônes Font Awesome
- **Server-Sent Events** pour streaming de logs sans polling

</details>

---

<details>
<summary>🇯🇵 日本語の説明書</summary>

## 謝辞

この度は、**木下小太郎様**による素晴らしいオリジナルプロジェクト**Yomitoku**を基盤として、Webインターフェースを開発させていただきました。木下様の卓越した技術と貢献に心より感謝申し上げます。

- **オリジナルプロジェクト:** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
- **ライセンス:** 派生作品として、このプロジェクトも[CC BY-NC-SA 4.0 ライセンス](https://creativecommons.org/licenses/by-nc-sa/4.0/)の下で配布させていただいております。

## 前提条件

- Python 3.10以降
- 翻訳機能を使用するには、お使いのマシンに[Ollama](https://ollama.com/)アプリケーションがインストールされ、実行されている必要がございます。

## インストール

1.  **リポジトリをクローンします:**
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```

2.  **仮想環境を作成して有効化します:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **依存関係をインストールします:**
    ```bash
    pip install -r requirements.txt
    ```

## 機能

### リアルタイム進捗追跡
- **ライブログストリーミング** - Server-Sent Events (SSE)による
- **ビジュアル進捗バー** - ページごとの処理状況を表示
- **詳細なコンソール出力** - カラーコード化されたログレベル（情報、成功、警告、エラー）
- **処理ステータスインジケーター** - 分析中の表示

### 専門翻訳プロンプト
インターフェースには6つの最適化された翻訳プロファイルがございます：
- **デフォルト** : 汎用翻訳
- **マンガ** : マンガ特有のスタイルと文化のニュアンスを保持、効果音を自然に適応
- **ビデオゲーム** : ゲーミング用語を使用し、没入型スタイルを維持、キャラクター名を保持
- **ファミ通** : レトロゲーミング雑誌（1980年代～1990年代スタイル）専用、クラシックな日本のゲーム誌の編集トーンを保持
- **技術** : IT・ソフトウェアドキュメント用の正確な専門用語、コードスニペットを保持
- **行政** : 日本の公的文書用のformalな言語、日付とタイトルを正確に保持

### ジョブ管理システム
- **一意のジョブID** - スレッドセーフな処理による各分析
- **ジョブ履歴ページ** (`/jobs`) - すべての過去の分析を閲覧可能
- **永続的な結果** - ジョブIDごとに整理されたフォルダに保存
- **バックグラウンド処理** - ThreadPoolExecutor使用（最大3つの同時ジョブ）

### ファイル管理と表示
- **ブラウザ直接表示** - すべてのファイルタイプで「表示」ボタンによる
- **個別ファイルダウンロード** - または完全なジョブ結果の閲覧
- **画像可視化** - サムネイルの自動生成付き
- **マルチフォーマット対応** : Markdown、HTML、JSON、CSV、PNG、JPEG

### APIエンドポイント
- **`/api/jobs`** - メタデータ付きの完了済みジョブ一覧
- **`/api/job/<job_id>`** - 特定ジョブの詳細情報取得
- **`/api/ollama/models`** - 利用可能なOllamaモデルの取得
- **`/api/logs/<job_id>`** - リアルタイムログストリーミング（SSE）

### 高度なオプション
- **可視化生成** - 検出されたテキストエリアをフレームで囲んだ画像を作成
- **ライトモード** - より高速ですが精度の低いOCRモデル使用
- **図の抽出** - グラフや画像を別ファイルとして抽出
- **図内テキスト検出** - 図やグラフ内のテキストを検出して抽出
- **改行処理** - 連続テキスト作成のため改行を削除するオプション
- **ページ結合** - すべてのページを1つの出力ファイルに統合
- **メタデータフィルタリング** - ヘッダー、フッター、ページ番号を無視

## 使い方

1.  **Flaskアプリケーションを起動します:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(または `python app.py` を実行)*

2.  **ウェブブラウザを開きます:**
    `http://<サーバーのIPアドレス>:5000` にアクセスしてください。

3.  **インターフェースを使用します:**
    - 画像またはPDFファイルをアップロード（最大50MB）
    - 希望の分析オプションを選択
    - 出力形式を選択（Markdown、HTML、JSON、CSV）
    - 必要に応じて翻訳を有効化し、専門プロンプトを選択
    - 処理を開始し、リアルタイム進捗を監視
    - インターフェースから直接結果を表示またはダウンロード
    - 「最近の分析」メニューから過去の分析にアクセス

## アーキテクチャに関する注記

- **スレッドセーフなジョブ管理** - 同時アクセス用のデータロック付き
- **自動Ollamaモデル検出** - サーバー起動時
- **セッションベースの言語設定** - フランス語、英語、日本語
- **Bootstrap 5レスポンシブUI** - Font Awesomeアイコン使用
- **Server-Sent Events** - ポーリングなしのリアルタイムログストリーミング

</details>

---

## Technical Notes

- **File Upload Limit**: 50MB (configurable in `app.py`)
- **Supported Formats**: PDF, PNG, JPG, JPEG, TIFF, BMP
- **Ollama Integration**: Automatically detects available models on startup with refresh capability
- **GPU Support**: Enable CUDA acceleration by selecting "CUDA" as device
- **Output Formats**: Markdown (default), HTML, JSON, CSV
- **Concurrent Processing**: Maximum 3 simultaneous jobs via ThreadPoolExecutor
- **Log Retention**: Last 1000 log entries per job stored in memory
- **Session Management**: Language preferences persist across page loads
- **Real-time Updates**: Log streaming via SSE with 200ms polling interval