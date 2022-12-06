import requests
import json
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import bcrypt
import html

def get_all_bundles():
    headers = {
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://sorare.com',
        'Referer': 'https://sorare.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.102',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Opera";v="89", "Chromium";v="103", "_Not:A-Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = '{"requests":[{"indexName":"BlockchainCard_EndingSoon","params":"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=200&analyticsTags=%5B%22TransferMarket%22%2C%22NewSignings%22%5D&filters=sport%3Afootball%20AND%20sale.primary%3Atrue%20AND%20(rarity%3Alimited%20OR%20rarity%3Arare%20OR%20rarity%3Asuper_rare%20OR%20rarity%3Aunique)&distinct=true&attributesToRetrieve=%5B%22sale%22%5D&attributesToHighlight=none&maxValuesPerFacet=10&page=0&facets=%5B%22rarity%22%2C%22sale.bundled%22%2C%22position%22%2C%22sale.price%22%2C%22active_league.display_name%22%2C%22card_edition.display_name%22%2C%22serial_number%22%2C%22team.long_name%22%2C%22season%22%2C%22player.display_name%22%2C%22player.birth_date_i%22%2C%22active_club.long_name%22%2C%22active_national_team.long_name%22%2C%22country.name_en%22%2C%22so5.last_five_so5_average_score%22%2C%22so5.last_fifteen_so5_average_score%22%5D&tagFilters=&facetFilters=%5B%5B%22sale.bundled%3Atrue%22%5D%5D"},{"indexName":"BlockchainCard_EndingSoon","params":"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&analyticsTags=%5B%22TransferMarket%22%2C%22NewSignings%22%5D&filters=sport%3Afootball%20AND%20sale.primary%3Atrue%20AND%20(rarity%3Alimited%20OR%20rarity%3Arare%20OR%20rarity%3Asuper_rare%20OR%20rarity%3Aunique)&distinct=true&attributesToRetrieve=%5B%22sale%22%5D&attributesToHighlight=%5B%5D&maxValuesPerFacet=10&page=0&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=sale.bundled"}]}'

    response = requests.post(
        'https://7z0z8pasdy-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.7.1)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(6.22.0)&x-algolia-application-id=7Z0Z8PASDY&x-algolia-api-key=4efd78ac67e55d3f6f37e7ebcd2295d8',
        headers=headers, data=data)

    json_data = json.loads(response.content)
    hits = json_data["results"][0]["hits"]
    hits_new = []
    for hit in hits:
        hits_new.append(hit["objectID"])

    # cookies = {
    #     'tracking-preferences': '{%22version%22:1%2C%22destinations%22:{%22Amazon%20S3%22:true%2C%22Amplitude%22:true%2C%22Appboy%22:true%2C%22Facebook%20Pixel%20Server%20Side%22:true%2C%22Google%20AdWords%20New%22:true%2C%22Google%20Analytics%22:true%2C%22Google%20Tag%20Manager%22:true%2C%22Hotjar%22:true%2C%22Twitter%20Ads%22:true%2C%22Visual%20Tagger%22:true}}',
    #     'csrftoken': 'tvuk0BYVrLz1VGND0yPmAIdCqfxZFttuJskhaDIii4cdRfpDZ4xsEE3EXAP98ySpuwz5P43g1s2rZA7hzjZCbQ%3D%3D',
    #     'ab.storage.userId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004': '%7B%22g%22%3A%22User%3A68541d6b-e52a-41be-96dc-d64dc8e8bacb%22%2C%22c%22%3A1661268074745%2C%22l%22%3A1661268074749%7D',
    #     'ab.storage.deviceId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004': '%7B%22g%22%3A%22d4317aae-5ad2-7b6b-9ec0-ca204e5a4714%22%2C%22c%22%3A1661268074752%2C%22l%22%3A1661268074752%7D',
    #     'SLG_G_WPT_TO': 'it',
    #     'SLG_GWPT_Show_Hide_tmp': '1',
    #     'SLG_wptGlobTipTmp': '1',
    #     'ab.storage.sessionId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004': '%7B%22g%22%3A%227a3df251-c79d-1a85-b81e-660b3b5a2e89%22%2C%22e%22%3A1661275125493%2C%22c%22%3A1661268074748%2C%22l%22%3A1661273325493%7D',
    #     '_sorare_session_id': 'ce6nzjaXVeu4gI6wlVTq35fqRqU4RCTUdxc2jMtla0564QWTpyZWi3Y7ow2u9o%2B0FfjVN2%2F0icmsTQkQghE%2F49RgeMjM0Ot9S6k6kmw%2BD1tofPlvFe6TiQ8CihTMG8JpiPSQEem26Va%2BHukSa6KSwpKKjCShwtcbR8mG%2Bi2hXdwkaFakud%2Bs6AhCqxeu848OWPnub5Dx1qjqZJEGWPaMFthyri7RnMzwEMpGgQpr4ufJk9R5F2OtBO6RKa19Zjr0gmnDJSJu4%2FaNZn7kpbK9ry4WIBHNhkJPjeGqKOELOIvf07xEE%2FcLgn0QVLwDEUtY3ERu3%2Bxb9Fcsst5fSK4pi6tSBohVvWFZHvFON1IhwMKUapXo7acMOuv%2FiSs7arQeC6FAFnmgVx4leyx9%2FUqix5tAA%2BqIxDFReZwgZapD9M5kv0NnmT08C52VjuCySvpusTUzTdpT2B1YOCPYpMkW8rTXIUSBlXH5topWW%2BjmiEJsCcYNDUizjNhmenSqvGoOQRgRSm0h5jnHYg%2FPPZl%2FVyVt%2BXXuWqYDQYx5v4OD2rcO6HQlv2jL1rjSRtrRRzC6j1RRSwvFuIfFXwa%2B6oQ%3D--PuNashC6620EeTRh--BFpqPQ2pgkLclNcZx9e5EQ%3D%3D',
    # }
    #
    # headers = {
    #     'authority': 'api.sorare.com',
    #     'accept': 'application/json',
    #     'accept-language': 'it-IT',
    #     # Already added when you pass json=
    #     # 'content-type': 'application/json',
    #     # Requests sorts cookies= alphabetically
    #     # 'cookie': 'tracking-preferences={%22version%22:1%2C%22destinations%22:{%22Amazon%20S3%22:true%2C%22Amplitude%22:true%2C%22Appboy%22:true%2C%22Facebook%20Pixel%20Server%20Side%22:true%2C%22Google%20AdWords%20New%22:true%2C%22Google%20Analytics%22:true%2C%22Google%20Tag%20Manager%22:true%2C%22Hotjar%22:true%2C%22Twitter%20Ads%22:true%2C%22Visual%20Tagger%22:true}}; csrftoken=tvuk0BYVrLz1VGND0yPmAIdCqfxZFttuJskhaDIii4cdRfpDZ4xsEE3EXAP98ySpuwz5P43g1s2rZA7hzjZCbQ%3D%3D; ab.storage.userId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004=%7B%22g%22%3A%22User%3A68541d6b-e52a-41be-96dc-d64dc8e8bacb%22%2C%22c%22%3A1661268074745%2C%22l%22%3A1661268074749%7D; ab.storage.deviceId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004=%7B%22g%22%3A%22d4317aae-5ad2-7b6b-9ec0-ca204e5a4714%22%2C%22c%22%3A1661268074752%2C%22l%22%3A1661268074752%7D; SLG_G_WPT_TO=it; SLG_GWPT_Show_Hide_tmp=1; SLG_wptGlobTipTmp=1; ab.storage.sessionId.f9062f4a-69b2-4d6b-a39c-23bc77cf4004=%7B%22g%22%3A%227a3df251-c79d-1a85-b81e-660b3b5a2e89%22%2C%22e%22%3A1661275125493%2C%22c%22%3A1661268074748%2C%22l%22%3A1661273325493%7D; _sorare_session_id=ce6nzjaXVeu4gI6wlVTq35fqRqU4RCTUdxc2jMtla0564QWTpyZWi3Y7ow2u9o%2B0FfjVN2%2F0icmsTQkQghE%2F49RgeMjM0Ot9S6k6kmw%2BD1tofPlvFe6TiQ8CihTMG8JpiPSQEem26Va%2BHukSa6KSwpKKjCShwtcbR8mG%2Bi2hXdwkaFakud%2Bs6AhCqxeu848OWPnub5Dx1qjqZJEGWPaMFthyri7RnMzwEMpGgQpr4ufJk9R5F2OtBO6RKa19Zjr0gmnDJSJu4%2FaNZn7kpbK9ry4WIBHNhkJPjeGqKOELOIvf07xEE%2FcLgn0QVLwDEUtY3ERu3%2Bxb9Fcsst5fSK4pi6tSBohVvWFZHvFON1IhwMKUapXo7acMOuv%2FiSs7arQeC6FAFnmgVx4leyx9%2FUqix5tAA%2BqIxDFReZwgZapD9M5kv0NnmT08C52VjuCySvpusTUzTdpT2B1YOCPYpMkW8rTXIUSBlXH5topWW%2BjmiEJsCcYNDUizjNhmenSqvGoOQRgRSm0h5jnHYg%2FPPZl%2FVyVt%2BXXuWqYDQYx5v4OD2rcO6HQlv2jL1rjSRtrRRzC6j1RRSwvFuIfFXwa%2B6oQ%3D--PuNashC6620EeTRh--BFpqPQ2pgkLclNcZx9e5EQ%3D%3D',
    #     'origin': 'https://sorare.com',
    #     'referer': 'https://sorare.com/market/new_signings?refinementList%5Bsale.bundled%5D%5B0%5D=true&page=1&configure%5BhitsPerPage%5D=40&configure%5BanalyticsTags%5D%5B0%5D=TransferMarket&configure%5BanalyticsTags%5D%5B1%5D=NewSignings&configure%5Bfilters%5D=sport%3Afootball%20AND%20sale.primary%3Atrue%20AND%20%28rarity%3Alimited%20OR%20rarity%3Arare%20OR%20rarity%3Asuper_rare%20OR%20rarity%3Aunique%29&configure%5Bdistinct%5D=true&configure%5BattributesToRetrieve%5D%5B0%5D=sale&configure%5BattributesToHighlight%5D=none',
    #     'sec-ch-ua': '"Opera";v="89", "Chromium";v="103", "_Not:A-Brand";v="24"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-site',
    #     'sorare-build': '24a65dcbe4bbf338dbfd0aae4d48888106267331',
    #     'sorare-client': 'Web',
    #     'sorare-version': '20220823141254',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.102',
    #     'x-csrf-token': 'tvuk0BYVrLz1VGND0yPmAIdCqfxZFttuJskhaDIii4cdRfpDZ4xsEE3EXAP98ySpuwz5P43g1s2rZA7hzjZCbQ',
    # }
    #
    # json_data = {
    #     'operationName': 'CardsQuery',
    #     'variables': {
    #         'singleCardSlugs': [],
    #         'bundledCardSlugs': hits_new,
    #     },
    #     'extensions': {
    #         'operationId': 'React/808ef61ca2f35874793080cd8b712a8150f1f81afb62d2462086a1deaa5013ee',
    #     },
    # }
    #
    # response = requests.post('https://api.sorare.com/graphql', cookies=cookies, headers=headers, json=json_data)
    #
    #
    # bundled_auctions = json.loads(response.content)["data"]["transferMarket"]["bundledAuctionsWithCards"]

    transport = AIOHTTPTransport(
        url="https://api.sorare.com/graphql",
        headers={"JWT-AUD": "SorareDataApp",
                 "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2ODU0MWQ2Yi1lNTJhLTQxYmUtOTZkYy1kNjRkYzhlOGJhY2IiLCJzY3AiOiJ1c2VyIiwiYXVkIjoiU29yYXJlRGF0YUFwcCIsImlhdCI6MTY2MTM3NTU3MywiZXhwIjoiMTY5MjkzMjUyNSIsImp0aSI6IjhjMGFjYzQ3LWFjZjgtNDcyNS1hOTVmLTI4MmZkOWIyZWU2ZiJ9.9tQdrYJPnJqGXEVi1MsV8ROp5D7JohQseIiBcxWP1RY"}
    )

    query = gql(
        """
            query{
              transferMarket{
                bundledAuctionsWithCards(slugs:""" + str(json.dumps(hits_new)) + """){
                    endDate
                      minNextBid
                        slug
                      currentPrice
                        cards{
                        slug
                        player{
                          slug
                          displayName
                        }
                        rarity
                        team {
                          ... on Club{
                            pictureUrl
                          }
                        }
                      }
                }
              }
            }
    """
    )

    result = Client(transport=transport).execute(query)

    bundled_auctions = result["transferMarket"]["bundledAuctionsWithCards"]

    bundled_auctions_prettify = []

    for bundled_auction in bundled_auctions:
        endDate = bundled_auction["endDate"]
        currentPrice = bundled_auction["currentPrice"]
        minNextBid = bundled_auction["minNextBid"]
        slug = bundled_auction["slug"]
        cards = bundled_auction["cards"]
        en_cards = []
        emblem = ""
        for card in cards:
            en_cards.append({
                "cardSlug": card["slug"],
                "playerSlug": card["player"]["slug"],
                "displayName": card["player"]["displayName"],
                "rarity": card["rarity"]
            })
            emblem = card["team"]["pictureUrl"]
        bundled_auctions_prettify.append({
            "endDate": endDate,
            "slug": slug,
            "currentPrice": currentPrice,
            "minNextBid": minNextBid,
            "cards": en_cards,
            "emblem": emblem
        })

    return json.dumps(bundled_auctions_prettify)


if __name__ == '__main__':
    pass
