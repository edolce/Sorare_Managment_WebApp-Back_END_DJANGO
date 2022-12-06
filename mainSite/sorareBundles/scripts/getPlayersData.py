import json

import cloudscraper
import requests
import pytz
from datetime import datetime
from datetime import datetime, timedelta

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


def getPlayersData(names):
    fallback_data = {}
    i=0
    for name in names:
        # Get ID of sorare DATA from name

        scraper = cloudscraper.create_scraper(disableCloudflareV1=True)  # returns a CloudScraper instance
        # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
        data = json.loads(
            scraper.get("https://www.soraredata.com/apiv2/search/autocomplete?query=" + name.replace("-", " ")).text)
        #
        # print("NAME\n" + str(name))
        # print("DATA\n" + str(data))

        id = data["player"][0]["item_id"]

        test = scraper.get('https://www.soraredata.com/apiv2/players/info/' + id)

        print("Fetching [%s,%s]" % (i,len(names)))

        data2 = json.loads(test.text)

        # response = requests.get('https://www.soraredata.com/apiv2/search/autocomplete', params=params, headers=headers)
        # id = response.json()["player"][0]["item_id"]
        # print(id)
        # Get all auctions data

        auction_data = data2["supply_and_averages"][0]["average"]
        fallback_data[name] = {
            "3_days": auction_data[0]["Average"],
            "7_days": auction_data[1]["Average"],
            "14_days": auction_data[2]["Average"],
            "30_days": auction_data[3]["Average"],
            "best_market_price": data2["best_market_prices"]["limited_best_price"]["Price"],
            "player_image": data2["player"]["TrimmedPictureUrl"],
            "player_id": id
        }
        i += 1
        # Get all auctions for the card

    return fallback_data


