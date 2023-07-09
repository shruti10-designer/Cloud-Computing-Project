
import numpy as np
import pickle
import pandas as pd
import os



def predict(data):
  
    pickle_in = open(f"{os.path.join(os.getcwd(),'ml_model','classifier.pkl')}","rb")
    classifier = pickle.load(pickle_in)
  
    step_count = data['step_count']
    calories_burnt = data['calories_burnt']
    hours_of_sleep = data['hours_of_sleep']
    Weight = data['Weight']
    Height = data['Height']
    calories = data['calories']
    BMI = data['BMI']
    prediction=classifier.predict([[	step_count,	calories_burnt,	hours_of_sleep,	Weight,	Height,	calories,	BMI]])
    
    print(prediction)
    
    pickle_in.close()
    
    return prediction
