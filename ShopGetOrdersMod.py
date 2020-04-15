
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

def getRecentShopOrders(_settings, _print=False):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to get_recent_orders_args to override default args if needed.
            _print =    Bool determining whether actions are printed to console (for debug).
    output: Return all_orders_, list of all current shop's orders based on argued conditions.
    """

    # Set default args.
    args = {
        'fulfillment_status':   'unfulfilled,unshipped,partial',
        'financial_status':     'paid,partially_refunded',
        'within_days':          30,
        'batch_size':           250,
    }
    # Override default args with values from _settings.get_recent_orders_args.
    for key, value in _settings.get_recent_orders_args.items():  args[key] = value

    # Set time stamp arg to date _within_days ago.
    within_date = datetime.now() - timedelta(days=args['within_days'])

    # BLOCK...  While loop performs pagination of calls on Shopify API, in case total number of
    # orders is greater than max allowed _batch_size.
    batch_count, previous_end_id, all_orders_ = 0, 0, []
    while True:
        batch_count += 1
        orders = shopify.Order.find(
            fulfillment_status=args['fulfillment_status'],
            financial_status=args['financial_status'],
            limit=args['batch_size'], created_at_min=within_date, since_id=previous_end_id,
        )
        # Arguable print for debugging.
        if _print:
            batch_print = "\n>>> in batch {}...  retrieved {} orders...\n>>> order ids:  {}"
            print_format = [batch_count, len(orders), ', '.join([ str(o.id) for o in orders ])]
            print(batch_print.format(*print_format))
        # Build all_orders_, check for while loop break condition, then if loop continues set next
        # loop's previous_end_id.
        all_orders_ += orders
        if len(orders) < args['batch_size']:  break
        previous_end_id = orders[-1].id

    return all_orders_



def weFulfill(_settings, _order, _id_type):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to sku_pointers and product_id_pointers to verify if items in _order
                        are items we fulfill.
            _order =    A Shopify Order object containing all order information.
            _id_type =  Accepts 'product_id' or 'sku' to designate values of pointers and
                        pointer_tag.
    output: Return True if item_id is in ids_we_fulfill, else return False.
    Shopify order reference:  https://shopify.dev/docs/admin-api/rest/reference/orders/order
    """

    # Ensure _id_type is correctly argued.
    if _id_type not in ['product_id', 'sku']:
        type_check_exit =  "when calling weFulfill(), arg _id_type only accepts 'product_id' or "
        type_check_exit += "'sku', not '{}', please try again"
        exit(type_check_exit.format(_id_type))

    # Get ids_we_fulfill from _settings based on _id_type.
    ids_we_fulfill = []
    if _id_type == 'sku':  pointers, pointer_tag = _settings.sku_pointers, 'shop_sku'
    else:  pointers, pointer_tag = _settings.product_id_pointers, 'shop_product_id'
    for pointer in pointers:  ids_we_fulfill += pointer[pointer_tag]

    # Block...  Return True if found item_id in ids_we_fulfill, else Return False.
    for item in _order.line_items:
        # Get item_id based on _id_type.
        item_id = item.product_id if _id_type == 'product_id' else item.sku
        if item_id in ids_we_fulfill:  return True
    return False



def getShipInfoFromOrder(_settings, _order):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return ship_info_, a dict containing relevant data of the _order's shipping information.
    Shopify order reference:  https://shopify.dev/docs/admin-api/rest/reference/orders/order
    """

    ship_info_keys = [
        'CompanyID', 'inDate', 'ReqBy', 'Company', 'Attn', 'Addy1', 'Addy2', 'City', 'State', 'Zip',
        'Country', 'Phone', 'ShipMethod', 'ShipNumber', 'userdefval2', 'Email'
    ]
    ship_info_ = { key: '' for key in ship_info_keys }

    ship_info_['CompanyID'] =   _settings.credentials['company_id']
    ship_info_['inDate'] =      datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ship_info_['ReqBy'] =       'Shopify'
    ship_info_['Company'] =     _order.shipping_address.company
    ship_info_['Attn'] =        _order.shipping_address.name # need to use string formatting
    ship_info_['Addy1'] =       _order.shipping_address.address1
    ship_info_['Addy2'] =       _order.shipping_address.address2
    ship_info_['City'] =        _order.shipping_address.city
    ship_info_['State'] =       _order.shipping_address.province
    ship_info_['Zip'] =         _order.shipping_address.zip
    ship_info_['Country'] =     _order.shipping_address.country
    ship_info_['Phone'] =       _order.shipping_address.phone
    ship_info_['ShipNumber'] =  _order.order_number
    ship_info_['Email'] =       _order.contact_email
    ship_info_['userdefval2'] = _order.id

    return ship_info_



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

###   OBSOLETE (2020-04-15)   ###
# def getRecentShopOrders(_within_days=30, _keyargs='default', _batch_size=250, _print=False):
    # """
    # input:  _within_days =  Used to get date stamp of date that is X number days prior to current
    #                         date.  That date stamp is set as created_at_min condition.
    #         _keyargs =  - Dict for setting primary API request conditions of fulfillment_status and
    #                     financial_status.
    #                     - Example:
    #                     # This code example sets request conditions identical to 'default'.  i.e.
    #                     # It would have the same return as 'orders = getRecentShopOrders()'.
    #                     keyargs = {
    #                         'fulfillment_status': 'unfulfilled,unshipped,partial',
    #                         'financial_status': 'paid,partially_refunded'
    #                     }
    #                     orders = getRecentShopOrders(_keyargs=keyargs)
    #                     - For details, refer to:
    #                     https://shopify.dev/docs/admin-api/rest/reference/orders/order#index-2020-04
    #         _batch_size = Order retrieval pagination page size.
    #         _print = Bool determining whether actions are printed to console (for debug).
    # output: Return all_orders_, list of all current shop's orders based on argued conditions.
    # """

    # # Set Shopify API call arguments of fulfillment_status and financial_status from _keyargs.
    # if _keyargs == 'default':
    #     fulfillment_status_args = 'unfulfilled,unshipped,partial'
    #     financial_status_args = 'paid,partially_refunded'
    # else:
    #     fulfillment_status_args = _keyargs['fulfillment_status']
    #     financial_status_args = _keyargs['financial_status']
