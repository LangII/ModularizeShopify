
import sys
sys.path.insert(0, '/tomcat/python')

import ssl
try:  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:  pass
else:  ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime
from copy import deepcopy

from ShopifyOtherMod import *
from ShopifyGetsMod import *
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
    #     _company_id=shop_settings.credentials['company_id'],
    #     _orders=shop_orders,
    #     _cart='Shopify',
    #     _days_ago=0,
    #     _print=True
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



    print("\n>>> converting orders into disk ordering format")
    ordering = getOrderingFromOrders(shop_settings, shop_orders, 'product_id')
    printAllOrderingSummary(ordering)

    # MODIFY FOR TESTING
    ordering = makeAllTest(ordering, 3)

    print("\n>>> inserting 'ordering' into tblXmlShipData")
    insertIntoXmlShipData(ordering, _print=True)

    print("MADE IT")
    exit()



############
main()   ###
############
