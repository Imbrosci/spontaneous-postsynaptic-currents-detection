# -*- coding: utf-8 -*-
"""Created on Mon Mar 14 14:32:02 2022.

@author: barbara
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
tf.config.list_physical_devices('GPU')
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D, Flatten,
                                     Dense, Dropout)
from tensorflow.keras.models import Model


class ModelBase:
    """Estimate the probability of the input.

    This deep learning model takes 300 dp long vector and outputs a vector of
    the same length with values between 0 and 1.
    """

    def __init__(self, input_shape=(300, 1)):
        self.input_shape = input_shape
        i = Input(shape=self.input_shape)
        x = Conv1D(32, 15, padding='same', activation='relu')(i)
        x = MaxPooling1D(2)(x)
        x = Conv1D(64, 15, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Conv1D(128, 15, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Conv1D(256, 15, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.35)(x)
        x = Dense(300, activation='sigmoid')(x)

        self.model = Model(i, x)


class ModelRefinement:
    """Check if the events detected by ModelBase are true or false positives.

    This deep learning model takes 300 dp long vector and outputs the
    probability of the input vector to contain a true event in the middle.
    """

    def __init__(self, input_shape=(300, 1)):
        self.input_shape = input_shape
        i = Input(shape=self.input_shape)
        x = Conv1D(64, 7, padding='same', activation='relu')(i)
        x = MaxPooling1D(3)(x)
        x = Conv1D(128, 7, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Conv1D(256, 7, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Conv1D(512, 7, padding='same', activation='relu')(x)
        x = MaxPooling1D(2)(x)
        x = Flatten()(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Dense(16, activation='relu')(x)
        x = Dense(1, activation='sigmoid')(x)

        self.model = Model(i, x)
