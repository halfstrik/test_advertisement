from django.http import HttpResponse

from auction.utils import select_winner_advertisement, process_auction_results, get_prices_by_advertisements


def show_adv(request):
    user = request.user
    price_per_adv = get_prices_by_advertisements(user)
    adv_to_show = select_winner_advertisement(price_per_adv)
    process_auction_results(user, price_per_adv, adv_to_show)
    return HttpResponse(str(adv_to_show.short) + ' - ' + str(adv_to_show.long))
