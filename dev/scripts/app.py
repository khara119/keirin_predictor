# dev/scripts/app.py
import argparse
import sys
import train_model
import predict
import triplet_predict
import select_triplet_bets

def run_all():
    print("=== モデル学習 ===")
    train_model.main()

    print("=== 予測処理 ===")
    predict.main()

    print("=== 3連単予想 ===")
    triplet_predict.main()

    print("=== 買い目選定 ===")
    select_triplet_bets.main()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KEIRIN PREDICTOR CLI")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["train", "predict", "triplet_predict", "select", "all"],
        help="実行モード: train / predict / triplet_predict / select / all（省略時は all）"
    )
    args = parser.parse_args()

    mode = args.mode or "all"

    print(f"=== モデル学習モード: {mode} ===", flush=True)

    if mode == "train":
        train_model.main()
    elif mode == "predict":
        predict.main()
    elif mode == "triplet_predict":
        triplet_predict.main()
    elif mode == "select":
        select_triplet_bets.main()
    elif mode == "all":
        run_all()
    else:
        print(f"未知のモード: {mode}", file=sys.stderr)
        sys.exit(1)
