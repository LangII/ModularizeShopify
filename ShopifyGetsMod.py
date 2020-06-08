
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
import json

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

    # Set time stamp arg to date of _within_days ago.
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
        # Convert orders to json format.
        for i in range(len(orders)):
            orders[i] = json.loads(orders[i].to_json().decode('utf-8'))['order']
        # Arguable print for debugging.
        if _print:
            batch_print = "\n>>> in batch {}...  retrieved {} orders...\n>>> order ids:\n{}"
            print_format = [batch_count, len(orders), ', '.join([ str(o['id']) for o in orders ])]
            print(batch_print.format(*print_format))
        # Build all_orders_, check for while loop break condition, then if loop continues set next
        # loop's previous_end_id.
        all_orders_ += orders
        if len(orders) < args['batch_size']:  break
        previous_end_id = orders[-1]['id']

    return all_orders_



def weFulfillItemsByIdType(_settings, _orders, _print=False):
    """
    input:  _settings = A Shopify settings module in a json like syntax.  This method requires
                        access to sku_pointers and product_id_pointers to verify if items in _order
                        are items we fulfill.
            _orders =    A list of Shopify Order objects containing all order information.
            _print =    Bool determining whether actions are printed to console (for debug).
    output: Return we_fulfill_ and we_do_not_fulfill_, lists of sorted orders from _orders.  To
            fulfill or not to fulfill determined based on items in orders by _id_type.
    Shopify order reference:  https://shopify.dev/docs/admin-api/rest/reference/orders/order
    """

    # Get ids_we_fulfill from _settings based on _id_type.
    product_ids_we_fulfill, skus_we_fulfill = [], []
    for key, value in _settings.part_pointers.items():
        if key == 'by_product_id':
            for pointer in value:  product_ids_we_fulfill += pointer['shop_product_ids']
        elif key == 'by_sku':
            for pointer in value:  skus_we_fulfill += pointer['shop_skus']

    # BLOCK...  Sort each order in _orders into we_fulfill_ or we_do_not_fulfill_.
    we_fulfill_, we_do_not_fulfill_ = [], []
    for order in _orders:
        if _print:  print(">>>     checking order {}...  ".format(order['id']), end='')
        found_one = False
        # Check each item in line_items to see if it's in ids_we_fulfill.
        for item in order['line_items']:
            has_product_id = item['product_id'] in product_ids_we_fulfill
            has_sku = item['sku'] in skus_we_fulfill
            if has_product_id or has_sku:
                we_fulfill_ += [order]
                found_one = True
                if _print:  print("has items we fulfill")
                break
        # If all items are checked and none are in ids_we_fulfill, add order to we_do_not_fulfill_.
        if not found_one:
            we_do_not_fulfill_ += [order]
            if _print:  print("does not have items we fulfill")

    return we_fulfill_, we_do_not_fulfill_



