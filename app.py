import os
import sys

import requests
from flask import Flask, request
import requests
import json
from lxml import html
import re
import zipcode
import numbers

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "awesome_bot":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "It works!", 200


@app.route('/', methods=['POST'])
def webhook():


    # endpoint for processing incoming messaging events
    #url = 'https://www.neighborhoodscout.com/ca/san-jose/crime'
    #greeting_message()
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing


    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    # print (sender_id)
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if message_text == "Hi" or message_text == "/help":
                        send_message(sender_id, "Welcome to the Crime Report Bot! Enter a city in California to get "
                                                "crime statistics \n"
                                                "Type /help to get info")
                    else:
                        if (validate_city(message_text) == True):
                            current_city = message_text
                            send_message(sender_id, get_crime_report(current_city))
                            safety_risk = calculate_safety(current_city)
                            send_message(sender_id, "We rate your city as - {}".format(safety_risk))
                        else:
                            send_message(sender_id, "Enter valid city")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    send_message(sender_id, "Hello there!")

    return "ok", 200


def validate_city(message_text):
    if ' ' in message_text:
        message_text = message_text.replace(" ", "-").lower()
    else:
        message_text = message_text.lower()
    url = 'https://www.neighborhoodscout.com/ca/{}/crime'.format(message_text)
    page = requests.get(url)

    if (page.status_code == 200):
        return True
    else:
        return False


#print("Crime index:", crime_index[0].text)
#print('Number of violent cases:', violent_number[0].text)
#print('Number of property-related cases:', property_number[0].text)
#print('Murder:', murder_number[0].text)
#print('Rape:', rape_number[0].text)
#print('Robbery:', robbery_number[0].text)
#print('Assault:', assault_number[0].text)

#def send_criminal_statistics():
#  return "Statistics!"

def get_crime_report(city_input):

    if ' ' in city_input:
        city = city_input.replace(" ", "-").lower()
    else:
        city = city_input.lower()
    url = 'https://www.neighborhoodscout.com/ca/{}/crime'.format(city)
    page = requests.get(url)
    if (page.status_code == 200):
        tree = html.fromstring(page.content)
        crime_index = tree.xpath('//*[@class="score mountain-meadow"]')
        violent_number = tree.xpath('//*[@id="data"]/section[1]/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]/p/strong')
        property_number = tree.xpath('//*[@id="data"]/section[1]/div[2]/div[2]/div/div/table/tbody/tr[1]/td[3]/p/strong')
        murder_number = tree.xpath('//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[2]')
        rape_number = tree.xpath('//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[3]')
        robbery_number = tree.xpath('//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[4]')
        assault_number = tree.xpath('//*[@id="data"]/section[2]/div[5]/div/div/table/tbody/tr[1]/td[5]')
        return ("Crime index is {} \n Number of violent cases is {} \n Number of property related cases is {} \n"
                  "Murder rate is {} \nRape - {} Robberies - {} \n Assaults is {} \n").format(crime_index[0].text,
                                                                                        violent_number[0].text,
                                                                                        property_number[0].text,
                                                                                        murder_number[0].text,
                                                                                        rape_number[0].text,
                                                                                        robbery_number[0].text,
                                                                                        assault_number[0].text)

def calculate_safety(city_input):

    if ' ' in city_input:
        city = city_input.replace(" ", "-").lower()
    else:
        city = city_input.lower()
    url = 'https://www.neighborhoodscout.com/ca/{}/crime'.format(city)
    page = requests.get(url)
    if (page.status_code == 200):
        tree = html.fromstring(page.content)
        crime_index = tree.xpath('//*[@class="score mountain-meadow"]')
        crime_index = int(crime_index[0].text)

        try:
            crime_index += 1
            crime_index -= 1
        except TypeError:
            print ("error crime_index")

        #print ("crime_index ", crime_index )
        #print("crime_index ", crime_index)

        if (crime_index > 0 and crime_index <= 10):
            return "Holy shit! Get out of that shithole!"
        elif (crime_index > 10 and crime_index < 30):
            return "It's alright but you will still get stabbed on your way to Walmart"
        elif (crime_index > 30 and crime_index < 50):
            return "Your city is almost safe"
        elif (crime_index > 50 and crime_index <= 100):
            return "Your city is safe!"
        else:
            return "Invalid response"



def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": "EAAFT6DiOFhoBAEwRIzOUoqJ7r5ZBc66nvkDrUeHu8ZChGArOfBsv3TMk113MwQav27q6oHzwmuZBfvsKZCdlivuvBlgYU1YlFKgYiJX8nBMK9ZAO4RvFPRgoNbv4ALkEjsJkscoBd4n3ugsw2SCUZBvaZCkBSUoxVvVsakcMjscAAZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def greeting_message():
    data = json.dumps({
        "greeting": {
            "locale": "en_US",
            "text": "Get Started"
        }
    })

    r = requests.get("https://graph.facebook.com/v2.6/messenger_profile?fields=greeting&access_token=EAAFT6DiOFhoBAEwRIzOUoqJ7r5ZBc66nvkDrUeHu8ZChGArOfBsv3TMk113MwQav27q6oHzwmuZBfvsKZCdlivuvBlgYU1YlFKgYiJX8nBMK9ZAO4RvFPRgoNbv4ALkEjsJkscoBd4n3ugsw2SCUZBvaZCkBSUoxVvVsakcMjscAAZDZD")
    if r.status_code != 200:
        print("ERROR WITH GREETING MESSAGE")

def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
      print("message is ", msg)
#        msg = unicode(msg).format(*args, **kwargs)
#        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)