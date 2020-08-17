#from comet_ml import Experiment

#import IPython.display as ipd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from sklearn import metrics
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import Adam
from keras.utils import to_categorical

with open('orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)


#Lista etsittävistä jutuista:
#lista=["violin", "viola"]
#Uusi dict etsittävistä jutuista:
#uusi={k:orchestra[k] for k in lista if k in orchestra}

features = []
strings = ["violin", "viola", "cello"]
strings_orch={k:orchestra[k] for k in strings if k in orchestra}

woodwinds = ["flute", "bassoon"]
woodwind_orch={k:orchestra[k] for k in woodwinds if k in orchestra}

brass = ["trumpet", "horn"]
brass_orch={k:orchestra[k] for k in brass if k in orchestra}

for ins in strings_orch:
    for notes in strings_orch[ins]["normal"]["mf"]:
        features.append([strings_orch[ins]["normal"]["mf"][notes]["mfcc"], "strings"])

for ins in woodwind_orch:
    for notes in woodwind_orch[ins]["normal"]["mf"]:
        features.append([woodwind_orch[ins]["normal"]["mf"][notes]["mfcc"], "woodwinds"])

for ins in brass_orch:
    for notes in brass_orch[ins]["normal"]["mf"]:
        features.append([brass_orch[ins]["normal"]["mf"][notes]["mfcc"], "brass"])

# Convert into a Panda dataframe
featuresdf = pd.DataFrame(features, columns=['feature','class_label'])

from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
# Convert features and corresponding classification labels into numpy arrays
X = np.array(featuresdf.feature.tolist())
y = np.array(featuresdf.class_label.tolist())

# Encode the classification labels
le = LabelEncoder()
yy = to_categorical(le.fit_transform(y))

# split the dataset
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(X, yy, test_size=0.2, random_state = 127)

num_labels = yy.shape[1]
filter_size = 2

# imput_dim 2 = jos on 2-ulotteinen ominaisuusmatriisi
# model.add(Dense(8, input_dim=2, activation='relu'))

def build_model_graph(input_shape=(40,)):
    model = Sequential()
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_labels))
    model.add(Activation('softmax'))
    # Compile the model
    model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='adam')
    return model

model = build_model_graph()

# Display model architecture summary
#model.summary()
# Calculate pre-training accuracy
score = model.evaluate(x_test, y_test, verbose=0)
accuracy = 100*score[1]

print("Pre-training accuracy: %.4f%%" % accuracy)

from keras.callbacks import ModelCheckpoint
from datetime import datetime
num_epochs = 100
num_batch_size = 32
model.fit(x_train, y_train, batch_size=num_batch_size, epochs=num_epochs, validation_data=(x_test, y_test), verbose=1)

# Evaluating the model on the training and testing set
score = model.evaluate(x_train, y_train, verbose=1)
print("Training Accuracy: {0:.2%}".format(score[1]))

score = model.evaluate(x_test, y_test, verbose=0)
print("Testing Accuracy: {0:.2%}".format(score[1]))

print("Predict:")
samples_to_predict = np.array([orchestra["tenor_trombone"]["normal"]["mf"][45]["mfcc"]])

# Generate predictions for samples
predictions = model.predict(samples_to_predict)
print(predictions)

# Generate arg maxes for predictions
classes = np.argmax(predictions, axis = 1)
print(np.unique(y)[classes])

def predict_instrument_type(samples_to_predict):
    predictions = model.predict(np.array([samples_to_predict]))
    classes = np.argmax(predictions, axis=1)
    print(np.unique(y)[classes])
    return np.unique(y)[classes]

predict_instrument_type(orchestra["tenor_trombone"]["normal"]["mf"][45]["mfcc"])