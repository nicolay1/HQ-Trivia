import requests
import wikipedia
import json

from threading import Thread

class Wikipedia(Thread):
    def __init__(self, question, answer):
        Thread.__init__(self)
        self.question = question
        self.answer = answer
        self.result = []
      
    def run(self):
        url = 'http://demo.allennlp.org/predict/machine-comprehension'

        try:
            passage = wikipedia.summary(self.answer)

            data = {"passage": passage, "question": self.question}
            self.result = json.loads(requests.post(url, json=data).text)['best_span_str']
        
        except wikipedia.exceptions.DisambiguationError as e:
            print(e.options[:3])

            for subject in e.options[:3]:
                passage = wikipedia.summary(subject)

                data = {"passage": passage, "question": self.question}
                self.result.append(json.loads(requests.post(url, json=data).text)['best_span_str'])

        except:
            pass

        print(self.answer, ':', self.result)
