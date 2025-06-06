import pandas as pd
import itertools
from pathlib import Path

# --- パス設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "prediction_result.csv"
OUTPUT_PATH = BASE_DIR / "data" / "triplet_predictions.csv"

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