def getShipMethodByDefault(_settings, _order):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return ship_method_, shipping method of the _order as designated by _settings.
    """

    # Assign ship_method_ value based on default dom/int settings.
    default_pointers = _settings.ship_method_pointers['by_default']
    if _order['shipping_address']['country'] == 'United States':
        ship_method_ = default_pointers['dom']
    else:
        ship_method_ = default_pointers['int']

    return ship_method_



def customCheckSubtotalPrice(_key, _order):
    """
    input:  _key = Key from shop_settings.ship_method_pointers['by_shipping_lines'][''] dict.
            _order = A Shopify Order object containing all order information.
    output: Return (key_, use_default_).  key_ is a modified _key with && flag removed.
            use_default_ is a bool telling getShipMethod() whether or not to use the default ship
            method based on value of _order['subtotal_price'].
    """

    key_, use_default_ = '', True
    key_ = _key.replace('&check_subtotal_price&', '')
    if float(_order['subtotal_price']) > 0.00:  use_default_ = False

    return key_, use_default_



def getShipMethodByShippingLines(_ship_method, _settings, _order):
    """
    input:  _ship_method =  Previously designated ship_method to be maintained if get by condition
                            is not met.
            _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return _ship_method, shipping method of the _order as designated by _settings.
    """

    # Block...  Assign ship_method_ based on custom shipping_lines settings.
    by_shipping_lines = _settings.ship_method_pointers['by_shipping_lines']
    if _order['shipping_lines']:
        # Different settings can use different types; currently accepting 'code' and 'title'.
        for type in by_shipping_lines:
            # Loop through each pointer set in each type.
            for key, value in by_shipping_lines[type].items():
                # First if handles (michaelhyatt) custom function.
                if key.startswith('&check_subtotal_price&'):
                    key, use_default = customCheckSubtotalPrice(key, _order)
                    if use_default:  break
                # Final comparison to set ship_method_.
                if _order['shipping_lines'][0][type] == key:
                    _ship_method = value
                    break

    return _ship_method



def getShipMethodByCountry(_ship_method, _settings, _order):
    """
    input:  _ship_method =  Previously designated ship_method to be maintained if get by condition
                            is not met.
            _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
    output: Return _ship_method, shipping method of the _order as designated by _settings.
    """

    by_country = _settings.ship_method_pointers['by_country']
    for country, method in by_country.items():
        if _order['shipping_address']['country'] == country:
            _ship_method = method
            break

    return _ship_method



def getShipMethodByProvince(_ship_method, _settings, _order):
    """
    input:  _ship_method =  Previously designated ship_method to be maintained if get by condition
                            is not met.
            _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return _ship_method, shipping method of the _order as designated by _settings.
    """

    by_province = _settings.ship_method_pointers['by_province']
    for province, method in by_province.items():
        if _order['shipping_address']['province'] == province:
            _ship_method = method
            break

    return _ship_method



def getShipMethodByNameAndEmail(_ship_method, _settings, _order):
    """
    input:  _ship_method =  Previously designated ship_method to be maintained if get by condition
                            is not met.
            _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return _ship_method, shipping method of the _order as designated by _settings.
    """

    by_name_and_email = _settings.ship_method_pointers['by_name_and_email']
    for pointer in by_name_and_email:
        same_name = _order['shipping_address']['name'] == pointer['name'] if pointer['name'] else True
        same_email = _order['contact_email'] == pointer['email'] if pointer['email'] else True
        if same_name and same_email:  _ship_method = pointer['ship_method']

    return _ship_method



# def getShipMethodByParts(_ship_method, _settings, _order):
#     """
#     input:  _ship_method =
#             _settings =
#             _order =
#     output:
#     """
#
#     by_parts = _settings.ship_method_pointers['by_parts']
#
#     return _ship_method



def getShipMethod(_settings, _order):
    """
    input:  _settings = A Shopify settings module in a json like syntax.  This method requires
                        access to ship_method_pointers for ship_method_ assignment.
            _order =    A Shopify Order object containing all order information.
    output: Return ship_method_, a string representing the order's designated shipping method
            assigned by conditions from _settings and values from _order.
    """

    ship_method_ = getShipMethodByDefault(_settings, _order)

    for pointer_group in _settings.ship_method_pointers['sequence']:
        if pointer_group == 'by_default':  continue
        elif pointer_group == 'by_shipping_lines':
            ship_method_ = getShipMethodByShippingLines(ship_method_, _settings, _order)
        elif pointer_group == 'by_country':
            ship_method_ = getShipMethodByCountry(ship_method_, _settings, _order)
        elif pointer_group == 'by_province':
            ship_method_ = getShipMethodByProvince(ship_method_, _settings, _order)
        elif pointer_group == 'by_name_and_email':
            ship_method_ = getShipMethodByNameAndEmail(ship_method_, _settings, _order)
        # elif pointer_group == 'by_parts':
        #     ship_method_ = getShipMethodByParts(ship_method_, _settings, _order)


    return ship_method_



