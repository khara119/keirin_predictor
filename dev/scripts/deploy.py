# deploy.py
import os
import sys
import shutil
import subprocess
import zipapp
from pathlib import Path

def deploy_and_build_pyz():
    if getattr(sys, 'frozen', False):
        # PyInstaller実行ファイルの場合
        BASE_DIR = Path(sys._MEIPASS)
    else:
        # 通常のPythonスクリプト実行時
        BASE_DIR = Path(__file__).resolve()
        while BASE_DIR.name != "keirin_predictor":
            BASE_DIR = BASE_DIR.parent

    dev = BASE_DIR / "dev"
    stable = BASE_DIR / "stable"
    
    bin = stable / "bin"
    exe = bin / "keirin_app"
    
    # 実行ファイルを削除
    if os.path.exists(exe):
        os.remove(exe)
        print(f"{exe} を削除しました。")
    else:
        print(f"{exe} は存在しません。")
        
    # モデルを削除
    model_dir = stable / "models"
    if model_dir.exists() and model_dir.is_dir():
        for file in model_dir.glob("*"):
            if file.is_file():
                os.remove(file)
                print(f"{file} を削除しました。")
            elif file.is_dir():
                shutil.rmtree(file)
                print(f"{file} ディレクトリを削除しました。")
    else:
        print(f"{model_dir} は存在しません。")
        
    # スクリプトを削除
    scripts_dir = stable / "scripts"
    if scripts_dir.exists() and scripts_dir.is_dir():
        for file in scripts_dir.glob("*"):
            if file.is_file():
                os.remove(file)
                print(f"{file} を削除しました。")
            elif file.is_dir():
                shutil.rmtree(file)
                print(f"{file} ディレクトリを削除しました。")
    else:
        print(f"{scripts_dir} は存在しません。")

    # --- コピー先を作成 ---
    (stable / "config").mkdir(parents=True, exist_ok=True)
    (stable / "scripts").mkdir(parents=True, exist_ok=True)
    
    # --- 実行先を作成 ---
    bin.mkdir(parents=True, exist_ok=True)
    
    # --- スクリプト のコピー ---
    for file in ["app.py", "train_model.py", "predict.py", "select_triplet_bets.py", "triplet_predict.py"]:
        shutil.copy(dev / "scripts" / file, stable / "scripts" / file)

    xgboost_dir = BASE_DIR / "venv/lib/python3.12/site-packages/xgboost"

    # PyInstallerコマンド
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "keirin_app",
        "--distpath", str(bin),
        "--add-binary", f"{(xgboost_dir / 'lib/libxgboost.dylib').resolve()}:xgboost/lib",
        "--add-data", f"{(xgboost_dir / 'VERSION').resolve()}:xgboost",
        "--add-data", "stable/data:stable/data",
        "--runtime-hook", str(stable / "config" / "set_env_hook.py"),
        str(stable / "scripts" / "app.py")
    ]

    # 実行
    print("🔧 PyInstaller でビルド開始...")
    subprocess.run(cmd, check=True)
    print(f"✅ ビルド完了！→ {exe}")

if __name__ == "__main__":
    deploy_and_build_pyz()
