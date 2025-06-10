import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier

# --- パス設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
TRAIN_CSV_PATH = BASE_DIR / "data" / "train_data.csv"
MODEL_PATH = BASE_DIR / "models" / "trained_model.pkl"
ENCODER_PATH = BASE_DIR / "models" / "category_encoder.pkl"

# --- データ読み込み ---
df = pd.read_csv(TRAIN_CSV_PATH)
df["開催日"] = pd.to_datetime(df["開催日"])
df["年"] = df["開催日"].dt.year
df["月"] = df["開催日"].dt.month
df["日"] = df["開催日"].dt.day
df["曜日"] = df["開催日"].dt.weekday

# --- カテゴリ変数の抽出 ---
categorical_cols = [col for col in df.columns if any(key in col for key in ["競輪場", "選手名", "出身"])]

# --- エンコード ---
encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
df[categorical_cols] = encoder.fit_transform(df[categorical_cols])

# --- 級班のマッピング ---
rank_map = {
    "SS": 1,
    "S1": 2,
    "S2": 3,
    "A1": 4,
    "A2": 5,
    "A3": 6,
    "L1": 7,
}
for col in df.columns:
    if "級班" in col:
        df[col] = df[col].map(rank_map)

# --- 数値変換 ---
for col in df.columns:
    if any(key in col for key in ["得点", "前走", "今走", "年齢", "年", "月", "日", "曜日", "着順"]):
        df[col] = pd.to_numeric(df[col], errors="coerce")

target_cols = [col for col in df.columns if any(key in col for key in ["前走", "今走", "着順"])]
df[target_cols] = df[target_cols].where(df[target_cols] < 4, 4)
        
# --- 特徴量と目的変数の分離 ---
target_cols = [f"{i}_着順" for i in range(1, 8)]
drop_cols = target_cols + ["レースID", "開催日"]
X = df.drop(columns=drop_cols)
y = df[target_cols] - 1

# --- データ分割 ---
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- モデル構築 ---
base_clf = XGBClassifier(
    objective='multi:softprob',
    num_class=7,
    eval_metric='mlogloss',
    random_state=42
)

# --- モデル学習 ---
model = MultiOutputClassifier(base_clf)
model.fit(X_train, y_train)

# --- モデル保存 ---
with open(MODEL_PATH, "wb") as f:
    pickle.dump({
        "model": model,
        "feature_names": X_train.columns.tolist(),
    }, f)

# --- エンコーダ保存 ---
with open(ENCODER_PATH, "wb") as f:
    pickle.dump(encoder, f)    

print("✅ マルチターゲット分類モデルの学習と保存が完了しました！")
