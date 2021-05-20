# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from api_key import key, projectId, algorthimia_api, algorthimia_key
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
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


class ActionFindFacility(Action):

    def name(self) -> Text:
        return "action_find_facility"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        loc = tracker.get_slot('location')  # obtain location

        # to get lattitude and longitude of the areas
        URL = "https://maps.googleapis.com/maps/api/geocode/json"

        PARAMS = {'address': loc,  'key': key}

        # sending get request and saving the response as response object
        r = requests.get(url=URL, params=PARAMS)

        # extracting data in json format
        data = r.json()

        lat = data['results'][0]['geometry']['location']['lat']
        long = data['results'][0]['geometry']['location']['lng']
        location = str(lat) + "," + str(long)

        # to find the nearby facility
        URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        radius = "1500"
        type = tracker.get_slot('facility_type')

        PARAMS = {'location': location, 'radius': radius,
                  'opennow': True, 'type': type, 'key': key}

        # sending get request and saving the response as response object
        r = requests.get(url=URL, params=PARAMS)

        # extracting data in json format
        data = r.json()
        final_resp = ""  # format the final response in name, vicinity format
        i = 0
        for x in data:
            final_resp += "Name: " + \
                data['results'][i]['name'] + " Vicinity: " + \
                data['results'][i]['vicinity'] + "\n"
            i += 1

        dispatcher.utter_message(text=final_resp)

        return []


class ActionFindService(Action):

    def name(self) -> Text:
        return "action_find_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # since corona related also adding testing facilities.
        final_resp = "Pakistan COVID-19 Helpline: 1166\nEdhi Ambulance: 115\nRescue: 1122\nAman TeleHealth: 111-11-9123\nTesting Facilities list: http://covid.gov.pk/facilities/10%20June%202020%20Current%20Laboratory%20Testing%20Capacity%20for%20COVID.pdf"

        dispatcher.utter_message(text=final_resp)

        return []


class ActionFindCases(Action):

    def name(self) -> Text:
        return "action_findcases"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        distype = "None"
        condition = "None"
        condition.lower()
        distype = tracker.get_slot("disaster_type")
        condition = tracker.get_slot("patient_condition")

        # access api
        URL = "https://coronavirus-19-api.herokuapp.com/countries/pakistan"
        r = requests.get(url=URL)

        # extracting data in json format
        data = r.json()

        if condition == "infected" or condition == "infect" or condition == "infection":
            response = "Currently the number of "+distype+" victims in Pakistan " + data["todayCases"]

        elif condition == "died" or condition == "death" or condition == "dying" or condition == "deaths":
            response = "Currently the number of "+distype+" victims in Pakistan" + data["todayDeaths"]

        elif condition == "recovered" or condition == "recoveries" or condition == "recover":
            response = "Currently the number total of "+distype+" recoveries in Pakistan " + data["recovered"]

        elif condition == "critical" :
            response = "Currently the number total of "+distype+" critical patients in Pakistan " + data["critical"]

        elif condition == "None":
            response = "Currently, in Pakistan the cases of the following are:\nDeaths:" + data["todayDeaths"] + "\nRecovered Patients:" + data["recovered"] + "\nInfected Patients: " +  data["todayCases"] +"\nCritical Condition:" + data["critical"]

        dispatcher.utter_message(text=response)

        return []


class ActionCheckSymptom(Action):

    def name(self) -> Text:
        return "action_checksymptom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        checksymp = "None"
        distype = tracker.get_slot("disaster_type")
        checksymp = tracker.get_slot("symptom")
        getsymptomsfromdatabase = ["fever", "fatigue", "cough"]
        if checksymp in getsymptomsfromdatabase:
            response = "Yes, " + checksymp + " is a symptom of " + distype + \
                "\nOther symtoms include blah blah\nIf you have more of these symptoms, please consult a doctor to recieve a certain diagnosis. \nWould you like me to find a hospital for you?"
        else:
            response = "According to my database, this isn't a verified or listed symptom of " + \
                distype + " but i recommend you consult a doctor to be certain.\nWould you like me to find a hospital for you?"

        dispatcher.utter_message(text=response)
        facility = "hospital"
        return [SlotSet("facility_search", facility)]


