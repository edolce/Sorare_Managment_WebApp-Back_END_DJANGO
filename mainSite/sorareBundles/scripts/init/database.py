import json

import mysql.connector
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from sorareBundles.scripts.init.bundleCalsses import Bundle, Card, ContestingCard, CardAverages
import datetime


# All'avvio scannare tutte le carte in possesso e confrontarle con il database per vedere se ci sono stati cambiamenti
# Avviare websocket che tiene traccia di (ognuno di questi dati viene inviato via besocket):
# 1-Aquisto di bundles -> aggiunta al database di bundles
# 2-Contestazione -> aggiunta al database di carte
# 3-Vendita Di una carta -> aggiunta al database di carte

def getDatabaseConnection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="edoardo2000",
        database="sorare-app"
    )


## DONE
def insertNewBundle(bundle):
    mydb = getDatabaseConnection()

    cursor = mydb.cursor()

    sql = "INSERT INTO my_bundle (image_url, buy_date, buy_price, slug) VALUES (%s, STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ'), " \
          "%s, %s) "
    val = (bundle.image_url, bundle.buy_date, bundle.buy_price, bundle.bundle_slug)
    cursor.execute(sql, val)

    # Get bundle Id
    bundle_id = cursor.lastrowid

    for card in bundle.cards:
        sql = "INSERT INTO my_card (bundle_id, player_name, player_rarity, is_contested, is_sold, listing_price, " \
              "is_listed, last_insertion_date,slug,player_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        val = (bundle_id, card.display_name, card.rarity, False, False,
               0, False, None, card.card_slug, card.player_image)
        # val = (bundle_id, card["display_name"], card["player_rarity"], card["is_contested"], card["is_sold"],
        #        card["listing_price"], card["is_listed"], card["last_insertion_date"])
        cursor.execute(sql, val)

        for contestingCard in card.contesting_cards:
            insertNewContestingCard(contestingCard)

    mydb.commit()


def updateCardsAverage(averages):
    mydb = getDatabaseConnection()

    cursor = mydb.cursor()

    for cardAverageKey in averages.keys():
        sql = "INSERT INTO card_average (player_name, 3_days, 7_days, 14_days, 30_days, best_market_price, " \
              "player_id, player_image,last_update) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        val = (cardAverageKey,
               averages[cardAverageKey]["3_days"],
               averages[cardAverageKey]["7_days"],
               averages[cardAverageKey]["14_days"],
               averages[cardAverageKey]["30_days"],
               averages[cardAverageKey]["best_market_price"],
               averages[cardAverageKey]["player_id"],
               averages[cardAverageKey]["player_image"],
               datetime.datetime.now())
        cursor.execute(sql, val)

    mydb.commit()


## DONE
def insertNewContestingCard(contestingCard):
    mydb = getDatabaseConnection()

    cursor = mydb.cursor()

    sql = "INSERT INTO contesting_card (card_id, listing_price, is_sold, insertion_date) VALUES (%s, %s, %s, %s)"
    val = (contestingCard["card_id"], contestingCard["listing_price"], contestingCard["is_sold"],
           contestingCard["insertion_date"])
    cursor.execute(sql, val)


## RETURN ALL DATABASE BUNDLES WITH ASSOCIATED CARDS
def getAllMyBundlesData():
    # Get all the bundles in the database
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM my_bundle")
    mySqlBundles = cursor.fetchall()
    feedbackBundles = []

    # iterate all bundles in database to get every card
    for bundle in mySqlBundles:

        # save the bundle
        bundleToAdd = Bundle(
            bundle_id=bundle[0],
            image_url=bundle[1],
            buy_date=bundle[2],
            buy_price=bundle[3],
            bundle_slug=bundle[4],
            cards=[]
        )

        # get all cards of the bundle
        sql = "SELECT * FROM my_card WHERE bundle_id=%s"
        val = ([bundle[0]])
        cursor.execute(sql, val)
        mySqlCards = cursor.fetchall()

        # iterate every card from the mysql feedback
        for card in mySqlCards:

            cardToAdd = Card(
                card_id=card[0],
                bundle_id=card[1],
                player_name=card[2],
                player_rarity=card[3],
                is_contested=card[4],
                is_sold=card[5],
                listing_price=card[6],
                is_listed=card[7],
                last_insertion_date=card[8],
                contesting_cards=[],
                card_slug=card[9],
                player_image=card[11],
            )

            sql = "SELECT * FROM contesting_card WHERE card_id=%s"
            val = ([card[0]])
            cursor.execute(sql, val)
            mySqlContestingCards = cursor.fetchall()

            for contestingCard in mySqlContestingCards:
                cardToAdd.contesting_cards += ContestingCard(
                    contesting_card_id=contestingCard[0],
                    card_id=contestingCard[1],
                    listing_price=contestingCard[2],
                    is_sold=contestingCard[3],
                    insertion_date=contestingCard[4],
                )

            bundleToAdd.cards.append(cardToAdd)

        feedbackBundles.append(bundleToAdd)

    return feedbackBundles


