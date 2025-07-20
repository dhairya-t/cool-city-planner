import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, Activation, MaxPool2D, Conv2DTranspose, Concatenate, ZeroPadding2D, Dropout
from tensorflow.keras.applications import InceptionResNetV2

# Re-define the dice_coef function since it's a custom metric
def dice_coef(y_true, y_pred):
    return (2. * K.sum(y_true * y_pred) + 1.) / (K.sum(y_true) + K.sum(y_pred) + 1.)

# Re-define the build_inception_resnetv2_unet function
def conv_block(input, num_filters):
    x = Conv2D(num_filters, 3, padding="same")(input)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Conv2D(num_filters, 3, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    return x
def decoder_block(input, skip_features, num_filters):
    x = Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input)
    x = Concatenate()([x, skip_features])
    x = conv_block(x, num_filters)
    return x
def build_inception_resnetv2_unet(input_shape):
    inputs = Input(input_shape)
    encoder = InceptionResNetV2(include_top=False, weights="imagenet", input_tensor=inputs)
    s1 = encoder.get_layer("input_layer").output
    s2 = encoder.get_layer("activation").output
    s2 = ZeroPadding2D(((1, 0), (1, 0)))(s2)
    s3 = encoder.get_layer("activation_3").output
    s3 = ZeroPadding2D((1, 1))(s3)
    s4 = encoder.get_layer("activation_74").output
    s4 = ZeroPadding2D(((2, 1),(2, 1)))(s4)
    b1 = encoder.get_layer("activation_161").output
    b1 = ZeroPadding2D((1, 1))(b1)
    d1 = decoder_block(b1, s4, 512)
    d2 = decoder_block(d1, s3, 256)
    d3 = decoder_block(d2, s2, 128)
    d4 = decoder_block(d3, s1, 64)
    dropout = Dropout(0.3)(d4)
    outputs = Conv2D(6, 1, padding="same", activation="softmax")(dropout)
    model = Model(inputs, outputs, name="InceptionResNetV2-UNet")
    return model

model = build_inception_resnetv2_unet((512, 512, 3))

model.load_weights('InceptionResNetV2-UNet.h5')
