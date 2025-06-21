import os
import sys
import pandas as pd
import numpy as np
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
    INPUT_PATH = DATA_DIR / "triplet_predictions.csv"
    OUTPUT_PATH = DATA_DIR / "triplet_bets.csv"

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
    
if __name__ == "__main__":
    main()