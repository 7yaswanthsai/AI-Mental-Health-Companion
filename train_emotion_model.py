import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
import pickle
import os

# 1. Load and merge CSVs
data_files = ["data/goemotions_1.csv", "data/goemotions_2.csv", "data/goemotions_3.csv"]
dfs = [pd.read_csv(f) for f in data_files]
data = pd.concat(dfs, ignore_index=True)

# 2. Identify emotion columns
emotion_cols = data.columns.tolist()
start_idx = emotion_cols.index('admiration')  # first emotion column
emotion_cols = emotion_cols[start_idx:]

# 3. Keep text + emotion columns, drop missing text
data = data[['text'] + emotion_cols].dropna(subset=['text'])

# 4. Tokenize text
tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
tokenizer.fit_on_texts(data['text'])
sequences = tokenizer.texts_to_sequences(data['text'])
padded_sequences = pad_sequences(sequences, maxlen=50, padding='post', truncating='post')

# 5. Prepare labels using MultiLabelBinarizer
labels_array = data[emotion_cols].values
mlb = MultiLabelBinarizer()
mlb.fit([emotion_cols])  # fit on all emotion names (multi-label)

# 6. Train/test split
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels_array, test_size=0.1, random_state=42)

# 7. Build LSTM model
model = Sequential([
    Embedding(input_dim=10000, output_dim=128, input_length=50),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(labels_array.shape[1], activation='sigmoid')  # multi-label
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# 8. Train model (2 epochs for demo)
model.fit(X_train, y_train, epochs=2, batch_size=32, validation_split=0.1)

# 9. Evaluate model
loss, acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {acc:.4f}")

# 10. Save model, tokenizer, and mlb
os.makedirs("models", exist_ok=True)
model.save("models/emotion_lstm_model.h5")
with open("models/tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
with open("models/mlb.pkl", "wb") as f:
    pickle.dump(mlb, f)

print("Model, tokenizer, and mlb saved successfully!")
