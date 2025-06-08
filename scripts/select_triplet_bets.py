import pandas as pd
import numpy as np
from pathlib import Path

# --- パス設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "triplet_predictions.csv"
OUTPUT_PATH = BASE_DIR / "data" / "triplet_bets.csv"

# triplet_predictions.csvの読み込み
df = pd.read_csv(INPUT_PATH)

# 出力用リスト
bets = []

# レースIDごとに処理
for race_id, group in df.groupby("レースID"):
    # 確率（%）列がなければ作成
    if "確率（%）" in group.columns:
        prob_col = "確率（%）"
    else:
        raise ValueError("確率列が見つかりません")
    
    # 10%以上
    over10 = group[group[prob_col] >= 10]
    bets.append(over10)
    
    # 10%未満
    under10 = group[group[prob_col] < 10]

    if len(under10) > 0:
        # 重み付きランダムで2点選択（重みは確率）
        weights = under10[prob_col].values
        weights = weights / weights.sum() if weights.sum() > 0 else np.ones_like(weights) / len(weights)
        chosen_idx = np.random.choice(under10.index, size=min(2, len(under10)), replace=False, p=weights)
        bets.append(under10.loc[chosen_idx])        

# 結合して出力
bets_df = pd.concat(bets)
# 指定カラムのみ
output_cols = ["レースID", "1着", "2着", "3着", "スコア", "確率（%）"]
bets_df = bets_df[output_cols]
bets_df.to_csv(OUTPUT_PATH, index=False)

print(f"買い目を {OUTPUT_PATH} に出力しました。")