def getCardsAverage(names):
    # Get all the bundles in the database
    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM card_average")
    cardsAverages = cursor.fetchall()
    validCardAverage = {}

    # iterate all bundles in database to get every card
    for cardAverage in cardsAverages:

        # save the bundle
        cardAverageToAdd = CardAverages(
            player_name=cardAverage[0],
            _3_days=cardAverage[1],
            _7_days=cardAverage[2],
            _14_days=cardAverage[3],
            _30_days=cardAverage[4],
            best_market_price=cardAverage[5],
            player_id=cardAverage[6],
            player_image=cardAverage[7],
            last_update=cardAverage[8],
        )

        if cardAverage[0] in names:
            if cardAverageToAdd.last_update <= datetime.datetime.now() + datetime.timedelta(minutes=60):
                validCardAverage[cardAverageToAdd.player_name] = {
                    '3_days': cardAverageToAdd._3_days,
                    '7_days': cardAverageToAdd._7_days,
                    '14_days': cardAverageToAdd._14_days,
                    '30_days': cardAverageToAdd._30_days,
                    'best_market_price': cardAverageToAdd.best_market_price,
                    'player_id': cardAverageToAdd.player_id,
                    'player_image': cardAverageToAdd.player_image
                }
                names.remove(cardAverageToAdd.player_name)

    return {
        "valid": validCardAverage,
        "not_valid": names
    }


## NOT DATABASE

