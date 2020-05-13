
import sys
sys.path.insert(0, '/tomcat/python')

import ssl
try:  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:  pass
else:  ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime
from copy import deepcopy

import ShopifyOtherMod as shop_other
import ShopifyGetsMod as shop_gets
import AllCartsMod as all_carts



def main():

    ###########################

    start_time = datetime.now()

    print("\n>>> getting shop settings")
    shop_settings = shop_other.getShopSettings('apeironzoh')

    print("\n>>> opening shop")
    shop_other.openShop(shop_settings, _print=True)

    ###########################

    print("\n>>> getting recent shop orders")
    shop_orders = shop_gets.getRecentShopOrders(shop_settings, _print=True)
    print(">>> retrieved {} shop orders".format(len(shop_orders)))

    if not shop_orders:  exit("\n>>> no orders to fulfill, goodbye")

    ###########################
    """   FILTERING   >>>   """
    ###########################

    filtered_out = {}

    # print("\n>>> filtering orders by userdefval2 dupecheck")
    # not_dupes, dupes = all_carts.dupeCheckXmlShipUserdefval2(
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
    # filtered_out['dupes'] = dupes

    ###########################

    print("\n>>> filtering orders by items we fulfill")
    we_fulfill, we_do_not_fulfill = shop_gets.weFulfillItemsByIdType(
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
    filtered_out['we_do_not_fulfill'] = we_do_not_fulfill

    ###########################
    """   <<<   FILTERING   """
    ###########################

    if not shop_orders:  exit("\n>>> after filtering, no orders to fulfill, goodbye")

    print("\n>>> converting orders into disk format")
    disk_orders = shop_gets.convertOrdersToDiskFormat(shop_settings, shop_orders, 'product_id')

    disk_orders = all_carts.makeAllTest(disk_orders, 3) # TESTING
    all_carts.printDiskOrdersSummary(disk_orders)

    print("\n>>> inserting disk orders into tblXmlShipData")
    all_carts.insertIntoXmlShipData(disk_orders, _print=True)

    # printGetOrdersSummary(disk_orders, filtered_out)

    print("\n>>> now exiting {}, goodbye".format(sys.argv[0][sys.argv[0].rfind('\\') + 1:]))
    print(">>> runtime = {}".format(str(datetime.now() - start_time)))



############
main()   ###
############
