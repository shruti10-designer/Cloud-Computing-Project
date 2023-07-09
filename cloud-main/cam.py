import base64
# from flask import Flask, request, render_template
from io import BytesIO
from PIL import Image
import requests

import torch
from PIL import Image
from transformers import SwinForImageClassification
from torchvision.transforms import Compose, Resize, ToTensor, Normalize




def predict(base64_img):  
    # Load the pre-trained model
    model_name = 'Neruoy/swin-finetuned-food101-e3'
    model = SwinForImageClassification.from_pretrained(model_name)

    # Create a preprocessing pipeline
    preprocess = Compose([
        Resize((224, 224)),
        ToTensor(),
        Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])

    # Decode the base64 image string
    img_data = base64.b64decode(base64_img.split(',', 1)[1])

    # Load the image using PIL and convert to RGB format
    image = Image.open(BytesIO(img_data)).convert('RGB')

    # Preprocess image using the preprocessing pipeline
    input_tensor = preprocess(image).unsqueeze(0)

    # Perform inference with the pre-trained model
    outputs = model(input_tensor)

    # Get the predicted class
    predicted_class_idx = torch.argmax(outputs.logits, dim=-1).item()

    # If you want the class name, you can use the model's `id2label` attribute
    predicted_class_name = model.config.id2label[predicted_class_idx]

    return predicted_class_name

def readb64(base64_string):
    print(base64_string)
    img_bytes = base64.b64decode(base64_string.split(',')[1])
    img = Image.open(BytesIO(img_bytes))
    
    img = img.resize((800,800))   
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    resized_bytes = buffer.getvalue()
    return 'data:image/jpeg;base64,' + base64.b64encode(resized_bytes).decode('utf-8')


def get_details(foodname):

    url = "https://dietagram.p.rapidapi.com/apiFood.php"

    querystring = {"name":f"{foodname}","lang":"en"}

    headers = {
        "X-RapidAPI-Key": "6027ba98d4msh071d55914125fddp1e00d4jsn05c1722316ad",
        "X-RapidAPI-Host": "dietagram.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())

    return response.json()