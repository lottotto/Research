#/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import tensorflow as tf
import cv2
import tensorflow.python.platform
import os
# from types import *
# import Space_test

NUM_CLASSES = 10
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*1

# flags = tf.app.flags
# FLAGS = flags.FLAGS
# flags.DEFINE_string('N_readmodels', os.path.abspath('./TrainningResource/Number/Number_model/model.ckpt'), 'File name of model data')

def inference(images_placeholder, keep_prob):

    def weight_variable(shape):
      initial = tf.truncated_normal(shape, stddev=0.1)
      return tf.Variable(initial)

    def bias_variable(shape):
      initial = tf.constant(0.1, shape=shape)
      return tf.Variable(initial)

    def conv2d(x, W):
      return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
      return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                            strides=[1, 2, 2, 1], padding='SAME')

    x_images = tf.reshape(images_placeholder, [-1, IMAGE_SIZE, IMAGE_SIZE, 1])

    with tf.name_scope('N_conv1') as scope:
        W_conv1 = weight_variable([5, 5, 1, 32])
        b_conv1 = bias_variable([32])
        h_conv1 = tf.nn.relu(conv2d(x_images, W_conv1) + b_conv1)

    with tf.name_scope('N_pool1') as scope:
        h_pool1 = max_pool_2x2(h_conv1)

    with tf.name_scope('N_conv2') as scope:
        W_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

    with tf.name_scope('N_pool2') as scope:
        h_pool2 = max_pool_2x2(h_conv2)

    with tf.name_scope('N_fc1') as scope:
        W_fc1 = weight_variable([7*7*64, 1024])
        b_fc1 = bias_variable([1024])
        h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    with tf.name_scope('N_fc2') as scope:
        W_fc2 = weight_variable([1024, NUM_CLASSES])
        b_fc2 = bias_variable([NUM_CLASSES])

    with tf.name_scope('N_softmax') as scope:
        y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
    return y_conv

def loss(logits, labels):
    cross_entropy = -tf.reduce_sum(labels*tf.log(tf.clip_by_value(logits,1e-10,1.0)))
    tf.summary.scalar("cross_entropy", cross_entropy)
    return cross_entropy

def training(loss, learning_rate):
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    return train_step

def accuracy(logits, labels):
    correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    tf.summary.scalar("accuracy", accuracy)
    return accuracy

def get_particular_variables(name):
    return {v.name: v for v in tf.global_variables() if v.name.find(name) >= 0}

def detect_space(Image):
    Image = Image[7:23, 7:23]
    temp_Image = cv2.threshold(Image,135,255,cv2.THRESH_BINARY)[1]
    if np.count_nonzero(temp_Image)/temp_Image.size > 0.98:
        return True
    else:
        return False

def main(ImagePath):
    images_placeholder = tf.placeholder("float", shape=(None, IMAGE_PIXELS))
    labels_placeholder = tf.placeholder("float", shape=(None, NUM_CLASSES))
    keep_prob = tf.placeholder("float")
    logits = inference(images_placeholder, keep_prob)
    sess = tf.InteractiveSession()
    Dict = get_particular_variables('N')
    saver = tf.train.Saver(Dict)
    sess.run(tf.global_variables_initializer())
    saver.restore(sess,os.path.abspath('./TrainningResource/Number/Number_model/model.ckpt'))
    ret =[]
    img = cv2.imread(ImagePath, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img,(IMAGE_SIZE, IMAGE_SIZE))
    #ノイズ取り
    dst = cv2.threshold(img,230,100,cv2.THRESH_TOZERO_INV)[1]
    for i in range(len(dst)):
        for j in range(len(dst[i])):
            if dst[i][j] == 0:
                dst[i][j] = 255
    #ここまで、次は正規化
    Max = dst.max()
    Min = dst.min()
    dst = (dst-Min)/(Max-Min)

    if detect_space(dst):
        ret.append('-')
    else:
        img = dst.flatten().astype(np.float32)
        pr = logits.eval(feed_dict={images_placeholder: [img], keep_prob: 1.0 })[0]
        # print(pr)
        ret.append(np.argmax(pr))
    sess.close()
    tf.reset_default_graph()
    return ret[0]

if __name__ == '__main__':
    print(main(sys.argv[1]))
