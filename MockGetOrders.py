
import sys
sys.path.insert(0, '/tomcat/python')

# import ssl
# try:  _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:  pass
# else:  ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime
from copy import deepcopy

from ShopOtherMod import *
from ShopGetOrdersMod import *
from AllCartsMod import *



def main():

    print("\n>>> getting shop settings")
    shop_settings = getShopSettings('apeironzoh')
    print("\n>>> opening shop")
    openShop(shop_settings, _print=True)

    print("\n>>> getting recent shop orders")
    shop_orders = getRecentShopOrders(shop_settings, _print=True)
    print(">>> retrieved {} shop orders".format(len(shop_orders)))

    ###########################
    """   FILTERING   >>>   """
    ###########################

    # print("\n>>> filtering orders by userdefval2 dupecheck")
    # not_dupes, dupes = dupeCheckXmlShipUserdefval2(
    # _company_id=shop_settings.credentials['company_id'],
    # _orders=shop_orders,
    # _cart='Shopify',
    # _days_ago=0,
    # _print=True
    # )
    # print(">>>")
    # print(">>> filtered orders = {}".format(len(shop_orders)))
    # print(">>> dupes =           {}".format(len(dupes)))
    # print(">>> not dupes =       {}".format(len(not_dupes)))
    # shop_orders = deepcopy(not_dupes)

    ###########################

    print("\n>>> filtering orders by items we fulfill")
    we_fulfill, we_do_not_fulfill = weFulfillItemsByIdType(
        _settings=shop_settings,
        _orders=shop_orders,
        _id_type='product_id',
        _print=True
    )
    print(">>>")
    print(">>> filtered orders =   {}".format(len(shop_orders)))
    print(">>> we do not fulfill = {}".format(len(we_do_not_fulfill)))
    print(">>> we fulfill =        {}".format(len(we_fulfill)))
    shop_orders = deepcopy(we_fulfill)

    ###########################
    """   <<<   FILTERING   """
    ###########################

    shop_orders = shop_orders[:3]

    print("\n>>> converting orders into disk ordering format")
    ordering = getOrderingFromOrders(shop_settings, shop_orders, 'product_id')
    printAllOrderingSummary(ordering)

    print("\n>>> inserting ordering into tblXmlShipData")
    insertIntoXmlShipData(ordering, _print=True)

    exit()

    # ordering_all = []
    # for order in shop_orders:
    #     ordering = {}
    #     ordering['ship_info'] = getShipInfoFromOrder(shop_settings, order)
    #     ordering['items'] = getItemsWeFulfillFromOrder(shop_settings, order, 'product_id')
    #     ordering_all += [ordering]

    # for ordering in ordering_all:
    #     printOrderingSummary(ordering)

    # print("\n>>> {} orders to be inserted into tblXmlShipData".format(len(ordering)))
    # insertIntoXmlShipData(ordering)
    #
    # exit()

    # print("\n>>> getting data of orders we fulfill from shop orders")
    # ordering = filterOrdersBy(shop_settings, shop_orders, 'product_id', _print=True)
    # print(">>> of {} shop orders, {} have items we fulfill".format(len(shop_orders), len(ordering)))
    #
    # print("\n>>> performing userdefval2 dupecheck")
    # dupecheck_largs = [ordering, shop_settings.credentials['company_id'], 'Shopify']
    # ordering, userdefval2_dupes = dupeCheckXmlShipUserdefval2(*dupecheck_largs)
    # print(">>> found {} userdefval2 dupes".format(len(userdefval2_dupes)))
    #
    # ordering = ordering[:1]

    # print(ordering_all)
    # print("")
    # print(userdefval2_dupes)
    # print("")
    # print(len(ordering_all), len(userdefval2_dupes))
    # exit()

    # for order in orders:
    #     for item in order.line_items:
    #         if item.product_id in all_product_ids:
    #             print("item product_id =", item.product_id, "fulfilling")
    #         else:
    #             print("item product_id =", item.product_id)

    # print(all_product_ids)

main()
