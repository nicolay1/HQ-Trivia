from PIL import Image
import pytesseract
import cv2
from mss import mss

import requests
import wikipedia
from bs4 import BeautifulSoup

import os
import prompt
import operator
import numpy as np
import time

import nltk
from nltk.corpus import stopwords
sw = set(stopwords.words('english'))

from Wikipedia import *

def getRequestsFromInput(question, list_answer, format=False):
    if(format):
        question = formatQuestion(question)

    return [{
        'q': question,
        'a': a}
        for a in list_answer]

def getRequestFromFile(filename):
    img = cv2.imread(filename,0)

    text = pytesseract.image_to_string(img)
    text = text.strip()

    text_split = text.split('?')

    if(len(text_split) > 1):
        question = text_split[0].replace('\n', ' ')
        list_answer = [x.strip() for x in ' '.join(text_split[1:]).split('\n') if len(x)]

        return getRequestsFromInput(question, list_answer)

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

        if (cv2.waitKey(1) & 0xFF == ord('q')) or len(list_answer) == 3:
            break

    camera.release()
    cv2.destroyAllWindows()
    return getRequestsFromInput(question, list_answer)

def getRequestFromPhone():
    monitor = {'top': 150, 'left': 0, 'width': 395, 'height': 450}
    sct = mss()
    cv2.namedWindow("Phone", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Phone", 500, 500);

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

        if (cv2.waitKey(1) & 0xFF == ord('q')) or len(list_answer) == 3:
            break

    cv2.destroyAllWindows()
    return getRequestsFromInput(question, list_answer)

def formatQuestion(question):
    return ' '.join([x for x in question.lower().split() if x not in sw])

def getResults_Google(q):
    r = requests.get('http://www.google.com/search', params={'q':q})

    soup = BeautifulSoup(r.text, "html.parser")

    strResult = soup.find('div',{'id':'resultStats'}).text
    result = int(''.join([x for x in strResult if x.isdigit()]))

    return result

def getStats_Google(list_req, order='AQ'):
    stats = {}

    for n,req in enumerate(list_req):
        if(order == 'AQ'):
            q = req['a'] + ' ' + req['q']

        elif(order == 'QA'):
            q = req['q'] + ' ' + req['a']

        stats[n+1] = getResults_Google(q)

    total = sum(stats.values())

    for n,s in stats.items():
        stats[n] = round(s / total, 2)

    return stats

def getResults_Wikipedia(list_req):
    question = list_req[0]['q']
    list_answer = []

    for e in list_req:
        list_answer.append(e['a'])

    wiki_threads = []
    
    for subject in formatQuestion(question).split():
        list_answer.append(subject)

    for answer in list_answer:
        wiki_threads.append(Wikipedia(question, answer))

    print(list_answer)

    for thread in wiki_threads:
        thread.start()

    for thread in wiki_threads:
        thread.join() 

def getRequest(source):
    if source == 'phone':
        return getRequestFromPhone()

    elif source == 'camera':
        return getRequestFromCamera()

    elif source == 'file':
        return getRequestFromFile()

    elif source == 'test':
        return getRequestsFromInput(
            'What is the capital of France',
            ['Paris', 'London', 'Madrid'])

    return []

def saveFile(s, filename='history.txt'):
    with open(filename, 'a') as f:
        f.write('\n')
        f.write(s)
        f.write('\n')
    
    f.close()

def play_HQ(source='test', save = False):
    n_question = 0
    n_correct_answer = 0
    
    if save:
        saveFile(time.strftime("%a %d %b %Y %H:%M:%S"))

    play = prompt.integer('\nNew question : ')

    while(play):
        s = ""
        n_question += 1
        list_req = getRequest(source)

        if len(list_req):
            print('\nQ',n_question,'.', list_req[0]['q'], '?\n')
            s += 'Q' + str(n_question) + '. ' + list_req[0]['q'] + ' ?'

            # change all structure
            # change list_req into (question, list_answer
            #getResults_Wikipedia(list_req)

            stats = getStats_Google(list_req)
            answer = list_req[max(stats.items(), key=operator.itemgetter(1))[0] - 1]['a']
            
            for n,req in enumerate(list_req):
                print(n+1, '. ', req['a'], '->', stats[n+1])
                s += '\n' + str(n+1) + '. ' + str(req['a']) + ' -> ' + str(stats[n+1])

            print('\nAnswer :', answer)
            s += '\n\nAnswer : ' + answer

            correct_answer = prompt.integer('The correct answer is : ')

            if correct_answer < 1 or correct_answer > 3:
                correct_answer = 1

            correct_answer = list_req[correct_answer-1]['a']
            s += '\nThe correct answer is : ' + correct_answer

            if answer == correct_answer:
                n_correct_answer += 1

            if save:
                saveFile(s)

        play = prompt.integer('\nNew question : ')

    if save:
        saveFile('Accuracy : ' + str(n_correct_answer) + ' / ' + str(n_question))
        saveFile('--------------------------------------------------')

os.system('clear')
play_HQ(source='phone', save=True)
