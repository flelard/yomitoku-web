# Yomitoku-Web 🚀

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![License](https://img.shields.io/badge/license-CC_BY--NC--SA_4.0-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)

<!-- LANGUAGE NAVIGATION -->
<div align="center">
  <strong>
    <a href="#-english">🇺🇸 English</a> | 
    <a href="#-français">🇫🇷 Français</a> | 
    <a href="#-日本語">🇯🇵 日本語</a>
  </strong>
</div>

---

<a name="-english"></a>
## 🇺🇸 English

### Acknowledgements & Origin

This project is a **web-based wrapper** built upon the excellent work of **Kotaro Kinoshita** on the original **Yomitoku** project. This repository does not contain the core OCR engine itself but provides a graphical interface to use it.

*   **Original Project:** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
*   **Core Author:** Kotaro Kinoshita

### What does this tool do?

This application bridges the gap between powerful command-line tools and user accessibility. It combines two major technologies into a single workflow:

1.  **OCR (Optical Character Recognition)**: Uses the **Yomitoku** engine to analyze Japanese documents (PDF, Images) and extract text.
2.  **Translation**: Uses **Ollama** (Local LLMs) to automatically translate the extracted text into your target language.

**Key Benefit: 100% Offline & Private**
Unlike cloud services, this tool runs entirely on your hardware. Your documents never leave your computer, and you don't need an internet connection once the models are installed.

### Features

#### User Interface & Experience
*   **Drag & Drop Upload**: Simple interface to process files (PDF, JPG, PNG, TIFF, BMP).
*   **Real-time Monitoring**: View live server logs via SSE (Server-Sent Events) and a visual progress bar.
*   **Job History**: Access previous analyses and download results later via the `/jobs` page.
*   **Multi-format Output**: Export results to Markdown, HTML, JSON, or CSV.

#### Translation Capabilities
*   **Local AI Integration**: Connects seamlessly with a running Ollama instance.
*   **Contextual Prompts**: Select specialized prompts to guide the translation style (Default, Manga, Video Games, Technical, Administrative).

#### Advanced OCR Options
*   **Visualization**: Generate images with detected text boxes overlayed (`--vis`).
*   **Figure Extraction**: Automatically save charts and images as separate files (`--figure`).
*   **Lite Mode**: Use a faster, lightweight model (`-l`).

### Technical Aspects

#### Resource Management
*   **Concurrency**: Handles up to **2 jobs simultaneously** in the background.
*   **GPU Safety**: Implements a **GPU Lock** to ensure only one process accesses CUDA at a time.
*   **VRAM Protection**: Automatically monitors GPU memory and unloads Ollama models during the OCR phase to prevent Out-Of-Memory crashes.

#### Prerequisites
*   **Python 3.10+**
*   **Yomitoku**: `pip install yomitoku`
*   **Ollama**: Must be installed and running for translation features ([ollama.com](https://ollama.com)).
*   **(Recommended)**: NVIDIA GPU with CUDA support for reasonable performance.

#### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```
2.  Setup environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Run:
    ```bash
    python app.py
    # Open http://localhost:5000
    ```

### License
As a derivative work of Yomitoku, this project is distributed under the **[CC BY-NC-SA 4.0 License](https://creativecommons.org/licenses/by-nc-sa/4.0/)**.

---

<a name="-français"></a>
## 🇫🇷 Français

### Remerciements & Origine

Ce projet est une **interface graphique (wrapper)** construite sur l'excellent travail de **Kotaro Kinoshita** sur le projet original **Yomitoku**. Ce dépôt ne contient pas le moteur OCR lui-même mais fournit une interface pour l'utiliser.

*   **Projet Original :** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
*   **Auteur principal :** Kotaro Kinoshita

### Que fait cet outil ?

Cette application rend accessible des outils puissants en ligne de commande via une interface web simple. Elle combine deux technologies :

1.  **OCR (Reconnaissance de Caractères)** : Utilise le moteur **Yomitoku** pour analyser des documents japonais (PDF, Images) et en extraire le texte.
2.  **Traduction** : Utilise **Ollama** (IA Locale) pour traduire automatiquement le texte extrait vers la langue de votre choix.

**Avantage clé : 100% Hors-ligne & Privé**
Contrairement aux services cloud, cet outil tourne entièrement sur votre machine. Vos documents ne quittent jamais votre ordinateur et aucune connexion internet n'est requise une fois les modèles installés.

### Fonctionnalités

#### Interface & Expérience Utilisateur
*   **Upload Glisser-Déposer** : Interface simple pour traiter vos fichiers (PDF, JPG, PNG, TIFF, BMP).
*   **Suivi Temps Réel** : Visualisez les logs du serveur en direct et la barre de progression.
*   **Historique** : Accédez aux analyses précédentes et téléchargez les résultats via la page `/jobs`.
*   **Formats de Sortie** : Export vers Markdown, HTML, JSON ou CSV.

#### Capacités de Traduction
*   **Intégration IA Locale** : Se connecte automatiquement à une instance Ollama locale.
*   **Prompts Contextuels** : Choisissez des styles de traduction spécialisés (Défaut, Manga, Jeux Vidéo, Technique, Administratif).

#### Options OCR Avancées
*   **Visualisation** : Génère des images avec les zones de texte détectées encadrées (`--vis`).
*   **Extraction de Figures** : Sauvegarde automatiquement les graphiques et images à part (`--figure`).
*   **Mode Léger** : Utilise un modèle plus rapide et léger (`-l`).

### Aspects Techniques

#### Gestion des Ressources
*   **Concurrence** : Gère jusqu'à **2 tâches simultanément** en arrière-plan.
*   **Sécurité GPU** : Implémente un **Verrou GPU** pour garantir qu'un seul processus utilise CUDA à la fois.
*   **Protection VRAM** : Surveille la mémoire vidéo et décharge automatiquement les modèles Ollama pendant la phase OCR pour éviter les crashs mémoire.

#### Prérequis
*   **Python 3.10+**
*   **Yomitoku** : `pip install yomitoku`
*   **Ollama** : Doit être installé et lancé pour la traduction ([ollama.com](https://ollama.com)).
*   **(Recommandé)** : GPU NVIDIA avec support CUDA.

#### Installation
1.  Cloner le dépôt :
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```
2.  Configurer l'environnement :
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Windows : venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Lancer :
    ```bash
    python app.py
    # Ouvrir http://localhost:5000
    ```

### Licence
En tant que travail dérivé de Yomitoku, ce projet est distribué sous la licence **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)**.

---

<a name="-日本語"></a>
## 🇯🇵 日本語

### 謝辞と起源

本プロジェクトは、**木下小太郎様**による素晴らしいオリジナルプロジェクト**Yomitoku**を基盤として開発された**Webインターフェース（ラッパー）**です。本リポジトリにはOCRエンジンそのものは含まれておらず、それを利用するためのGUIを提供します。

*   **オリジナルプロジェクト:** [https://github.com/kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)
*   **原作者:** 木下 小太郎 様

### 概要

本ツールは、コマンドラインツールの操作を簡略化し、以下の2つの技術を統合します：

1.  **OCR (光学文字認識)**: **Yomitoku**エンジンを使用して、日本の文書（PDF、画像）からテキストを抽出します。
2.  **翻訳**: **Ollama**（ローカルLLM）を使用して、抽出されたテキストを自動的に翻訳します。

**利点: 完全なオフラインとプライバシー**
クラウドサービスとは異なり、すべてご自身のPC上で完結します。文書が外部に送信されることはなく、モデルのダウンロード後はインターネット接続も不要です。

### 機能

#### ユーザーインターフェース
*   **ドラッグ＆ドロップ**: ファイル（PDF, JPG, PNG等）を簡単にアップロード。
*   **リアルタイム監視**: サーバーログと進捗バーをライブで表示。
*   **履歴管理**: 過去の分析結果を保存し、`/jobs`ページからいつでもダウンロード可能。
*   **出力形式**: Markdown, HTML, JSON, CSVに対応。

#### 翻訳機能
*   **ローカルAI連携**: 実行中のOllamaインスタンスとシームレスに連携。
*   **専門プロンプト**: 文書の種類に応じた翻訳スタイルを選択可能（デフォルト、マンガ、ゲーム、技術書、行政文書）。

#### 高度なOCRオプション
*   **可視化**: テキスト領域を枠で囲んだ画像を生成 (`--vis`)。
*   **図版抽出**: 図やグラフを別ファイルとして保存 (`--figure`)。
*   **ライトモード**: 高速・軽量モデルを使用 (`-l`)。

### 技術仕様

#### リソース管理
*   **並列処理**: バックグラウンドで最大**2つのジョブ**を同時処理。
*   **GPUロック**: GPUの競合を防ぐため、一度に1つのプロセスのみがCUDAを使用するよう制御。
*   **VRAM保護**: OCR実行中はOllamaモデルを自動的にアンロードし、メモリ不足によるクラッシュを防止。

#### 前提条件
*   **Python 3.10+**
*   **Yomitoku**: `pip install yomitoku`
*   **Ollama**: 翻訳機能にはOllamaのインストールと起動が必要です ([ollama.com](https://ollama.com))。
*   **(推奨)**: CUDA対応のNVIDIA GPU。

#### インストール
1.  クローン:
    ```bash
    git clone https://github.com/flelard/yomitoku-web.git
    cd yomitoku-web
    ```
2.  環境設定:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  実行:
    ```bash
    python app.py
    # ブラウザで http://localhost:5000 を開く
    ```

### ライセンス
Yomitokuの派生作品として、本プロジェクトは **[CC BY-NC-SA 4.0 ライセンス](https://creativecommons.org/licenses/by-nc-sa/4.0/)** の下で配布されています。
