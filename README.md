# OCR Global Alert Tool - 開発者・ユーザーガイド

## 1. 環境構築

### Windows (推奨)
1. Python (3.8以上) をインストール。
2. ライブラリのインストール：
   ```bash
   pip install -r requirements.txt
   ```

### Mac (開発・テスト用)
Macで実行するには `tesseract` と `python-tk` (GUI用) が必要です。Homebrewを使ってインストールしてください。

```bash
# 1. 必要なツールのインストール
brew install tesseract
brew install python-tk

# 2. ライブラリのインストール
pip install -r requirements.txt
```

## 2. 動作確認 (スクリプト実行)

PCにTesseractがインストールされていれば、以下のコマンドで起動します。

```bash
python3 main.py
```
- **メモ**: Macの場合、初回起動時に「カメラへのアクセス」許可を求められる場合があります。許可してください。
- エラーが出る場合、`monitor.py` 内の `pytesseract.pytesseract.tesseract_cmd` をご自身の環境に合わせて書き換えてください（通常は自動検出されます）。

## 3. 配布用ビルドの作成

このツールは `PyInstaller` を使って、単体で動作する実行ファイル（exe/app）に変換できます。

### Windowsの場合 (exe化)
Windowsで実行できる `.exe` を作るには、Tesseract本体をプロジェクト内にバンドルする必要があります。

1. **Tesseractの準備**
   - [UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) から Windows 64-bit版をインストールします。
   - インストール先（例: `C:\Program Files\Tesseract-OCR`）の中身をすべてコピーします。
   - このプロジェクトのルートに `tesseract` というフォルダを作り、その中に貼り付けます。
     - 配置確認: `ocr_alert_tool/tesseract/tesseract.exe` がある状態。

2. **ビルド実行**
   ```bash
   python build.py
   ```
   - 成功すると `dist` フォルダに `OCRAlertTool.exe` が生成されます。
   - これを他のPCにコピーするだけで動作します。

### Macの場合 (Unix実行ファイル/app化)
Macで配布する場合、通常は `.app` 形式にしますが、簡易的には実行バイナリとして配布できます。

1. **ビルド実行**
   ```bash
   # build.py はWindows用に特化しているため、直接コマンドを叩きます
   pyinstaller --noconsole --onefile --name=OCRAlertTool main.py
   ```
2. **実行ファイルの確認**
   - `dist` フォルダに `OCRAlertTool` というファイルができます。
   - これを実行（ダブルクリックまたはターミナルから）すれば動きます。
   - **注意**: 配布先のMacにも `brew install tesseract` でTesseractが入っている必要があります（バンドルする場合、Mac用のバイナリを `tesseract` フォルダに入れて `python build.py` を改造する必要があります）。
