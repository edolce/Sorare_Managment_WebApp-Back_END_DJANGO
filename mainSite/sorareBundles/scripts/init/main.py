from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import json

def getAssetId(card_slug):
    transport = AIOHTTPTransport(
        url="https://api.sorare.com/graphql",
        headers={"JWT-AUD": "SorareDataApp",
                 "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
    )

    cardData = gql(
        "query{card(slug:\""+card_slug+"\"){assetId}}"
    )

    # Get StarKey
    cardData = Client(transport=transport).execute(cardData)

    return cardData["card"]["assetId"]

privateKey = "0x00396b30215e17998d5c4e3fd70d11211fa2d5c22f77816a6ad4479625b27e20"

sendAssetId = getAssetId("daniele-rugani-2021-limited-525")

currentUser = gql("""
  query CurentUserQuery {
    currentUser {
      starkKey
    }
  }""")

newOfferLimitOrders = gql("""
  mutation NewOfferLimitOrders($input: prepareOfferInput!) {
    prepareOffer(input: $input) {
      limitOrders {
        amountBuy
        amountSell
        expirationTimestamp
        nonce
        tokenBuy
        tokenSell
        vaultIdBuy
        vaultIdSell
      }
      errors {
        message
      }
    }
  }
""")

createSingleSaleOffer = gql("""
  mutation CreateSingleSaleOffer($input: createSingleSaleOfferInput!) {
    createSingleSaleOffer(input: $input) {
      offer {
        id
      }
      errors {
        message
      }
    }
  }
""")


def prepareSaleOffer():
    transport = AIOHTTPTransport(
        url="https://api.sorare.com/graphql",
        headers={"JWT-AUD": "SorareDataApp",
                 "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
    )

    # Get StarKey
    currentUserData = Client(transport=transport).execute(currentUser)
    print(currentUserData)
    starkKey = currentUserData["currentUser"]["starkKey"]
    print("Your starkKey is ", starkKey)

    # Perpare the sell offer
    prepareOfferInput = {
        "type": "SINGLE_SALE_OFFER",
        "sendAssetIds": [sendAssetId],
        "receiveAssetIds": [],
        "receiveWeiAmount": 1000000000000000000,
        "sendWeiAmount": 0
    }

    # sendAssetId ricavabile da cardDialogQuerry con card_slug come input 0x04004587a379d00e78c9e95241840c269c728bc6e2b5d8eb370f8b27df25f247

    print(prepareOfferInput)

    newOfferData = Client(transport=transport).execute(newOfferLimitOrders, {"input": prepareOfferInput})
    print(newOfferData)

    prepareOffer = newOfferData["prepareOffer"]
    if len(prepareOffer["errors"]) > 0:
        for error in prepareOffer["errors"]:
            print(error["message"])
            return

    limitOrders = prepareOffer["limitOrders"]
    if not limitOrders:
        print("You need to be authenticated to get LimitOrders.")
        return

    return {
        "limitOrders": limitOrders,
        "sendAssetId": sendAssetId
    }

    print(limitOrders)

    # starkSignatures = []
    #
    # for limitOrder in limitOrders:
    #     signLimitOrder = require('@sorare/crypto')
    #
    #     starkSignatures.append({
    #         "data": json.load(signLimitOrder(privateKey, limitOrder)),
    #         "nonce": limitOrder.nonce,
    #         "expirationTimestamp": limitOrder.expirationTimestamp,
    #         "starkKey": starkKey
    #     })
    #
    # print(starkSignatures)

    # crypto = js2py.require("crypto")
    #
    # createSingleSaleOfferInput = {
    #     "starkSignatures": starkSignatures,
    #     "dealId": crypto.randomBytes(8).join(""),
    #     "assetId": sendAssetId,
    #     "clientMutationId": crypto.randomBytes(8).join("")
    # }
    #
    # print(createSingleSaleOfferInput)
    #
    # createSingleSaleOfferData = Client(transport=transport).execute(
    #     createSingleSaleOffer,
    #     {"input": createSingleSaleOfferInput}
    # )
    # print(createSingleSaleOfferData)
    #
    # createSingleSaleOffer_ = createSingleSaleOfferData["createSingleSaleOffer"]
    #
    # if createSingleSaleOffer_["errors"].length > 0:
    #     for error in createSingleSaleOffer_["errors"]:
    #         print(error["message"])
    #     return
    #
    # print("Success!")






if __name__ == '__main__':
    print(prepareSaleOffer())