# # Controlla tutti i bundles vinti e vedo se sono up to date nel database [SOLO ALL AVVIO]
# def getOldData():
#     cursor0 = ""
#     cursor1 = ""
#     hasNextPage0 = True
#     hasNextPage1 = True
#     soldCard = []
#     ownedBundles = []
#     while hasNextPage0 or hasNextPage1:
#         transport = AIOHTTPTransport(
#             url="https://api.sorare.com/graphql",
#             headers={"JWT-AUD": "SorareDataApp",
#                      "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
#         )
#
#         query = gql(
#             """
#             query {
#               user(slug: "betking-instead-of-outbidding-me-message-me") {
#                 soldSingleSaleOffers (after: \"""" + cursor0 + """\") {
#                     pageInfo {
#                                     endCursor
#                                     hasNextPage
#                                     hasPreviousPage
#                                     startCursor
#                                   }
#                   nodes {
#                     endDate
#                     price
#                     card {
#                       slug
#                     }
#                   }
#                 }
#
#                 wonEnglishAuctions(after: \"""" + cursor1 + """\") {
#                     pageInfo {
#                                     endCursor
#                                     hasNextPage
#                                     hasPreviousPage
#                                     startCursor
#                                   }
#                   nodes {
#                     endDate
#                     slug
#                     currentPrice
#                     cards {
#                       slug
#                       player {
#                         slug
#                         displayName
#                       }
#                       team {
#                         ... on Club {
#                           pictureUrl
#                         }
#                       }
#                       rarity
#                     }
#                   }
#                 }
#               }
#             }
#
#
#                     """
#         )
#
#         result = Client(transport=transport).execute(query)
#
#         if hasNextPage0:
#             cursor0 = result["user"]["soldSingleSaleOffers"]["pageInfo"]["endCursor"]
#             hasNextPage0 = result["user"]["soldSingleSaleOffers"]["pageInfo"]["hasNextPage"]
#
#             for card in result["user"]["soldSingleSaleOffers"]["nodes"]:
#                 soldCard.append(
#                     {
#                         "price": card["price"],
#                         "card_slug": card["card"]["slug"],
#                         "end_date": card["endDate"]
#                     }
#                 )
#         if hasNextPage1:
#             cursor1 = result["user"]["wonEnglishAuctions"]["pageInfo"]["endCursor"]
#             hasNextPage1 = result["user"]["wonEnglishAuctions"]["pageInfo"]["hasNextPage"]
#
#             for bundle in result["user"]["wonEnglishAuctions"]["nodes"]:
#
#                 prettyBundle = {
#                     "image_url": bundle["cards"][0]["team"]["pictureUrl"],
#                     "bundle_slug": bundle["slug"],
#                     "buy_price": bundle["currentPrice"],
#                     "buy_date": bundle["endDate"],
#                     "cards": []
#                 }
#
#                 for card in bundle["cards"]:
#                     prettyBundle["cards"].append({
#                         "card_slug": card["slug"],
#                         "player_slug": card["player"]["slug"],
#                         "display_name": card["player"]["displayName"],
#                         "player_rarity": card["rarity"],
#                         "contesting_cards": [],
#                     })
#
#                 ownedBundles.append(prettyBundle)
#
#             pass
#
#     return {
#         "ownedBundles": ownedBundles,
#         "soldCards": soldCard
#     }
#
#
# def checkDatabaseBundles(bundlesToCheck):
#     bundlesDatabase = getAllMyBundlesData()
#
#     dataSlugs = []
#
#     for bundleDatabase in bundlesDatabase:
#         dataSlugs.append(bundleDatabase["bundle_slug"])
#
#     for bundle in bundlesToCheck:
#         if bundle["bundle_slug"] not in dataSlugs:
#             if len(bundle["cards"]) != 5:
#                 print("not a bundle: " + str(bundle))
#                 continue
#             # Trigger the not in database event
#             insertNewBundle(bundle)
#             print("added new bundle: " + str(bundle))
#         else:
#             print("Already Present: " + str(bundle))
#
#     pass
#
#
# def fetchSaleOfferData(data):
#     transport = AIOHTTPTransport(
#         url="https://api.sorare.com/graphql",
#         headers={"JWT-AUD": "SorareDataApp",
#                  "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
#     )
#
#     query = gql(
#         """
#         query{
#           allCards(slugs:[""" + str(json.dumps(data)) + """]){
#             nodes{
#             onSale
#             liveSingleSaleOffer{
#               price
#               createdAt
#               endDate
#               sender{
#                   ... on User{
#                     nickname
#                 }
#               }
#             }
#             ownerWithRates{
#               account{
#                 owner{
#                   ... on User{
#                     nickname
#                   }
#                 }
#               }
#             }
#           }
#           }
#         }
#         """
#     )
#
#     data = Client(transport=transport).execute(query)
#
#     feedbackData = {}
#
#     for saleOffer in data["allCards"]["nodes"]:
#         feedbackData[saleOffer["slug"]] = saleOffer
#
#     return feedbackData
#
#
# def databaseCardCheck():
#     # Controllo se le carde sono in vendita(contestate/vendute) o se sono scadute (vendita: on -> of) o appenma messe
#     # in vendita (vendita: off -> on)
#
#     # Controllo se qualche carta e stata venduta
#     data = getOldData()
#
#     bundlesDatabase = getAllMyBundlesData()
#     bundleCards = {}
#     # Get all cards
#     for bundle in bundlesDatabase:
#         for card in bundle["cards"]:
#             print(card)
#             bundleCards[card["card_slug"]] = card
#
#     print(bundleCards)
#
#     sqls = ""
#     vals = ""
#
#     # Controllo se alcune carte sono state vendute
#     for card in data["soldCards"]:
#         if card["card_slug"] in bundleCards.keys():
#             # La carta e stata venduta
#             # Controllare se bisogna aggiornare il database
#             if bundleCards[card["card_slug"]]["is_sold"]:
#                 # Aggiungi alla coda per aggiornare carta
#                 sql = "UPDATE Customers SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = %s  WHERE id = %s; "
#                 val = [False, True, card["price"], False, card["end_date"], bundleCards["card_id"]]
#                 sqls += sql
#                 vals += val
#
#     if sqls != "":
#         mydb = getDatabaseConnection()
#         cursor = mydb.cursor()
#         cursor.execute(sqls, vals)
#
#     # Controllo della situazione delle carte non vendute
#     bundlesDatabase = getAllMyBundlesData()
#     allCards = {}
#     for bundle in bundlesDatabase:
#         for card in bundle["cards"]:
#             allCards[card["card_slug"]] = card
#     saleOffersData = fetchSaleOfferData(allCards.keys())
#     sqls = ""
#     vals = ""
#     for card_slug in allCards.keys():
#         # la carta non e venduta e ora lo e, e il propietario non e lo stesso
#         if not allCards[card_slug]["is-sold"]:
#             if saleOffersData[card_slug]["on-sale"]:
#                 # la carta non e venduta, e il propietario e lo stesso || cambio in listed = true
#                 sql = "UPDATE Customers SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = %s  WHERE id = %s; "
#                 val = [False, False, saleOffersData[card_slug]["ownerWithRates"]["price"], True, None,
#                        allCards[card_slug]["card_id"]]
#             else:
#                 # la carta non e venduta, e il propietario e lo stesso || cambio in listed = false
#                 sql = "UPDATE Customers SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = %s  WHERE id = %s; "
#                 val = [False, False, saleOffersData[card_slug]["ownerWithRates"]["price"], False, None,
#                        allCards[card_slug]["card_id"]]
#             sqls += sql
#             vals += val
#
#     if sqls != "":
#         mydb = getDatabaseConnection()
#         cursor = mydb.cursor()
#         cursor.execute(sqls, vals)
#
#     pass
#
#
# def upToDateDataCheck():
#     data = getOldData()
#     checkDatabaseBundles(data["ownedBundles"])


if __name__ == '__main__':
    # databaseCardCheck()
    # upToDateDataCheck()
    pass
