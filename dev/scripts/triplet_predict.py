import os
import sys
import pandas as pd
import itertools
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
    else:
        # 開発環境（スクリプト直実行）
        BASE_DIR = Path(__file__).resolve()
        while BASE_DIR.name != "keirin_predictor":
            BASE_DIR = BASE_DIR.parent

    # --- 書き込み系ディレクトリ設定 ---
    ENV_DIR = BASE_DIR / ENV
    DATA_DIR = ENV_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # --- ファイルパス指定 ---
    INPUT_PATH = DATA_DIR / "prediction_result.csv"
    OUTPUT_PATH = DATA_DIR / "triplet_predictions.csv"

    # --- データ読み込み ---
    df = pd.read_csv(INPUT_PATH)

    # 出力用リスト
    all_predictions = []

    # レースごとに処理
    for _, row in df.iterrows():
        race_id = row["レースID"]
        
        triplet_data = []

        # 車番と順位を取り出す
        horses = []
        for i in range(1, 8):
            horses.append({
                "車番": i,
                "1着確率": row[f"{i}_1着確率"],
                "2着確率": row[f"{i}_2着確率"],
                "3着確率": row[f"{i}_3着確率"],
            })
            
        for a, b, c in itertools.permutations(horses, 3):
            score = a["1着確率"] * b["2着確率"] * c["3着確率"]
            
            triplet_data.append({
                "レースID": race_id,
                "1着": a["車番"],
                "2着": b["車番"],
                "3着": c["車番"],
                "スコア": score
            })

        triplet_df = pd.DataFrame(triplet_data)

        # スコアを正規化して確率に
        score_sum = triplet_df["スコア"].sum()
        triplet_df["確率（%）"] = (triplet_df["スコア"] / score_sum * 100).round(2)

        all_predictions.append(triplet_df)

    # 全レース分を結合
    result_df = pd.concat(all_predictions, ignore_index=True)

    # スコア降順、レースID昇順で並べる
    result_df = result_df.sort_values(by=["レースID", "スコア"], ascending=[True, False])

    # 保存
    result_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ 3連単予測（予想順位ベース）を {OUTPUT_PATH} に保存したよ！")

if __name__ == "__main__":
    main()