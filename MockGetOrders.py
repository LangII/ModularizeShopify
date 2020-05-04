
import sys
sys.path.insert(0, '/tomcat/python')

# import ssl
# try:  _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:  pass
# else:  ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime

from Required.DupeChecker import xmlDupeCheckSpecialuserdefval2

from ShopOtherMod import (
    getShopSettings, openShop
)
from ShopGetOrdersMod import (
    getRecentShopOrders, weFulfillItemsByIdType
    # getOrderingFromShopOrders
)
from AllCartsMod import (
    dupeCheckXmlShipUserdefval2, insertIntoXmlShipData
)



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



    print("\n>>> filtering orders by items we fulfill")

    wefulfill_largs = [shop_settings, shop_orders, 'product_id', True]
    we_fulfill, we_do_not_fulfill = weFulfillItemsByIdType(*wefulfill_largs)

    print("\n>>> filtered out {} orders of items we do not fulfill".format(len(we_do_not_fulfill)))



    print("\n>>> filtering orders by userdefval2 dupecheck")

    dupecheck_largs = [shop_settings.credentials['company_id'], we_fulfill, 'Shopify',  0, True]
    not_dupes, dupes = dupeCheckXmlShipUserdefval2(*dupecheck_largs)

    print("\n>>> filtered out {} orders that are userdefval2 dupes".format(len(dupes)))



    exit()

    ###########################
    """   <<<   FILTERING   """
    ###########################


    print("\n>>> {} orders to be inserted into tblXmlShipData".format(len(ordering)))
    insertIntoXmlShipData(ordering)

    exit()

    # print("\n>>> getting data of orders we fulfill from shop orders")
    # ordering = filterOrdersBy(shop_settings, shop_orders, 'product_id', _print=True)
    # print(">>> of {} shop orders, {} have items we fulfill".format(len(shop_orders), len(ordering)))

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
