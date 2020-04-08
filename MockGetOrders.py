
import sys
sys.path.insert(0, '/tomcat/python')

import ssl
try:  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:  pass
else:  ssl._create_default_https_context = _create_unverified_https_context

import shopify
import ShopifyRequestModule as shop_mod

def main():

    shop_creds = shop_mod.getShopCreds(1799)

    shop_mod.openShop(shop_creds)

    orders = getOrders()

def getOrders():

    # previous_end_id, batch_size = 0, 10
    #
    # orders = shopify.Order.find(
    #     fulfillment_status='unshipped, partial', financial_status='paid, partially_refunded',
    #     since_id=previous_end_id, limit=batch_size
    # )

    batch_size = 10

    COUNTING = 0

    previous_end_id, all_orders = 0, []
    while True:
        print("previous end id =", previous_end_id)
        # Get current batch of orders based on previous_end_id and batch_size.
        orders = shopify.Order.find(
            fulfillment_status='unshipped, partial', financial_status='paid, partially_refunded',
            since_id=previous_end_id, limit=batch_size
        )
        print(orders)
        all_orders += orders
        # If size of current batch is less than batch_size, stop pulling orders.
        if len(orders) < batch_size:  break
        previous_end_id = orders[-1].id

        COUNTING += 1
        if COUNTING >= 3:  break

    print("")
    print(all_orders)

main()
