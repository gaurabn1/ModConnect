import cv2
from PIL import Image
from django.conf import settings
import opennsfw2 as n2
from io import BytesIO
import numpy as np
import os




def censor_text(text):

    tokens = text.split()
    censored_tokens = []
    
    bad_words_file = os.path.join(settings.BASE_DIR, 'bad_words_updated.txt')
    
    try:
        with open(bad_words_file, 'r', encoding='utf-8') as file:
            bad_words = {word.lower() for word in file.read().splitlines()} 
    except FileNotFoundError:
        print(f'Error: File "{bad_words_file}" not found')
        return text
    except IOError as e:
        print(f"Error: an I/O error occurred while reading: {e}")
        return text
    except UnicodeDecodeError:
        print(f"Error: Unable to decode the file: {e}")
        return text
    
    for token in tokens:
        if token.lower() in bad_words:
            censored_tokens.append(len(token) * '*')
        else:
            censored_tokens.append(token)

    censored_text =' '.join(censored_tokens)

    return censored_text




























# def profanity_censor(text):
#     return profanity.censor(text)
    

 

def is_nsfw(image_array):

    img_pil = Image.fromarray(image_array)
    print("image pil: " ,img_pil)
    buffer = BytesIO()
    img_pil.save(buffer, format='JPEG')
    buffer.seek(0)

    predictions = n2.predict_images([buffer])
    # print("Predictions:", predictions)
    
    if isinstance(predictions, (list, np.ndarray)):
        if isinstance(predictions[0], (list, np.ndarray)):
            score = predictions[0][0]
        else:
            score = predictions[0]
    elif isinstance(predictions, float):
        score = predictions
    else:
        raise TypeError("Unsupported prediction format")
    return score > 0.05

def blur_image(image_array):
    ksize = (301, 301) 
    sigmaX = 0
    return cv2.GaussianBlur(image_array, ksize, sigmaX)