def getOtherShipInfo(_ship_info, _settings, _order):
    """
    input:  _ship_info = Previously designated ship_info, to be maintained and added to for return.
            _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _order =    A Shopify Order object containing all order information.
    output: Return _ship_info, from argued _ship_info, modifed with designations from
            _settings.ship_info_pointers.
    """

    for key, value in _settings.ship_info_pointers.items():
        # Navigate through _order json with drilldown sequence of value.
        pointing = _order
        for value_step in value:  pointing = pointing[value_step]
        # Dynamically update _ship_info.
        _ship_info[key] = pointing

    return _ship_info



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

    # Standard ship_info values retrieval.
    ship_info_['CompanyID'] =   _settings.credentials['company_id']
    ship_info_['inDate'] =      datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ship_info_['ReqBy'] =       'Shopify'
    ship_info_['Company'] =     _order['shipping_address']['company']
    ship_info_['Attn'] =        _order['shipping_address']['name'] # need to use string formatting
    ship_info_['Addy1'] =       _order['shipping_address']['address1']
    ship_info_['Addy2'] =       _order['shipping_address']['address2']
    ship_info_['City'] =        _order['shipping_address']['city']
    ship_info_['State'] =       _order['shipping_address']['province']
    ship_info_['Zip'] =         _order['shipping_address']['zip']
    ship_info_['Country'] =     _order['shipping_address']['country']
    ship_info_['Phone'] =       _order['shipping_address']['phone']
    ship_info_['Email'] =       _order['contact_email']
    # Shop specific ship_info values retrieval.
    ship_info_['ShipMethod'] =  getShipMethod(_settings, _order)
    ship_info_ = getOtherShipInfo(ship_info_, _settings, _order)

    # Convert None values to empty strings, remove specified chars, and remove non-ascii chars.
    remove_chars = '\'"[]#'
    for key in ship_info_:
        if ship_info_[key] == None:  ship_info_[key] = ''
        for char in remove_chars:  ship_info_[key] = str(ship_info_[key]).replace(char, '')
        ship_info_[key] = ship_info_[key].encode().decode('ascii', 'ignore')

    return ship_info_



def getItemsWeFulfillFromOrder(_settings, _order):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to sku_pointers an product_id_pointers for shop id to disk id
                        referencing.
            _order =    A Shopify Order object containing all order information.
    output: Return items_to_fulfill_, dict with keys as disk_part_numbers and values as quantities
            of said part numbers.  Each disk_part_number is referenced from _order by it's pointer
            in _settings and each quantity is multiplied through the pointer as well.
    Shopify order reference:  https://shopify.dev/docs/admin-api/rest/reference/orders/order
    """

    # BLOCK...  Build items_to_fulfill_, filter each item in line_items through
    # _settings.part_pointers.
    items_to_fulfill_ = {}
    for item in _order['line_items']:
        for key, value in _settings.part_pointers.items():
            # Set item_tag and pointer_tag by key of dict item in part_pointers.
            if key == 'by_product_id':  item_tag, pointer_tag = 'product_id', 'shop_product_ids'
            elif key == 'by_sku':  item_tag, pointer_tag = 'sku', 'shop_skus'
            # Loop through each pointer and compare item[item_tag] with pointer[pointer_tag] to get
            # disk_part_numbers.
            for pointer in value:
                if item[item_tag] in pointer[pointer_tag]:
                    for key, value in pointer['disk_part_numbers'].items():
                        items_to_fulfill_[key] = value * item['quantity']
                        break

    return items_to_fulfill_



def convertOrdersToDiskFormat(_settings, _orders):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials to get information for populating ship_info_.
            _orders =   A list of Shopify Order objects containing all order information.
    output: Return disk_orders_.  Take _orders (in shop format), using conditional modifications
            from _settings, alter the data into disk_orders_ (disk format) for submission.
    """

    disk_orders_ = []
    for order in _orders:
        disk_order = {}
        disk_order['ship_info'] = getShipInfoFromOrder(_settings, order)
        # disk_order['items'] = getItemsWeFulfillFromOrder(_settings, order)
        disk_orders_ += [disk_order]

        # print("\n", disk_order, "\n")
        # print("\n\n\n<><><>   ORDER   <><><>")
        # print(json.dumps(order, indent=4, sort_keys=True))
        print("\n\n\n<><><>   DISK ORDER   <><><>")
        print(json.dumps(disk_order, indent=4, sort_keys=True))
        # print(disk_order)

    return disk_orders_



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

