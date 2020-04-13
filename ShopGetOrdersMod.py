
"""

ShopifyGetOrdersMod.py

- Modularizing Shopify carts.
- Get Order methods for Shopify carts.

Resources:

https://shopify.dev/docs/admin-api/rest/reference
- rest api docs
- referenced by Parker

https://github.com/Shopify/shopify_python_api
- python shopify github repo
- referenced by Parker

"""

####################################################################################################
                                                                     ###   SYS SETUP & IMPORTS   ###
                                                                     ###############################

# Legacy fix...  Handling of unsupported HTTPS verification.
import ssl
try:  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:  pass
else:  ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime, timedelta

import shopify



####################################################################################################
                                                                                 ###   METHODS   ###
                                                                                 ###################

def getRecentShopOrders(_within_days=30, _keyargs='default', _batch_size=250, _print=False):
    """
    input:  _within_days =  Used to get date stamp of date that is X number days prior to current
                            date.  That date stamp is set as created_at_min condition.
            _keyargs =  - Dict for setting primary API request conditions of fulfillment_status and
                        financial_status.
                        - Example:
                        # This code example sets request conditions identical to 'default'.  i.e.
                        # It would have the same return as 'orders = getRecentShopOrders()'.
                        keyargs = {
                            'fulfillment_status': 'unfulfilled,unshipped,partial',
                            'financial_status': 'paid,partially_refunded'
                        }
                        orders = getRecentShopOrders(_keyargs=keyargs)
                        - For details, refer to:
                        https://shopify.dev/docs/admin-api/rest/reference/orders/order#index-2020-04
            _batch_size = Order retrieval pagination page size.
            _print = Bool determining whether actions are printed to console (for debug).
    output: Return all_orders_, list of all current shop's orders based on argued conditions.
    """

    # Set Shopify API call arguments of fulfillment_status and financial_status from _keyargs.
    if _keyargs == 'default':
        fulfillment_status_args = 'unfulfilled,unshipped,partial'
        financial_status_args = 'paid,partially_refunded'
    else:
        fulfillment_status_args = _keyargs['fulfillment_status']
        financial_status_args = _keyargs['financial_status']

    # Set time stamp arg to date _within_days ago.
    within_date = datetime.now() - timedelta(days=_within_days)

    # BLOCK...  While loop performs pagination of calls on Shopify API, in case total number of
    # orders is greater than max allowed _batch_size.
    batch_count, previous_end_id, all_orders_ = 0, 0, []
    while True:
        batch_count += 1
        orders = shopify.Order.find(
            fulfillment_status=fulfillment_status_args, financial_status=financial_status_args,
            created_at_min=within_date, since_id=previous_end_id, limit=_batch_size
        )
        # Arguable print for debugging.
        if _print:
            batch_print = "\n>>> in batch {}...  retrieved {} orders...\n>>> order ids:  {}"
            print_format = [batch_count, len(orders), ', '.join([ str(o.id) for o in orders ])]
            print(batch_print.format(*print_format))
        # Build all_orders_, check for while loop break condition, then if loop continues set next
        # loop's previous_end_id.
        all_orders_ += orders
        if len(orders) < _batch_size:  break
        previous_end_id = orders[-1].id

    return all_orders_