def getExtraPlayerData(players_slug):
    fallbackData = {}

    for p_slug in players_slug:
        cards = []
        cursor = ""
        hasNextPage = True
        while hasNextPage:
            transport = AIOHTTPTransport(
                url="https://api.sorare.com/graphql",
                headers={"JWT-AUD": "SorareDataApp",
                         "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
            )

            query = gql(
                """
                    query {
                      player(slug: \"""" + p_slug + """\") {
                        cards(
                          rarities: [limited]
                          after: \"""" + cursor + """\"
                        ) {
                          pageInfo {
                            endCursor
                            hasNextPage
                            hasPreviousPage
                            startCursor
                          }
                          nodes {
                            slug
                            notContractOwners {
                              price
                              from        
                              transferType
                            }
                          }
                        }
                      }
                    }
                """
            )

            result = Client(transport=transport).execute(query)
            cursor = result["player"]["cards"]["pageInfo"]["endCursor"]
            hasNextPage = result["player"]["cards"]["pageInfo"]["hasNextPage"]
            cards += result["player"]["cards"]["nodes"]

        # RIORDINARE I DATI IN ORDINE CRONOLOGICO ASCENDENTE
        transactions = []
        for card in cards:
            for transaction in card["notContractOwners"]:
                transaction["slug"] = card["slug"]
                transactions.append(transaction)

        transactions.sort(key=takeDate,reverse=True)
        fallbackData[p_slug] = transactions

    return fallbackData


def takeDate(elem):
    element = datetime.strptime(elem["from"], "%Y-%m-%dT%H:%M:%SZ")
    timestamp = datetime.timestamp(element)
    return timestamp
# def getExtraPlayerData(players_id):
#     fallbackData = {}
#     for player_id in players_id:
#         scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
#         # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
#
#         # headers = {
#         #     "content-type": "application/json"
#         # }
#         # json_data = {
#         #     # "player_id": player_id,
#         #     "player_id": "77707760391596557921096752431889753634827807417738453742111889379634886865454",
#         #     "scarcity": "LIMITED",
#         #     #"end_date": datetime.utcnow().replace(tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.304Z"),
#         #     #"start_date": (datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.304Z"),
#         #     "start_date": "2022-08-01T20:35:33.304Z",
#         #     "end_date": "2022-08-31T20:35:33.304Z",
#         #     "currency": "eth",
#         #     "sorare_slug": "betking-instead-of-outbidding-me-message-me",
#         #     "expired": True,
#         #     "seasons": [],
#         #     "positions": []
#         # }
#
#         cookies = {
#             'SLG_G_WPT_TO': 'it',
#             'SLG_GWPT_Show_Hide_tmp': '1',
#             'SLG_wptGlobTipTmp': '1',
#             'cookiehub': 'eyJhbnN3ZXJlZCI6dHJ1ZSwicHJlY29uc2VudCI6ZmFsc2UsInJldmlzaW9uIjoxLCJkbnQiOmZhbHNlLCJhbGxvd1NhbGUiOnRydWUsImltcGxpY3QiOmZhbHNlLCJyZWdpb24iOiIiLCJ0b2tlbiI6ImdaQW9JTTNjTkxldURodmg2V3o3SnhqSmpVUVV4aTlhaHBwWkxCQ1ZlUWQya0tIRk4zWUhUUmNJMEx2Zk16YXMiLCJ0aW1lc3RhbXAiOiIyMDIyLTA4LTI4VDIyOjE3OjU5LjQxN1oiLCJjYXRlZ29yaWVzIjpbeyJjaWQiOjEsImlkIjoibmVjZXNzYXJ5IiwidmFsdWUiOnRydWUsInByZWNvbnNlbnQiOnRydWUsImZpcmVkIjp0cnVlfSx7ImNpZCI6MiwiaWQiOiJwcmVmZXJlbmNlcyIsInZhbHVlIjp0cnVlLCJwcmVjb25zZW50IjpmYWxzZSwiZmlyZWQiOmZhbHNlfSx7ImNpZCI6MywiaWQiOiJhbmFseXRpY3MiLCJ2YWx1ZSI6dHJ1ZSwicHJlY29uc2VudCI6ZmFsc2UsImZpcmVkIjpmYWxzZX1dfQ==',
#             'sd-refresh-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjcxNTc3ODYsImp0aSI6IjUzNzZiMDk4LTM1YzAtNDc2My1iZDdhLWExZDgxYzVjYTA2NiIsImlhdCI6MTY2MTk3Mzc4NiwiaXNzIjoiU29yYXJlRGF0YSIsInN1YiI6IlVzZXI6Njg1NDFkNmItZTUyYS00MWJlLTk2ZGMtZDY0ZGM4ZThiYWNiIn0.V2IYfUimz2-sR2vL8bYarNqoJyPUxbmEjalGtcNdVuI',
#             'sd-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjE5ODA5ODYsImp0aSI6IjUzNzZiMDk4LTM1YzAtNDc2My1iZDdhLWExZDgxYzVjYTA2NiIsImlhdCI6MTY2MTk3Mzc4NiwiaXNzIjoiU29yYXJlRGF0YSIsInN1YiI6IlVzZXI6Njg1NDFkNmItZTUyYS00MWJlLTk2ZGMtZDY0ZGM4ZThiYWNiIn0.N8STKACic4AUmSLep_1INdYKKktT57lHKUjTSzy0ROc',
#             '__cf_bm': '0gEV9r5JVw_E63kOG7vS7CoaEFySTplH4KZFlfz2Q3k-1661978120-0-AbVZ3F8qUMg33ShdHvIjYj6m32zva9+XEvcMtfJEVRdvbrE5xAUyjogCQ/SGBFSd9F/WVHv3upJ3Wk+eTT2VWKzmxc9/NaXlAR6DGRV/hV8Q9cp67mxXrwo+hi6aF1rIjg==',
#         }
#
#         from fake_useragent import UserAgent
#         ua = UserAgent()
#         headers = {
#             'authority': 'www.soraredata.com',
#             'accept': 'application/json, text/plain, */*',
#             'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
#             'origin': 'https://www.soraredata.com',
#             'referer': 'https://www.soraredata.com/player/77707760391596557921096752431889753634827807417738453742111889379634886865454',
#             'sec-ch-ua': '"Opera";v="89", "Chromium";v="103", "_Not:A-Brand";v="24"',
#             'sec-ch-ua-mobile': '?0',
#             'sec-ch-ua-platform': '"Windows"',
#             'sec-fetch-dest': 'empty',
#             'sec-fetch-mode': 'cors',
#             'sec-fetch-site': 'same-origin',
#             'User-Agent': f"{ua.random}",
#             'x-sd-auth-version': 'v2',
#         }
#
#         json_data = {
#             'player_id': '77707760391596557921096752431889753634827807417738453742111889379634886865454',
#             'scarcity': 'LIMITED',
#             'start_date': '2022-03-27T21:01:11.000Z',
#             'end_date': '2022-08-31T21:01:11.213Z',
#             'currency': 'eth',
#             'sorare_slug': 'betking-instead-of-outbidding-me-message-me',
#             'expired': False,
#             'seasons': [],
#             'positions': [],
#         }
#
#         import cfscrape
#         s = cfscrape.create_scraper()
#         k = s.post("https://www.soraredata.com/apiv2/players/price-graph-chart", data=json_data,headers=headers,cookies=cookies)
#         print(k.text)
#
#         data = json.loads(scraper.post("https://www.soraredata.com/apiv2/players/price-graph-chart", data=json_data, headers=headers, cookies=cookies).text)
#
#         print("PLAYER ID\n"+player_id)
#         print("DATA\n"+str(data))
#         print("PAYLOAD\n"+json.dumps(json_data))
#
#         fallbackData[player_id] = data["prices"]
#
#     return fallbackData
