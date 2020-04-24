# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

import requests
from requests.exceptions import HTTPError
import re

from typing import Any, Dict, List, Text, Union, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    ActionExecuted,
    UserUttered,
)
from actions.SendEmail.sendEmail import EmailSender
from actions.config_reader import ConfigReader


class SetName(Action):
    def name(self):
        return "action_set_name"

    def run(self, dispatcher, tracker, domain):
        name = tracker.latest_message.get('text')

        return [SlotSet("name", name)]


class SetEmail(Action):
    def name(self):
        return "action_set_email"

    def run(self, dispatcher, tracker, domain):
        email = tracker.latest_message.get('text')

        return [SlotSet("email", email)]


class SetMobile(Action):
    def name(self):
        return "action_set_mobile"

    def run(self, dispatcher, tracker, domain):
        mobile = tracker.latest_message.get('text')

        return [SlotSet("mobile", mobile)]


class SetPincode(Action):
    def name(self):
        return "action_set_pincode"

    def run(self, dispatcher, tracker, domain):
        pincode = tracker.latest_message.get('text')

        return [SlotSet("pincode", pincode)]


class NearbyCasesSendEmail(FormAction):

    def name(self) -> Text:
        return "user_details_form"

    @staticmethod
    def required_slots(tracker) -> List[Text]:
        return ["name", "email", "mobile", "pincode"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "name": [
                self.from_entity(entity="name"),
                self.from_text(intent="enter_name"),
            ],
            "email": [
                self.from_entity(entity="email"),
                self.from_text(intent="enter_email"),
            ],
            "mobile": [
                self.from_entity(entity="mobile"),
                self.from_text(intent="enter_mobile"),
            ],
            "pincode": [
                self.from_entity(entity="pincode"),
                self.from_text(intent="enter_pincode"),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        name = str(tracker.get_slot("name"))
        email = str(tracker.get_slot("email"))
        mobile = str(tracker.get_slot("mobile"))
        pincode = str(tracker.get_slot("pincode"))
        regex_email = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        regex_mobile = "[0-9]{10}"
        regex_pincode = "[0-9]{6}"
        if re.search(regex_email, email) is None:
            dispatcher.utter_message(
                f"Not a valid email. Please start again and enter valid email.")
            return {"email": None}
        if re.search(regex_mobile, mobile) is None:
            dispatcher.utter_message(
                f"Not a valid mobile number. Please start again and enter valid mobile number.")
            return {"mobile": None}
        if re.search(regex_pincode, pincode) is None:
            dispatcher.utter_message(
                f"Not a valid pincode. Please start again and enter valid pincode.")
            return {"pincode": None}
        try:
            url = "https://api.postalpincode.in/pincode/" + pincode
            res = requests.get(url)
            jsonRes = res.json()
            postOffice = jsonRes[0]["PostOffice"]
            state = str(postOffice[0]["State"])
            if "&" in state:
                state = state.replace("&", "and")
            district = str(postOffice[0]["District"])
            if "&" in district:
                district = district.replace("&", "and")
            if district == "Ahmedabad":
                district = "Ahmadabad"
            elif district == "Bangalore":
                district = "Bengaluru"
            elif district == "Central Delhi":
                district = "New Delhi"
            print(state, end=',')
            print(district)
            try:
                url1 = "https://api.covid19india.org/v2/state_district_wise.json"
                res1 = requests.get(url1)
                jsonRes1 = res1.json()
                stateDistrictData = jsonRes1
                for i in range(len(stateDistrictData)):
                    stateDistrictData1 = stateDistrictData[i]
                    if stateDistrictData1["state"] == state:
                        districtData = stateDistrictData1["districtData"]
                        for j in range(len(districtData)):
                            email_sender = EmailSender()
                            if districtData[j]["district"] == district:
                                confirmed = str(districtData[j]["confirmed"])
                                print(f"\n Confirmed Cases are: {confirmed}")
                                email_file = open(
                                    "actions/email-templates/email-template-district.html", "r")
                                email_message = email_file.read()
                                email_sender.sendEmailDistrict(
                                    name, email, district, confirmed, email_message)
                                dispatcher.utter_message(
                                    template="utter_mail_sent")
                                break
                        else:
                            dispatcher.utter_message(
                                f"Sorry we did not found any data of COVID-19 in {district}. It might be a misspelling or we don't have record of the district.")

            except HTTPError as http_err:
                dispatcher.utter_message(f"HTTP error occurred: {http_err}")
            except Exception as err:
                dispatcher.utter_message(f"Other error occurred: {err}")

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return [
            SlotSet("name", None),
            SlotSet("email", None),
            SlotSet("mobile", None),
            SlotSet("pincode", None)
        ]


class News(Action):

    def name(self) -> Text:
        return "action_news"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            self.config_reader = ConfigReader()
            self.configuration = self.config_reader.read_config()
            url = "http://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=" + \
                self.configuration['NEWS_API']
            res = requests.get(url)
            jsonRes = res.json()
            articles = jsonRes["articles"]
            news = list()
            for i in range(len(articles)):
                title = articles[i]["title"]
                author = articles[i]["author"]
                news_final = str(i + 1) + ". " + \
                    str(title) + " - " + str(author)
                news.append(news_final)
            dispatcher.utter_message("\n\n".join(news))

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return []


class TotalIndiaCases(Action):

    def name(self) -> Text:
        return "action_india_cases"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            url = "https://api.covid19india.org/data.json"
            res = requests.get(url)
            jsonRes = res.json()
            totalIndiaCases = jsonRes["statewise"][0]
            confirmed = str(totalIndiaCases["confirmed"])
            active = str(totalIndiaCases["active"])
            recovered = str(totalIndiaCases["recovered"])
            deaths = str(totalIndiaCases["deaths"])

            dispatcher.utter_message(
                f"Confirmed Cases: {confirmed} \n\nActive Cases: {active} \n\nRecovered Cases: {recovered} \n\nDeaths: {deaths}")

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return []


class SetState(Action):
    def name(self):
        return "action_set_state"

    def run(self, dispatcher, tracker, domain):
        state = tracker.latest_message.get('text')

        return [SlotSet("state", state)]


class GetStateCases(FormAction):

    def name(self) -> Text:
        return "state_form"

    @staticmethod
    def required_slots(tracker) -> List[Text]:
        return ["state"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "state": [
                self.from_entity(entity="state"),
                self.from_text(intent="enter_state"),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        state = tracker.get_slot("state")
        state = state.lower()
        state = state.title()
        if "&" in state:
            state = state.replace("&", "and")
        if state == "Tamilnadu":
            state = "Tamil Nadu"
        elif state == "Delhi ":
            state = "Delhi"
        try:
            url = "https://api.covid19india.org/data.json"
            res = requests.get(url)
            jsonRes = res.json()
            stateWiseCases = jsonRes["statewise"]
            for i in range(len(stateWiseCases)):
                if stateWiseCases[i]["state"] == state:
                    confirmed = str(stateWiseCases[i]["confirmed"])
                    active = str(stateWiseCases[i]["active"])
                    recovered = str(stateWiseCases[i]["recovered"])
                    deaths = str(stateWiseCases[i]["deaths"])
                    dispatcher.utter_message(
                        f"{state} stats of COVID-19 are: \n\nConfirmed Cases: {confirmed} \n\nActive Cases: {active} \n\nRecovered Cases: {recovered} \n\nDeaths: {deaths}")
                    break
            else:
                dispatcher.utter_message(
                    f"Sorry we could not find any state named {state}. It might be a misspelling or we don't have record of the state.")

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return [SlotSet("state", None)]


class TotalGlobalCases(Action):

    def name(self) -> Text:
        return "action_global_cases"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            url = "https://api.covid19api.com/summary"
            res = requests.get(url)
            jsonRes = res.json()
            totalGlobalCases = jsonRes["Global"]
            confirmed = str(totalGlobalCases["TotalConfirmed"])
            recovered = str(totalGlobalCases["TotalRecovered"])
            deaths = str(totalGlobalCases["TotalDeaths"])

            dispatcher.utter_message(
                f"Confirmed Cases: {confirmed} \n\nRecovered Cases: {recovered} \n\nDeaths: {deaths}")

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return []


class SetCountry(Action):
    def name(self):
        return "action_set_country"

    def run(self, dispatcher, tracker, domain):
        country = tracker.latest_message.get('text')

        return [SlotSet("country", country)]


class GetCountryCases(FormAction):

    def name(self) -> Text:
        return "country_form"

    @staticmethod
    def required_slots(tracker) -> List[Text]:
        return ["country"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "country": [
                self.from_entity(entity="country"),
                self.from_text(intent="enter_country"),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        country = tracker.get_slot("country")
        country = country.lower()
        country = country.title()
        try:
            url = "https://corona.lmao.ninja/v2/countries/" + country
            res = requests.get(url)
            jsonRes = res.json()
            countryWiseCases = jsonRes
            if countryWiseCases["country"]:
                confirmed = str(countryWiseCases["cases"])
                recovered = str(countryWiseCases["recovered"])
                deaths = str(countryWiseCases["deaths"])
                dispatcher.utter_message(
                    f"{country} stats of COVID-19 are: \n\nConfirmed Cases: {confirmed} \n\nRecovered Cases: {recovered} \n\nDeaths: {deaths}")
            else:
                dispatcher.utter_message(
                    f"Sorry we could not find any country named {country}. It might be a misspelling or we don't have record of the country.")

        except HTTPError as http_err:
            dispatcher.utter_message(f"HTTP error occurred: {http_err}")
        except Exception as err:
            dispatcher.utter_message(f"Other error occurred: {err}")

        return [SlotSet("country", None)]
