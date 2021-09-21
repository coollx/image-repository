import os
import tensorflow_hub as hub
import cv2
import numpy
import pandas as pd
import tensorflow as tf
#prevent tensorflow from throwing warning information
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner
    
@singleton
class Detector(object):
    def __init__(self, labels = 'labels.csv'):
        print('constructing indexing...please wait')
        #self.model = hub.load("https://hub.tensorflow.google.cn/tensorflow/efficientdet/lite2/detection/1")
        self.model = hub.load(os.path.abspath('.')+r'\pretrained')        
        self.labels = pd.read_csv(labels, sep=';', index_col='ID')
        self.labels = self.labels['OBJECT (2017 REL.)']
        print('indexing complete')

    def get_tags(self, img):
        width = 1028
        height = 1028
        
        #Resize to respect the input_shape
        inp = cv2.resize(img, (width , height ))
        #Convert img to RGB
        rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
        # COnverting to uint8
        rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)
        #Add dims to rgb_tensor
        rgb_tensor = tf.expand_dims(rgb_tensor , 0)
        #predict use pretrained model
        boxes, scores, classes, num_detections = self.model(rgb_tensor)
        #get tags and socres in image
        pred_labels = classes.numpy().astype('int')[0] 
        pred_labels = [self.labels[i] for i in pred_labels]
        pred_scores = scores.numpy()[0]

        nothing_detected = True
        tags = []

        #remove all tags with prob lower than .5
        for score, label in zip(pred_scores, pred_labels):
            if score < 0.5:
                continue

            tags.append(label)
            nothing_detected = False
    
        if not tags:
            print('nothing detected!')
        return tags