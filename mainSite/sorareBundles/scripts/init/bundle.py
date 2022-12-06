import mysql.connector
from sorareBundles.scripts.init import graphqlRequests
from sorareBundles.scripts.init.database import getAllMyBundlesData, insertNewBundle

owner = "godbetking"


# import data that are present in sorare but not in database
def updateDatabaseBundlesWithSorareData():
    databaseBundles = getAllMyBundlesData()
    sorareBundles = graphqlRequests.getOwnedBundlesAndSoldCardsFromSorare()["ownedBundles"]

    databaseBundlesSlug = []

    for databaseBundle in databaseBundles:
        databaseBundlesSlug.append(databaseBundle.bundle_slug)

    for sorareBundle in sorareBundles:
        if sorareBundle.bundle_slug not in databaseBundlesSlug:
            if len(sorareBundle.cards) != 5:
                print("not a bundle: " + str(sorareBundle))
                continue
            # Trigger the not in database event
            insertNewBundle(sorareBundle)
            print("added new bundle: " + str(sorareBundle))
        else:
            print("Already Present: " + str(sorareBundle))


def getDatabaseConnection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="edoardo2000",
        database="sorare-app"
    )


def updateCardDatabase(event_id, card_id, marketInfo):
    sql = ""
    val = []
    print(card_id)
    if event_id == 0:
        sql = "UPDATE my_card SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ'),last_insertion_date=STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ')  WHERE id = %s; "
        val = [False, True, marketInfo.buy_price, False, marketInfo.buy_date, marketInfo.buy_date, card_id]
        print("SOLD")
    elif event_id == 1:
        sql = "UPDATE sorareapp.my_card SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ'),last_insertion_date=STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ')  WHERE id = %s; "
        val = [False, False, marketInfo.live_sell_offer["ownerWithRates"]["price"], True,
               marketInfo.live_sell_offer["sell_end_date"], marketInfo.live_sell_offer["sell_start_date"], card_id]
        print("NOT LISTED -> LISTED")
    elif event_id == 2:
        sql = "UPDATE my_card SET is_contested = %s, is_sold = %s, listing_price = %s, is_listed = %s,sold_date = STR_TO_DATE(%s,'%Y-%m-%dT%H:%i:%SZ')  WHERE id = %s; "
        val = [False, False, 0, False, None, card_id]
        print("LISTED -> NOT LISTED")

    mydb = getDatabaseConnection()
    cursor = mydb.cursor()
    cursor.execute(sql, val)
    mydb.commit()


# update card data with info from sorare market
def databaseCardCheck():
    # get list of card slugs from database (cards to control)
    databaseBundles = getAllMyBundlesData()
    databaseCards = {}
    databaseCardsSlug = []
    for bundle in databaseBundles:
        for card in bundle.cards:
            databaseCards[card.card_slug] = card
            databaseCardsSlug.append(card.card_slug)

    # get all info from sorare market for given slugs
    marketInfo = graphqlRequests.getMarketInfoForCardsFromSorare(databaseCardsSlug)

    for cardSlug in databaseCardsSlug:
        databaseCard = databaseCards[cardSlug]
        marketInfoCard = marketInfo[cardSlug]

        # case if the card is already sold
        if databaseCard.is_sold:
            pass
        # case if the card has not sold yet
        else:
            print(databaseCard.card_slug)
            print(marketInfoCard.owner_slug)
            # case if the owner of the card is different (card has been sold ONLY CASE)
            if owner != marketInfoCard.owner_slug:
                updateCardDatabase(0, databaseCard.card_id, marketInfoCard)
            # case if the owner is the same (2 case/ card is not sold)
            else:
                # case if the card wasn't listed, but now it is (change is_listed/last_listed_date/listed_price in database)
                if not databaseCard.is_listed and marketInfoCard.is_on_sale:
                    updateCardDatabase(1, databaseCard.card_id, marketInfoCard)
                    pass
                # case if it was listed, but now it isn't
                if databaseCard.is_listed and not marketInfoCard.is_on_sale:
                    updateCardDatabase(2, databaseCard.card_id, marketInfoCard)
                    pass
            pass


def initAndGetBundlesData():
    updateDatabaseBundlesWithSorareData()
    databaseCardCheck()
    bundles = getAllMyBundlesData()

    dictBundles = []

    for bundle in bundles:
        for card in bundle.cards:
            if card.last_insertion_date is not None:
                card.last_insertion_date = card.last_insertion_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        bundle.cards = list(map(lambda x: x.__dict__, bundle.cards))
        bundle.buy_date = bundle.buy_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        dictBundle = bundle.__dict__
        dictBundles.append(dictBundle)

    return dictBundles


if __name__ == '__main__':
    updateDatabaseBundlesWithSorareData()
    databaseCardCheck()
