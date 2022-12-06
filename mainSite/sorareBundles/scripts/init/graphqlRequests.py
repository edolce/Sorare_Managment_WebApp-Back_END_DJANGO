import json

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from sorareBundles.scripts.init.bundleCalsses import Bundle, SimpleCard, MarketInfo


def getOwnedBundlesAndSoldCardsFromSorare():
    cursor0 = ""
    cursor1 = ""
    hasNextPage0 = True
    hasNextPage1 = True
    cardsSold = []
    ownedBundles = []
    while hasNextPage0 or hasNextPage1:
        transport = AIOHTTPTransport(
            url="https://api.sorare.com/graphql",
            headers={"JWT-AUD": "SorareDataApp",
                     "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
        )

        query = gql(
            """
            query {
              user(slug: "betking-instead-of-outbidding-me-message-me") {
                soldSingleSaleOffers (after: \"""" + cursor0 + """\") {
                    pageInfo {
                                    endCursor
                                    hasNextPage
                                    hasPreviousPage
                                    startCursor
                                  }
                  nodes {
                    endDate
                    price
                    card {
                      slug
                      player {
                        pictureUrl
                      }
                    }
                  }
                }

                wonEnglishAuctions(after: \"""" + cursor1 + """\") {
                    pageInfo {
                                    endCursor
                                    hasNextPage
                                    hasPreviousPage
                                    startCursor
                                  }
                  nodes {
                    endDate
                    slug
                    currentPrice
                    cards {
                      slug
                      player {
                        slug
                        displayName
                        pictureUrl
                      }
                      team {
                        ... on Club {
                          pictureUrl
                        }
                      }
                      rarity
                    }
                  }
                }
              }
            }


                    """
        )

        result = Client(transport=transport).execute(query)

        if hasNextPage0:
            cursor0 = result["user"]["soldSingleSaleOffers"]["pageInfo"]["endCursor"]
            hasNextPage0 = result["user"]["soldSingleSaleOffers"]["pageInfo"]["hasNextPage"]

            for card in result["user"]["soldSingleSaleOffers"]["nodes"]:
                cardsSold.append(
                    SimpleCard(price=card["price"], card_slug=card["card"]["slug"], end_date=card["endDate"],
                               rarity=None,display_name=None,player_image=card["card"]["player"]["pictureUrl"]))

        if hasNextPage1:
            cursor1 = result["user"]["wonEnglishAuctions"]["pageInfo"]["endCursor"]
            hasNextPage1 = result["user"]["wonEnglishAuctions"]["pageInfo"]["hasNextPage"]

            for bundle in result["user"]["wonEnglishAuctions"]["nodes"]:
                bundleToAdd = Bundle(bundle_id=None, image_url=bundle["cards"][0]["team"]["pictureUrl"],
                                     bundle_slug=bundle["slug"], buy_price=bundle["currentPrice"],
                                     buy_date=bundle["endDate"], cards=[])

                for card in bundle["cards"]:
                    bundleToAdd.cards.append(
                        SimpleCard(player_image=card["player"]["pictureUrl"],price=None, card_slug=card["slug"], end_date=0, rarity=card["rarity"],display_name=card["player"]["displayName"]))

                ownedBundles.append(bundleToAdd)

            pass

    return {
        "ownedBundles": ownedBundles,
        "soldCards": cardsSold
    }


def getMarketInfoForCardsFromSorare(slugs):
    transport = AIOHTTPTransport(
        url="https://api.sorare.com/graphql",
        headers={"JWT-AUD": "SorareDataApp",
                 "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
    )

    query = gql(
        """
        query{
          allCards(slugs:""" + str(json.dumps(slugs)) + """){
            nodes{
            slug
            onSale
            liveSingleSaleOffer{
              price
              createdAt
              endDate
              sender{
                  ... on User{
                    slug
                }
              }
            }
            ownerWithRates{
            from
            price
              account{
                owner{
                  ... on User{
                    slug
                  }
                }
              }
            }
          }
          }
        }
        """
    )

    data = Client(transport=transport).execute(query)

    feedbackData = {}

    for saleOffer in data["allCards"]["nodes"]:

        if not saleOffer["onSale"]:
            print(saleOffer)
            feedbackData[saleOffer["slug"]] = MarketInfo(
                is_on_sale=saleOffer["onSale"],
                live_sell_offer=None,
                owner_slug=saleOffer["ownerWithRates"]["account"]["owner"]["slug"],
                buy_date=saleOffer["ownerWithRates"]["from"],
                buy_price=saleOffer["ownerWithRates"]["price"]

            )
        else:
            feedbackData[saleOffer["slug"]] = MarketInfo(
                is_on_sale=saleOffer["onSale"],
                live_sell_offer={
                    "sell_price": saleOffer["liveSingleSaleOffer"]["price"],
                    "sell_start_date": saleOffer["liveSingleSaleOffer"]["createdAt"],
                    "sell_end_date": saleOffer["liveSingleSaleOffer"]["endDate"],
                },
                owner_slug=saleOffer["ownerWithRates"]["account"]["owner"]["slug"],
                buy_date=saleOffer["ownerWithRates"]["from"],
                buy_price=saleOffer["ownerWithRates"]["price"]

            )

    return feedbackData