""" OBSOLETE from getShipMethod() (2020-06-08) """

# """ possible bad """
# # # Loaded as json because Shopify shipping_line object was difficult to parse.
# # shipping_line = json.loads(_order['shipping_lines'][0].to_json().decode('utf-8'))
# # # Final comparison for ship_method_ assignment.
# # if shipping_line['shipping_line'][type] == key:
# #     ship_method_ = value
# #     break
# """ possible good (2020-06-08) """
# if _order['shipping_lines'][0][type] == key:
#     ship_method_ = value
#     break

""" OBSOLETE from weFulfillItemsByIdType() (2020-05-29) """
# # Ensure _id_type is correctly argued.
# if _id_type not in ['product_id', 'sku']:
#     type_check_exit =  "when calling weFulfillItemsByIdType(), arg _id_type only accepts "
#     type_check_exit += "'product_id' or 'sku', not '{}', please try again"
#     exit(type_check_exit.format(_id_type))
#
# if _id_type == 'sku':  pointers, pointer_tag = _settings.sku_pointers, 'shop_sku'
# else:  pointers, pointer_tag = _settings.product_id_pointers, 'shop_product_ids'
# for pointer in pointers:  ids_we_fulfill += pointer[pointer_tag]
#
#         # Set item_id based on _id_type, then see if item_id is in ids_we_fulfill.
#         item_id = item['product_id'] if _id_type == 'product_id' else item['sku']
#         if item_id in ids_we_fulfill:
#             # If so, add order to we_fulfill_, trigger found_one, and end inner for loop.
#             we_fulfill_ += [order]
#             found_one = True

""" OBSOLETE from getItemsWeFulfillFromOrder() (2020-05-29) """
# # Ensure _id_type is correctly argued.
# if _id_type not in ['product_id', 'sku']:
#     type_check_exit =  "when calling weFulfill(), arg _id_type only accepts 'product_id' or "
#     type_check_exit += "'sku', not '{}', please try again"
#     exit(type_check_exit.format(_id_type))
#
# if _id_type == 'sku':  pointers, pointer_tag = _settings.sku_pointers, 'shop_sku'
# else:  pointers, pointer_tag = _settings.product_id_pointers, 'shop_product_ids'
#
# # Get ids_we_fulfill from _settings based on _id_type.
# product_ids_we_fulfill, skus_we_fulfill = [], []
# for key, value in _settings.part_pointers.items():
#     if key == 'by_product_id':
#         for pointer in value:  product_ids_we_fulfill += pointer['shop_product_ids']
#     elif key == 'by_sku':
#         for pointer in value:  skus_we_fulfill += pointer['shop_skus']
#
# # BLOCK...  Build items_to_fulfill_, dict with keys as disk_part_numbers and values as
# # quantities.
# items_to_fulfill_ = {}
# for item in _order['line_items']:
#     # Designate item_id based on argued _id_type.
#     item_id = item['product_id'] if _id_type == 'product_id' else item['sku']
#     for pointer in pointers:
#         # The final alignment...  If predesignated item_id is in pointer from predesignated
#         # pointers (referenced with predesignated pointer_tag), then populate items_ with keys
#         # and values from 'disk_part_numbers'.
#         if item_id in pointer[pointer_tag]:
#             for key, value in pointer['disk_part_numbers'].items():
#                 # Note...  Important to multiply qty values from both sources.
#                 items_to_fulfill_[key] = value * item['quantity']
#
# for pointer in value:
#     if item['sku'] in pointer['shop_skus']:
#         for key, value in pointer['disk_part_numbers'].items():
#             items_to_fulfill_[key] = value * item['quantity']

""" OBSOLETE from weFulfillItemsByIdType() (2020-05-04) """
# # Return block...  Return True if found item_id in ids_we_fulfill, else Return False.
# for item in _order.line_items:
#     # Get item_id based on _id_type.
#     item_id = item.product_id if _id_type == 'product_id' else item.sku
#     if item_id in ids_we_fulfill:  return True
# return False

""" OBSOLETE (2020-04-15) """
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
