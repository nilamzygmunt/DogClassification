#TechVidvan load all required libraries
import cv2
import numpy as np 
import pandas as pd 
from tensorflow.keras.models import load_model,Model
from tensorflow.keras.applications.resnet_v2 import preprocess_input

class Classificator:


    def __init__(self):
        self.im_size = 224
        self.num_breeds = 60
        self.batch_size = 64

    def loadBreeds(self, csv_path):
        df_labels = pd.read_csv(csv_path)
        breed_dict = list(df_labels['breed'].value_counts().keys()) 
        self.new_list = sorted(breed_dict,reverse=True)[:self.num_breeds*2+1:2]

    def loadModel(self, model_path):
        self.model = Model()
        self.model = load_model(model_path)

    def predictBreed(self, pred_img_path):
        pred_img_array = cv2.resize(cv2.imread(pred_img_path,cv2.IMREAD_COLOR),((self.im_size,self.im_size)))
        pred_img_array = preprocess_input(np.expand_dims(np.array(pred_img_array[...,::-1].astype(np.float32)).copy(), axis=0))
        pred_val = self.model.predict(np.array(pred_img_array,dtype="float32"))
        pred_breed = sorted(self.new_list)[np.argmax(pred_val)]
        pred_breed = pred_breed.replace("_", " ")
        return pred_breed


