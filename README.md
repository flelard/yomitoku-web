# Yomitoku-Web 🚀

A web interface for the powerful command-line Japanese OCR tool, [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku).

This project provides a user-friendly UI to access all of Yomitoku's features and adds an automatic translation layer using a locally-run [Ollama](https://ollama.com/) instance.

---

&lt;details&gt;
&lt;summary&gt;🇬🇧 English Instructions&lt;/summary&gt;

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

### Specialized Translation Prompts
The interface offers several optimized translation profiles:
- **Default**: General-purpose translation
- **Manga**: Preserves style and cultural nuances specific to manga, adapts sound effects naturally
- **Video Games**: Uses gaming terminology and maintains an immersive style, preserves character names
- **Technical**: Precise terminology for IT and software documentation, preserves code snippets
- **Administrative**: Formal language for official Japanese documents, preserves dates and titles

### Job Navigation & File Management
- Access all previous analyses via the "Recent Analyses" menu
- View generated files directly in the browser with the "View" button
- Download files individually or browse job results
- Real-time progress tracking with live logs

## Usage

1.  **Launch the Flask application:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternatively, you can run `python app.py`)*

2.  **Open your web browser:**
    Navigate to `http://&lt;YOUR_SERVER_IP&gt;:5000`.

3.  **Use the interface:**
    - Upload an image or PDF file.
    - Select your desired analysis and translation options.
    - Choose a specialized prompt if needed.
    - Launch the process and view the results.

&lt;/details&gt;

---

&lt;details&gt;
&lt;summary&gt;🇫🇷 Instructions en Français&lt;/summary&gt;

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

### Prompts de traduction spécialisés
L'interface propose plusieurs profils de traduction optimisés :
- **Défaut** : Traduction polyvalente générale
- **Manga** : Préserve le style et les nuances culturelles propres aux mangas, adapte les bruitages naturellement
- **Jeux vidéo** : Utilise la terminologie gaming et maintient un style immersif, préserve les noms de personnages
- **Technique** : Terminologie précise pour la documentation IT, préserve les extraits de code
- **Administratif** : Langage formel pour documents officiels japonais, préserve les dates et titres

### Navigation entre les analyses et gestion des fichiers
- Accédez à toutes les analyses précédentes via le menu "Analyses récentes"
- Visualisez les fichiers générés directement dans le navigateur avec le bouton "Voir"
- Téléchargez les fichiers individuellement ou parcourez les résultats
- Suivi de progression en temps réel avec logs en direct

## Utilisation

1.  **Lancez l'application Flask :**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternativement, vous pouvez lancer `python app.py`)*

2.  **Ouvrez votre navigateur web :**
    Rendez-vous à l'adresse `http://&lt;IP_DE_VOTRE_SERVEUR&gt;:5000`.

3.  **Utilisez l'interface :**
    - Uploadez une image ou un fichier PDF.
    - Choisissez les options d'analyse et de traduction.
    - Sélectionnez un prompt spécialisé si nécessaire.
    - Lancez le traitement et consultez les résultats.

&lt;/details&gt;

---

&lt;details&gt;
&lt;summary&gt;🇯🇵 日本語の説明書&lt;/summary&gt;

## 謝辞

このプロジェクトは、**木下小太郎氏**による素晴らしいオリジナルプロジェクト**Yomitoku**の上に構築されたWebインターフェースです。

- **オリジナルプロジェクト:** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
- **ライセンス:** 派生作品として、このプロジェクトも[CC BY-NC-SA 4.0 ライセンス](https://creativecommons.org/licenses/by-nc-sa/4.0/)の下で配布されます。

## 前提条件

- Python 3.10以降
- 翻訳機能を使用するには、お使いのマシンに[Ollama](https://ollama.com/)アプリケーションがインストールされ、実行されている必要があります。

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

### 専門翻訳プロンプト
インターフェースには最適化された複数の翻訳プロファイルがあります：
- **デフォルト** : 汎用翻訳
- **マンガ** : マンガ特有のスタイルと文化のニュアンスを保持、効果音を自然に適応
- **ビデオゲーム** : ゲーミング用語を使用し、没入型スタイルを維持、キャラクター名を保持
- **技術** : ITドキュメント用の正確な専門用語、コードスニペットを保持
- **行政** : 日本の公的文書用の formal な言語、日付とタイトルを正確に保持

### ジョブナビゲーションとファイル管理
- 「最近の分析」メニューですべての過去の分析にアクセス
- 「表示」ボタンですぐにブラウザで生成されたファイルを閲覧
- ファイルを個別にダウンロード、またはジョブ結果を閲覧
- ライブログでのリアルタイム進捗追跡

## 使い方

1.  **Flaskアプリケーションを起動します:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(または `python app.py` を実行)*

2.  **ウェブブラウザを開きます:**
    `http://&lt;サーバーのIPアドレス&gt;:5000` にアクセスしてください。

3.  **インターフェースを使用します:**
    - 画像またはPDFファイルをアップロードします。
    - 希望の分析および翻訳オプションを選択ます。
    - 必要に応じて専門プロンプトを選択します。
    - 処理を開始し、結果を表示します。

&lt;/details&gt;

---

## Technical Notes

- **File Upload Limit**: 50MB (configurable in `app.py`)
- **Supported Formats**: PDF, PNG, JPG, JPEG, TIFF, BMP
- **Ollama Integration**: Automatically detects available models on startup
- **GPU Support**: Enable CUDA acceleration by selecting "CUDA" as device
- **Output Formats**: Markdown (default), HTML, JSON, CSV
