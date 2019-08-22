import numpy as np
import tensorflow as tf

from PIL import Image


DIV2K_RGB_MEAN = np.array([0.4488, 0.4371, 0.4040]) * 255


# ---------------------------------------
#  Normalization
# ---------------------------------------


def normalize(x, rgb_mean=DIV2K_RGB_MEAN):
    return (x - rgb_mean) / 127.5


def denormalize(x, rgb_mean=DIV2K_RGB_MEAN):
    return x * 127.5 + rgb_mean


def normalize_01(x):
    """Normalizes RGB images to [0, 1]."""
    return x / 255.0


def normalize_m11(x):
    """Normalizes RGB images to [-1, 1]."""
    return x / 127.5 - 1


def denormalize_m11(x):
    """Inverts normalization_m11."""
    return (x + 1) * 127.5


# ---------------------------------------
#  Metrics
# ---------------------------------------


def psnr(x1, x2):
    return tf.image.psnr(x1, x2, max_val=255)


# ---------------------------------------
#  See https://arxiv.org/abs/1609.05158
# ---------------------------------------


def subpixel_conv2d(scale):
    return lambda x: tf.nn.depth_to_space(x, scale)


# ---------------------------------------
#  Model
# ---------------------------------------


def resolve_single(model, lr):
    return resolve(model, np.expand_dims(lr, axis=0))[0]


def resolve(model, lr_batch):
    sr_batch = model.predict(lr_batch)
    sr_batch = np.clip(sr_batch, 0, 255)
    sr_batch = np.round(sr_batch)
    sr_batch = sr_batch.astype(np.uint8)
    return tf.constant(sr_batch)


def evaluate(model, ds):
    psnr_values = []
    for lr, hr in ds:
        sr = resolve(model, lr)
        psnr_value = psnr(hr, sr)[0]
        psnr_values.append(psnr_value)
    return tf.reduce_mean(psnr_values)