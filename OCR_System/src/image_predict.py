
# coding: utf-8

# In[1]:


import cv2
import numpy as np
import tensorflow as tf

IMAGE_SIZE = 28

def reset_graph(seed=42):
    tf.reset_default_graph()
    tf.set_random_seed(seed)
    np.random.seed(seed)


# In[2]:


def inference(X, keep_prob):
    
    def get_tensor_by_name(name):
        return tf.get_default_graph().get_tensor_by_name(name)
    
    def conv2D(X, W):
        return tf.nn.conv2d(X, W, strides=[1,1,1,1], padding="SAME")
    
    def max_pool(X):
        return tf.nn.max_pool(X, ksize=[1,2,2,1], strides=[1,2,2,1], padding="SAME")
    
    with tf.name_scope("conv1"):
        weight_conv1 = get_tensor_by_name("inference/conv1/weight:0")
        bias_conv1 = get_tensor_by_name("inference/conv1/bias:0")
        h_conv1 = tf.nn.relu(conv2D(X, weight_conv1) + bias_conv1)
        h_pool1 = max_pool(h_conv1)
    
    with tf.name_scope("conv2"):
        weight_conv2 = get_tensor_by_name("inference/conv2/weight:0")
        bias_conv2 = get_tensor_by_name("inference/conv2/bias:0")
        h_conv2 = tf.nn.relu(conv2D(h_pool1, weight_conv2) + bias_conv2)
        h_pool2 = max_pool(h_conv2)
         
    with tf.name_scope("fc1"):
        weight_fc1 = get_tensor_by_name("inference/fc1/weight:0")
        bias_fc1 = get_tensor_by_name("inference/fc1/bias:0")
        h_pool2_flat = tf.reshape(h_pool2,[-1, 7*7*64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, weight_fc1) + bias_fc1)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    
    with tf.name_scope("fc2"): 
        weight_fc2 = get_tensor_by_name("inference/fc2/weight:0")
        bias_fc2 = get_tensor_by_name("inference/fc2/bias:0")
        h_fc2 = tf.matmul(h_fc1_drop, weight_fc2) + bias_fc2
    
    with tf.name_scope("softmax"):
        y_pred = tf.nn.softmax(h_fc2)
        
    return y_pred


# In[3]:


def get_image_array(image_path):
    
    def min_max_normalization(image):
        max_ = image.max()
        min_ = image.min()
        ret = (image - min_)/(max_ - min_)
        return ret.astype(np.float32)
    
    read_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    ret_image = cv2.resize(read_image, (28,28)).reshape((1,28,28,1))
    
    return min_max_normalization(ret_image)


# In[4]:


def main(image_path, pred_type):
    model_path = "model/{}/".format(pred_type)
    if pred_type == "number":
        NUM_CLASS = 10
        convert_array = [i for i in range(10)]
        reset_graph()
        
    elif pred_type == "alphabet":
        NUM_CLASS = 4
        convert_array = ["A", "B", "C", "D"]
        reset_graph()
        
    elif pred_type == "checkbox":
        NUM_CLASS = 2
        convert_array = ["なし", "あり"]
        
    saver = tf.train.import_meta_graph(model_path+"model.ckpt.meta")
    src = get_image_array(image_path)
    
    X = tf.placeholder(dtype=tf.float32, shape=(None, IMAGE_SIZE, IMAGE_SIZE, 1), name="X")
    keep_prob = tf.placeholder(dtype=tf.float32, shape=(None), name="keep_prob")
    logits = inference(X, keep_prob)
    with tf.Session() as sess:
        saver.restore(sess, model_path+"model.ckpt")
        y_pred = logits.eval(feed_dict={X:src, keep_prob:0.5})
        return convert_array[np.argmax(y_pred)]


# In[6]:

if __name__ == '__main__':
    reset_graph()
    print(main("Sandbox/temp/Alphabet_15.jpg", pred_type="alphabet"))

