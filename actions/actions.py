from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class ActionHandleTopup(Action):
    def name(self) -> Text:
        return "action_handle_topup"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        amount = next(tracker.get_latest_entity_values("amount"), None)

        if amount:
            dispatcher.utter_message(json_message={"topup": True, "amount": amount})
            dispatcher.utter_message(response="utter_confirm_topup")
            return [SlotSet("amount", amount)]
        else:
            dispatcher.utter_message(response="utter_ask_amount")
            return []


#import requests
#requests.post("http://your-backend-api/endpoint", json={"topup": True, "amount": amount})
