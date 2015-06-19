from datetime import datetime
import random

from auction.models import Auction, Bid
from moderation.models import RequestForModeration


def get_prices_by_advertisements(user):
    price_per_adv = {}
    for moderated_adv in RequestForModeration.objects.filter(status='AC'):
        adv = moderated_adv.content_object
        price = get_price(adv, user)
        price_per_adv[adv] = price
    return price_per_adv


def get_price(adv, user):
    return random.randint(1, 100)


def select_winner_advertisement(price_per_adv):
    return max(price_per_adv, key=price_per_adv.get)


def process_auction_results(user, price_per_adv, winner_adv):
    print('For user "' + str(user) + '", at ' + str(datetime.now()))
    auction = Auction.objects.create(target_user=user)
    for adv, price in price_per_adv.items():
        print('Price: ' + str(price) + ', adv: "' + str(adv) + '"' + ' **winner**' if (adv == winner_adv) else '')
        Bid.objects.create(auction=auction, price=price, content_object=adv, winner=(adv == winner_adv))
