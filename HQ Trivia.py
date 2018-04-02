from PIL import Image
import pytesseract
import requests
from bs4 import BeautifulSoup
import cv2
from mss import mss
import os
import operator
import numpy as np

os.system('clear')

def getRequestFromFile(filename):
    img = cv2.imread(filename,0)

    text = pytesseract.image_to_string(img)
    text = text.strip()

    text_split = text.split('?')

    if(len(text_split) > 1):
        question = text_split[0].replace('\n', ' ')
        list_answer = [x.strip() for x in ' '.join(text_split[1:]).split('\n') if len(x)]

        list_req = []

        for a in list_answer:
            list_req.append({'q': question,'a': a})
        
        return list_req

    return []

def getRequestFromCamera():
    camera = cv2.VideoCapture(0)
    question = ""
    list_answer = [] 

    while True:
        return_value, img = camera.read()
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cv2.imshow('Camera', img)

        text = pytesseract.image_to_string(img)
        text = text.strip()

        text_split = text.split('?')

        if(len(text_split) > 1):
            question = text_split[0].replace('\n', ' ')
            list_answer = [x.strip() for x in ' '.join(text_split[1:]).split('\n') if len(x)]

            print('q:', question)
            print('a', list_answer)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or len(list_answer) == 3:
            break

    camera.release()
    cv2.destroyAllWindows()

    list_req = []

    for a in list_answer:
        list_req.append({'q': question,'a': a})
    
    return list_req

def getRequestFromPhone():
    monitor = {'top': 100, 'left': 0, 'width': 395, 'height': 500}
    sct = mss()
    cv2.namedWindow("Phone", cv2.WINDOW_NORMAL)

    question = ""
    list_answer = [] 

    while True:
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cv2.imshow('Phone', img)

        text = pytesseract.image_to_string(img)
        text = text.strip()

        text_split = text.split('?')

        if(len(text_split) > 1):
            question = text_split[0].replace('\n', ' ')
            list_answer = [x.strip() for x in ' '.join(text_split[1:]).split('\n') if len(x)]

            print('q:', question)
            print('a', list_answer)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or len(list_answer) == 3:
            break

    cv2.destroyAllWindows()

    list_req = []

    for a in list_answer:
        list_req.append({'q': question,'a': a})
    
    return list_req

def getRequestFromInput(question, list_answer):
    return [{
        'q': question,
        'a': a}
        for a in list_answer]

def getNbResults(q):
    r = requests.get('http://www.google.com/search', params={'q':q})

    soup = BeautifulSoup(r.text, "html.parser")
    strResult = soup.find('div',{'id':'resultStats'}).text
    result = int(''.join([x for x in strResult if x.isdigit()]))

    print(q, '->', result)
    return result

def getAnswerFromRequest(list_request, order='AQ'):
    stats = {}

    for req in list_req:
        if(order == 'AQ'):
            q = req['a'] + ' ' + req['q']

        elif(order == 'QA'):
            q = req['q'] + ' ' + req['a']

        stats[req['a']] = getNbResults(q)

    total = sum(stats.values())

    for a,s in stats.items():
        stats[a] = round(s / total, 2)

    answer = max(stats.items(), key=operator.itemgetter(1))

    print('Stats :', stats, '\n')
    print('Answer :', answer, '\n')


#list_req = getRequestFromPhone()
list_req = getRequestFromInput('What is the capital of Spain', ['Paris', 'Madrid', 'New York'])

if len(list_req):
    getAnswerFromRequest(list_req)