class ActionFindMed(Action):

    def name(self) -> Text:
        return "action_findmeds"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")

        response = "According to WHO:\nScientists around the world are working to find and develop treatments for COVID-19.\nOptimal supportive care includes oxygen for severely ill patients and those who are at risk for severe disease and more advanced respiratory support such as ventilation for patients who are critically ill.\nDexamethasone is a corticosteroid that can help reduce the length of time on a ventilator and save lives of patients with severe and critical illness. Read our dexamethasone Q&A for more information.\nResults from the WHO’s Solidarity Trial indicated that remdesivir, hydroxychloroquine, lopinavir/ritonavir and interferon regimens appear to have little or no effect on 28-day mortality or the in-hospital course of COVID-19 among hospitalized patients.\nHydroxychloroquine has not been shown to offer any benefit for treatment of COVID-19. Read our hydroxychloroquine Q&A for more information.\nWHO does not recommend self-medication with any medicines, including antibiotics, as a prevention or cure for COVID-19. WHO is coordinating efforts to develop treatments for COVID-19 and will continue to provide new information as it becomes available.\nFind more details at: https://www.who.int/emergencies/diseases/novel-coronavirus-2019/question-and-answers-hub/q-a-detail/coronavirus-disease-covid-19#"
        dispatcher.utter_message(text=response)

        return[]


class ActionFindTest(Action):

    def name(self) -> Text:
        return "action_findtests"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")

        response = "If you want to get tested for "+distype + \
            " the following tests are available for you:\nRT-PCR\nAntigen test\nAntibody test"
        dispatcher.utter_message(text=response)
        return[]


class ActionFindAccuracy(Action):

    def name(self) -> Text:
        return "action_getacc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        testtype = tracker.get_slot("test")

        response = "The accuracy of medical tests can vary depending upon the testing environment and equipment; but generally the accuracy of the " + testtype+" is: "
        dispatcher.utter_message(text=response)
        dispatcher.utter_message(image="https://imgur.com/a/q0TeP63")

        return[]


class ActionListPrevent(Action):

    def name(self) -> Text:
        return "action_prevent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")

        response = "The most updated and verifed methods to prevent " + distype + " are:"
        dispatcher.utter_message(text=response)

        return[]


# class ActionConfirmCause(Action):

#     def name(self) -> Text:
#         return "action_confirm_cause"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         check_cause = "None"
#         distype = tracker.get_slot("disaster_type")
#         check_cause = tracker.get_slot("cause")
#         if check_cause == "None":
#             check_cause = tracker.latest_message['text']

#         response = " According to blah blah " + \
#             check_cause + " does/doesn't cause " + distype
#         dispatcher.utter_message(text=response)

#         return[]


class ActionAskCause(Action):

    def name(self) -> Text:
        return "action_ask_cause"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")
        response = "I'm a bit confused. Could you tell me the cause again?"
        dispatcher.utter_message(text=response)

        return[]

# ML model query
class ActionConfirmCause(Action):
    def name(self) -> Text:
        return "action_ml"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")
        distype.lower()
        query = tracker.get_slot('query')  # obtain location

        if distype == "covid-19" or distype == "corona" or distype == "coronavirus" or distype == "covid" or distype == "covid19" or distype == "corona virus": 
            client = Algorithmia.client(algorthimia_key)
            algo = client.algo(algorthimia_api)
            algo.set_options(timeout=300)  # optional
            res = algo.pipe(input).result
            response = "According to our ML model your query is " + res
            dispatcher.utter_message(text=response)
        else:
            response = "Currently there is no machine learning model for this disaster type. You can visit our Forums page to get an answer to your query, https://corona-info.flywheelsites.com/home/forums/"
            dispatcher.utter_message(text=response)

        return[]


# DB model query
class ActionDB(Action):

    def name(self) -> Text:
        return "action_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        distype = tracker.get_slot("disaster_type")
        distype.lower()
        query = tracker.get_slot('query')  # obtain location

        # breaking query
        query = query.lower()
        new_query = query.split()

        # removing stopwords
        filtered_query = [w for w in new_query if not w in stop_words]

        # if query is more than 10 values (limit by Google Firebase)
        if len(filtered_query) > 10:
            for i in range(0, len(filtered_query)-10):
                filtered_query.pop()

        # quering
        if distype == "covid-19" or distype == "corona" or distype == "coronavirus" or distype == "covid" or distype == "covid19" or distype == "corona virus": 
            query_result = corona_faqs.where(
                u'keywords', u'array_contains_any', filtered_query).stream()
        else: 
            response = "Currently there are no FAQs for this disaster type. You can visit our Forums page to get an answer to your query, https://corona-info.flywheelsites.com/home/forums/"
            dispatcher.utter_message(text=response)

        # finding item whose keywords match the most
        ans = ""
        max_matches = 0

        for query in query_result:
            dict_ans = query.to_dict()
            matches = sum(
                [1 for i in dict_ans['keywords'] if i in filtered_query])
            if matches > max_matches:
                max_matches = matches
                ans = dict_ans['answer']

        dispatcher.utter_message(text=response)

        return[]
