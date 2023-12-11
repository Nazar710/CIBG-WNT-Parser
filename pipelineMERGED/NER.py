import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

# Load data from CSV
df = pd.read_csv('CSV/names.csv', encoding='latin1')

# Assuming your CSV has columns 'Name' and 'Label'
texts = df['Name'].tolist()
labels = df['Label'].values

# Tokenize the text
tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)

# Convert text to sequences
sequences = tokenizer.texts_to_sequences(texts)

# Pad sequences to a fixed length
max_length = max(len(seq) for seq in sequences)
padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')

# Vocabulary size
vocab_size = len(tokenizer.word_index) + 1

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)


# Build the model
embedding_dim = 8
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length))
model.add(LSTM(units=100))
model.add(Dense(units=1, activation='sigmoid'))

# Compile the model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=1, validation_data=(X_test, y_test))

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Accuracy: {accuracy * 100:.2f}%')

# Inference
new_names = ["Mark", "Jane", "Bezoldiging","A.F.Z Max van Der","Dhr S.Z Ali","S.Z.","A.B.C","A. Bezoldiging.","A. Maastricht"]
new_sequences = tokenizer.texts_to_sequences(new_names)
new_padded_sequences = pad_sequences(new_sequences, maxlen=max_length, padding='post')

predictions = model.predict(new_padded_sequences)
for i, name in enumerate(new_names):
    print(f'Name: {name}, Probability of being a name: {predictions[i][0]:.4f}')

# Save the trained model
model.save('name_detection_model.h5')

# Optionally, save the tokenizer for later use
import pickle

with open('tokenizer.pkl', 'wb') as tokenizer_file:
    pickle.dump(tokenizer, tokenizer_file)
