# Controllo se ho biddato qualche bundle e lo aggiungo alla lista watching - WILL ADD LATER
# Controllo aquisto completo bundle da parte mia
# Controllo se qualcuno mi supera


import websocket
import json
import time

from sorareBundles.scripts import personalArea

w_socket = 'wss://ws.sorare.com/cable'
identifier = json.dumps({"channel": "GraphqlChannel"})

subscription_query = {
    "query": """
    subscription {
      bundledAuctionWasUpdated {
        slug
    
        cards {
          slug
          player {
            displayName
          }
          rarity
        }
    
        bestBid {
          amount
          bidder {
            ... on User {
              nickname
            }
          }
        }
    
        endDate
    
        open
      }
    }

    """,
    "variables": {},
    "action": "execute"
}


def on_open(ws):
    subscribe_command = {"command": "subscribe", "identifier": identifier}
    ws.send(json.dumps(subscribe_command).encode())

    time.sleep(1)

    message_command = {
        "command": "message",
        "identifier": identifier,
        "data": json.dumps(subscription_query)
    }
    ws.send(json.dumps(message_command).encode())


def handleUpdate(update):
    user = update["result"]['data']['bundledAuctionWasUpdated']['bestBid']['nickname']
    is_sold = update["result"]['data']['bundledAuctionWasUpdated']['open']

    if user == "BETKING (Instead of outbidding me message me)" and not is_sold:
        # add Data
        bundle_to_add = {
            "image_url": update["result"]['data']['bundledAuctionWasUpdated']['cards'][0]["player"]["activeClub"]["pictureUrl"],
            "buy_date": update["result"]['data']['bundledAuctionWasUpdated']["endDate"],
            "buy_price": update["result"]['data']['bundledAuctionWasUpdated']["bestBid"]["amount"],
            "bundle_slug": update["result"]['data']['bundledAuctionWasUpdated']['slug'],
            "cards": []
        }

        for card in update["result"]['data']['bundledAuctionWasUpdated']["cards"]:
            prettyCard = {
                "player_name": card["player"]["displayName"],
                "player_rarity": card["rarity"],
                "player_slug": card["slug"],
                "is_contested": False,
                "is_sold": False,
                "is_listed": False,
                "listing_price": 0,
                "last_insertion_date": None,
                "contesting_cards": []
            }
            bundle_to_add["cards"].append(prettyCard)

        personalArea.insertNewBundle(bundle_to_add)

        # Send to client via WS





def on_message(ws, data):
    message = json.loads(data)
    type = message.get('type')
    if type == 'welcome':
        pass
    elif type == 'ping':
        pass
    elif message.get('message') is not None:
        # handleUpdate(message['message'])
        print(message['message'])


def on_error(ws, error):
    print('Error:', error)


def on_close(ws, close_status_code, close_message):
    print('WebSocket Closed:', close_message, close_status_code)


def long_connection():
    ws = websocket.WebSocketApp(
        w_socket,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
        on_open=on_open
    )
    ws.run_forever()


if __name__ == '__main__':
    long_connection()
