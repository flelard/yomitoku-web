# Yomitoku-Web 🚀

A web interface for the powerful command-line Japanese OCR tool, [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku).

This project provides a user-friendly UI to access all of Yomitoku's features and adds an automatic translation layer using a locally-run [Ollama](https://ollama.com/) instance.

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

## Usage

1.  **Launch the Flask application:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternatively, you can run `python app.py`)*

2.  **Open your web browser:**
    Navigate to `http://<YOUR_SERVER_IP>:5000`.

3.  **Use the interface:**
    - Upload an image or PDF file.
    - Select your desired analysis and translation options.
    - Launch the process and view the results.

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

## Utilisation

1.  **Lancez l'application Flask :**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(Alternativement, vous pouvez lancer `python app.py`)*

2.  **Ouvrez votre navigateur web :**
    Rendez-vous à l'adresse `http://<IP_DE_VOTRE_SERVEUR>:5000`.

3.  **Utilisez l'interface :**
    - Uploadez une image ou un fichier PDF.
    - Choisissez les options d'analyse et de traduction.
    - Lancez le traitement et consultez les résultats.

</details>

---

<details>
<summary>🇯🇵 日本語の説明書</summary>

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

## 使い方

1.  **Flaskアプリケーションを起動します:**
    ```bash
    flask run --host=0.0.0.0
    ```
    *(または `python app.py` を実行)*

2.  **ウェブブラウザを開きます:**
    `http://<サーバーのIPアドレス>:5000` にアクセスしてください。

3.  **インターフェースを使用します:**
    - 画像またはPDFファイルをアップロードします。
    - 希望の分析および翻訳オプションを選択します。
    - 処理を開始し、結果を表示します。

</details>
