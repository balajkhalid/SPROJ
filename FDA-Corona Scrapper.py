# This code is being used to scrape FDA's website for Corona related FAQs
# libraries for web scrapping 
import requests
from bs4 import BeautifulSoup

# initlizing  database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from api_key import key, projectId
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

cred = credentials.Certificate("./serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
  'projectId': projectId,
})

db = firestore.client()

corona = db.collection(u'pandemic').document(u'corona')
corona_faqs = corona.collection(u'FAQs - Scrapper')

stop_words = stopwords.words('english')
stop_words.append('Q')
stop_words.append('q:')

# start of scraping

URL = 'https://www.fda.gov/emergency-preparedness-and-response/coronavirus-disease-2019-covid-19/covid-19-frequently-asked-questions'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.findAll("div", {"class": "panel panel-default fda-accordion-panel"})

questions = []
answers = []

for res in results:
    q = res.find('h2', class_ = "panel-title")
    a = res.find('div', class_="panel-body")
    questions.append(q.text)
    answers.append(a.text)

counter = 1
for q, a in zip(questions, answers):
    q = q.lower()
    q = q.split()
    #removing stopwords
    filtered_keywords = [w for w in q if not w in stop_words]

    data = {u'keywords': filtered_keywords,u'answer': a}
    corona_faqs.document(str(counter)).set(data)
    counter += 1
    