
import sys
sys.path.insert(0, '/tomcat/python')

# import ssl
# try:  _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:  pass
# else:  ssl._create_default_https_context = _create_unverified_https_context

import ShopOtherMod as shopother
import ShopGetOrdersMod as shopgetorders

# from references.part_pointers.apeironzoh_1799_pts import product_id_pointers



def main():

    print("\n>>> getting shop settings")
    shop_settings = shopother.getShopSettings('apeironzoh')

    print("\n>>> opening shop")
    shop_creds = shopother.getShopCreds(shop_settings)
    shopother.openShop(shop_creds, _print=True)

    print("\n>>> getting all productid parts")
    all_product_ids = []
    for pointer in shop_settings.product_id_pointers:  all_product_ids += pointer['shopify_parts']

    print("\n>>> getting recent shop orders")
    keyargs = {'fulfillment_status': 'unfulfilled,partial', 'financial_status': 'paid'}
    orders = shopgetorders.getRecentShopOrders(_keyargs=keyargs, _print=True)

    for order in orders:
        for item in order.line_items:
            if item.product_id in all_product_ids:
                print("item product_id =", item.product_id, "fulfilling")
            else:
                print("item product_id =", item.product_id)

    print(all_product_ids)



main()
