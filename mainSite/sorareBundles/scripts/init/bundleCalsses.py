class Bundle:

    def __init__(self, bundle_id, image_url, buy_date, buy_price, bundle_slug, cards):
        self.bundle_id = bundle_id
        self.image_url = image_url
        self.buy_date = buy_date
        self.buy_price = buy_price
        self.bundle_slug = bundle_slug
        self.cards = cards


class Card:

    def __init__(self, card_id, bundle_id, player_name, player_rarity, is_contested, is_sold, listing_price, is_listed,
                 last_insertion_date, contesting_cards, card_slug,player_image):
        self.card_id = card_id
        self.bundle_id = bundle_id
        self.player_name = player_name
        self.player_rarity = player_rarity
        self.is_contested = is_contested
        self.is_sold = is_sold
        self.listing_price = listing_price
        self.is_listed = is_listed
        self.last_insertion_date = last_insertion_date
        self.contesting_cards = contesting_cards
        self.card_slug = card_slug
        self.player_image = player_image

class ContestingCard:

    def __init__(self, contesting_card_id, card_id, listing_price, is_sold, insertion_date):
        self.contesting_card_id = contesting_card_id
        self.card_id = card_id
        self.listing_price = listing_price
        self.is_sold = is_sold
        self.insertion_date = insertion_date


class SimpleCard:

    def __init__(self,display_name, price, card_slug, end_date, rarity,player_image):
        self.price = price
        self.card_slug = card_slug
        self.end_date = end_date
        self.rarity = rarity
        self.display_name = display_name
        self.player_image = player_image
        self.contesting_cards = []


class MarketInfo:

    def __init__(self, is_on_sale, live_sell_offer, owner_slug, buy_date, buy_price):
        self.is_on_sale = is_on_sale
        self.live_sell_offer = live_sell_offer
        self.owner_slug = owner_slug
        self.buy_date = buy_date
        self.buy_price = buy_price
