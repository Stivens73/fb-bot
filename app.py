import os
import sys
import json
from lxml import html

import requests
from flask import Flask, request

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

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    #print (sender_id)
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if (validate_city(message_text) == True):
                      send_criminal_statistics()


                    send_message(sender_id, "Welcome {{ user_first_name }}")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def validate_city(message_text):
  url = 'https://www.neighborhoodscout.com/ca/{}/crime'.format(message_text)
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

"""
from flask import Flask, request
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAFT6DiOFhoBAEwRIzOUoqJ7r5ZBc66nvkDrUeHu8ZChGArOfBsv3TMk113MwQav27q6oHzwmuZBfvsKZCdlivuvBlgYU1YlFKgYiJX8nBMK9ZAO4RvFPRgoNbv4ALkEjsJkscoBd4n3ugsw2SCUZBvaZCkBSUoxVvVsakcMjscAAZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  print ("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'awesome_bot':
    print ("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print ("Verification failed!")
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print (("Handling Messages"))
  payload = request.get_data()
  print (payload)
  for sender, message in messaging_events(payload):
    print ("Incoming from %s: %s" % (sender, message))
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):


  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print (r.text)

if __name__ == '__main__':
  app.run()
  """