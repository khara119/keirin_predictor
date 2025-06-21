import os
import sys
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

def main():
    # --- 環境切り替え（環境変数 ENV="stable" or "dev"）---
    ENV = os.getenv("ENV", "dev")

    # --- パス設定 ---
    if getattr(sys, 'frozen', False):
        # 実行ファイル時
        BASE_DIR = Path(sys.executable).parent
        while BASE_DIR.name != "stable":
            BASE_DIR = BASE_DIR.parent
        BASE_DIR = BASE_DIR.parent
        RESOURCE_DIR = Path(sys._MEIPASS) / ENV
    else:
        # 開発環境（スクリプト直実行）
        BASE_DIR = Path(__file__).resolve()
        while BASE_DIR.name != "keirin_predictor":
            BASE_DIR = BASE_DIR.parent
        RESOURCE_DIR = BASE_DIR / ENV

    # --- 書き込み系ディレクトリ設定 ---
    ENV_DIR = BASE_DIR / ENV
    MODEL_DIR = ENV_DIR / "models"
    DATA_DIR = ENV_DIR / "data"

    # 必要に応じて出力先ディレクトリを作成
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # --- ファイルパス指定 ---
    MODEL_PATH = MODEL_DIR / "trained_model.pkl"
    ENCODER_PATH = MODEL_DIR / "category_encoder.pkl"
    INPUT_PATH = RESOURCE_DIR / "data" / "predict_data.csv"
    OUTPUT_PATH = DATA_DIR / "prediction_result.csv"

    # --- 特徴量カラム ---
    FEATURE_COLUMNS = [
        "年", "月", "日", "曜日", "競輪場", "競輪場都道府県", "レース種別"
    ] + [
        f"{i}_{col}" for i in range(1, 8) for col in [
            "選手名", "登録都道府県", "登録地区", "前級班", "現級班", "車番", "期別", "年齢",
            "競走得点", "逃", "捲", "差", "マ", "B", "H", "S",
            "勝率", "2連対率", "3連対率", "前走1", "前走2", "前走3", "今走1", "今走2"
        ]
    ]

    CATEGORICAL_COLUMNS = ["競輪場", "競輪場都道府県", "レース種別"] + [
        f"{i}_{col}" for i in range(1, 8) for col in ["選手名", "登録都道府県", "登録地区"]
    ]

    # --- データ読み込み ---
    df = pd.read_csv(INPUT_PATH)

    # 出力時に必要なカラムを保存
    race_id_col = df["レースID"]
    date_col = df["開催日"]

    # 開催日から年月日・曜日を生成
    df["開催日"] = pd.to_datetime(df["開催日"])
    df["年"] = df["開催日"].dt.year
    df["月"] = df["開催日"].dt.month
    df["日"] = df["開催日"].dt.day
    df["曜日"] = df["開催日"].dt.weekday

    # 「故」をNaNに変換
    df.replace("故", np.nan, inplace=True)

    # --- 級班をランクに変換 ---
    rank_map = {"SS": 1, "S1": 2, "S2": 3, "A1": 4, "A2": 5, "A3": 6, "L1": 7}
    for col in df.columns:
        if "級班" in col:
            df[col] = df[col].map(rank_map)

    target_cols = [col for col in df.columns if any(key in col for key in ["前走", "今走", "着順"])]
    df[target_cols] = df[target_cols].where(df[target_cols] < 4, 4)

    # 結果の着順カラムを削除        
    drop_result_columns = [f"{i}_着順" for i in range(1, 8)]
    df.drop(columns=drop_result_columns, inplace=True)

    # --- 数値変換 ---
    NUMERIC_COLUMNS = list(set(FEATURE_COLUMNS) - set(CATEGORICAL_COLUMNS))
    df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].apply(pd.to_numeric, errors='coerce')

    # --- エンコーダー適用 ---
    with open(ENCODER_PATH, "rb") as f:
        encoder = pickle.load(f)
    df[CATEGORICAL_COLUMNS] = encoder.transform(df[CATEGORICAL_COLUMNS])

    # --- モデル読み込み ---
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)

    model = data["model"]
    expected_features = data["feature_names"]

    # 念のため特徴量に含まれてるかチェック
    missing = set(expected_features) - set(df.columns)
    extra = set(df.columns) - set(expected_features)

    if missing:
        print("⚠️ 予測データに存在しない特徴量:", missing)
    if extra:
        print("ℹ️ 学習時にはなかった特徴量（今回は無視される）:", extra)

    # 特徴量の順番を学習時に合わせる
    df = df[expected_features]

    # --- モデル予測 ---
    probs = model.predict_proba(df)

    # 着確率のカラム名作成
    prob_cols = [f"{i+1}_{j+1}着確率" for i in range(7) for j in range(4)]

    # 着確率カラムを一括で作成
    probs_df = pd.DataFrame(index=df.index)

    for i in range(7):  # 1〜7号車
        for j in range(4):  # 1〜7着
            probs_df[f"{i+1}_{j+1}着確率"] = probs[i][:, j]  # i番車がj+1着になる確率

    # 予想順位
    rank_cols = [f"{i+1}_予想順位" for i in range(7)]
    ranks_df = pd.DataFrame(index=df.index)

    for i in range(7):
        ranks_df[f"{i+1}_予想順位"] = probs[i].argmax(axis=1) + 1

    # 一括結合
    df = pd.concat([df, probs_df, ranks_df], axis=1)

    # --- カテゴリを元の文字列に戻す（予測後にやるのが正解）---
    decoded_df = pd.DataFrame(
        encoder.inverse_transform(df[CATEGORICAL_COLUMNS]),
        columns=CATEGORICAL_COLUMNS
    )
    df[CATEGORICAL_COLUMNS] = decoded_df.fillna("初学習")

    # --- 級班を元の文字列に戻す ---
    reverse_rank_map = {v: k for k, v in rank_map.items()}
    for col in df.columns:
        if "級班" in col:
            df[col] = df[col].map(reverse_rank_map).fillna("不明")

    # --- 出力に不要なカラムを削除 ---
    df.drop(columns=["年", "月", "日", "曜日"], inplace=True)

    # --- レースIDと開催日を最初に戻す ---
    df.reset_index(drop=True, inplace=True)
    df.insert(0, "開催日", date_col.reset_index(drop=True))
    df.insert(0, "レースID", race_id_col.reset_index(drop=True))

    # --- 結果保存 ---
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ 予測スコア＋予想順位を含めて {OUTPUT_PATH} に保存したよ！")

if __name__ == "__main__":
    main()