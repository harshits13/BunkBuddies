from typing import Text, List, Any, Dict
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import random as rand

allowed_gender_states = ["Girls", "Boys"]
allowed_location_states = ["Bidholi", "Kandoli", "Pondha", "Doonga"]
allowed_amenity_states = ["gym", "library", "transport"]
# budget_options = ["1.5 Lakhs to 1.8 Lakhs", "1.8 Lakhs to 2 Lakhs", "2 Lakhs+"]
food_options = ["Veg", "Non-Veg"]



class AskForGender(Action):
    def name(self) -> Text:
        return "action_ask_gender"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            text=domain['responses']['utter_ask_gender'][0]['text'],  ## Lmao I chatgpt'd this code
            buttons=[{"title": p, "payload": p} for p in allowed_gender_states],
            button_type="vertical")
        return []


class AskForLocation(Action):
    def name(self) -> Text:
        return "action_ask_location"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(

            text=domain['responses']['utter_ask_location'][rand.randrange(0, 3, 1)]['text'],
            buttons=[{"title": p, "payload": p} for p in allowed_location_states],
            button_type="vertical")
        return []


class AskForBudget(Action):
    def name(self) -> Text:
        return "action_ask_budget"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            text=domain['responses']['utter_ask_budget'][rand.randrange(0, 4, 1)]['text'],
            buttons=[{"title": "1.5 Lakhs - 1.8 Lakhs", "payload": 0},
                     {"title": "1.8 Lakhs - 2 Lakhs", "payload": 1},
                     {"title": "2 Lakhs+", "payload": 2}],
            button_type="vertical")
        return []


class AskForFoodType(Action):
    def name(self) -> Text:
        return "action_ask_food_type"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            text=domain['responses']['utter_ask_food_type'][0]['text'],
            buttons=[{"title": p, "payload": p} for p in food_options])
        return []


class ValidateHostelForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_hostel_form"

    def validate_gender(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `gender` value."""

        if slot_value not in allowed_gender_states:
            dispatcher.utter_message(text=f"I can only find a Boys or Girls hostel for you.")
            return {"gender": None}
        dispatcher.utter_message(text=f"Okay! You're looking for {slot_value} hostel.")
        return {"gender": slot_value}

    def validate_location(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `location` value."""

        if slot_value not in allowed_location_states:
            dispatcher.utter_message(text=f"Sorry but I can only find a hostel in the locations: "
                                          f"Bidholi/Kandoli/Pondha/Doonga.")
            return {"location": None}
        dispatcher.utter_message(text=f"Okay! I'll look for a hostel in {slot_value}.")
        return {"location": slot_value}

    def validate_budget(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `budget` value."""

        dispatcher.utter_message(text=f"Okay! I'll keep your budget in mind.")
        return {"budget": slot_value}

    def validate_food_type(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `food_type` value."""

        if slot_value not in food_options:
            dispatcher.utter_message(text=f"Please select from the options listed above.")
            return {"food_type": None}
        dispatcher.utter_message(text=f"Okay! You prefer {slot_value} food.")
        return {"food_type": slot_value}



import mysql.connector


class ActionRecommendHostel(Action):
    def name(self):
        return "action_recommend_hostel"

    def run(self, dispatcher, tracker, domain):

        location = tracker.get_slot('location')
        gender = tracker.get_slot('gender')
        fees = tracker.get_slot('budget')
        if tracker.get_slot('food_type') == 'Veg':
            food_type = 0
        else:
            food_type = 1

        # Connect to the database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database='hostelbot_db'
        )

        # Create a cursor object
        mycursor = mydb.cursor()
        query_1 = "SELECT * FROM hostels WHERE gender = %s AND location = %s AND fees BETWEEN 150000 AND 175000 AND " \
                  "food_type = %s "
        query_2 = "SELECT * FROM hostels WHERE gender = %s AND location = %s AND fees BETWEEN 175000 AND 195000 AND " \
                  "food_type = %s "
        query_3 = "SELECT * FROM hostels WHERE gender = %s AND location = %s AND fees BETWEEN 180000 AND 200000 AND " \
                  "food_type = %s "
        values = [gender, location, food_type]

        if fees == 0:
            mycursor.execute(query_1, values)

        elif fees == 1:
            mycursor.execute(query_2, values)

        else:
            mycursor.execute(query_3, values)

        result = mycursor.fetchall()

        if result:
            for row in result:
                hostel_name = row[0]
                hostel_gender = row[1]
                hostel_location = row[2]
                hostel_fees = row[3]
                hostel_food_type = row[4]
                hostel_transport = row[5]
                hostel_gym = row[6]
                hostel_image = row[8]

                if hostel_food_type == 0:
                    hostel_food_type = "Vegetarian"
                else:
                    hostel_food_type = "Vegetarian and Non-Vegetarian"

                if hostel_transport == 1:
                    hostel_transport = "✅"
                else:
                    hostel_transport = "❎"

                if hostel_gym == 1:
                    hostel_gym = "✅"
                else:
                    hostel_gym = "❎"

                message = f"Hostel Name: {hostel_name}\nGender: {hostel_gender}\nLocation: {hostel_location}\nFees: {hostel_fees}\nFood Offering: {hostel_food_type}\nTransportation: {hostel_transport}\nGym: {hostel_gym}\n"

                if hostel_image is not None:
                    dispatcher.utter_message(text=message, image=hostel_image)
                else:
                    dispatcher.utter_message(text=message)

        else:
            dispatcher.utter_message("Sorry, I couldn't find a hostel that fits your criteria.")

        return []
