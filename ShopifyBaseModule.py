
"""

ShopifyGetsModule.py

- Modularizing Shopify carts.
- First developing series of basic frequently used methods.

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

import ShopifyCredentials
import shopify
import json
from datetime import datetime, timedelta



####################################################################################################
                                                                                 ###   METHODS   ###
                                                                                 ###################

def getShopCreds(_by):
    """
    input:  _by =   String of customer's company name or company id (will also accept int of company
                    id).
    output: Return shop_creds_, dict of client's shopify credentials needed for shop access, from
            ShopifyCredentials module.
    """

    if not _by:  exit("getShopCreds() requires string argument of company name or company id")

    # Perform general maintenance of _by and determine by_type.
    _by = str(_by).strip()
    by_type = 'id' if all([ char.isdigit() for char in _by ]) else 'name'

    # BLOCK...  Get creds by searching ShopifyCredentials.py credentials attribute.
    found_it = False
    for key, value in ShopifyCredentials.credentials.items():
        # Use by_type to determine identifier.
        identifier = key[:key.index(' ')] if by_type == 'name' else key[key.index(' ') + 1:]
        if _by == identifier:
            creds, found_it = value, True
            break
    if not found_it:
        not_found_print = "argued '{}' of type '{}' was not found in call to getShopCreds()"
        exit(not_found_print.format(_by, by_type))

    # Get specific values from creds.
    creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
    shop_creds_ = { key: creds[key] for key in creds_dict_keys }

    return shop_creds_



def openShop(_creds):
    """
    input:  _creds = Dict of credentials for accessing Shopify shop with keys of:  'api_key',
            'password', 'shop_name', and 'api_version'.
    output: Return 'shop_', Shopify object identifier.
    """

    url_template = 'https://{}:{}@{}.myshopify.com/admin/api/{}'
    creds_list = [ _creds[k] for k in ['api_key', 'password', 'shop_name', 'api_version'] ]
    shopify.ShopifyResource.set_site(url_template.format(*creds_list))
    shop_ = shopify.Shop.current()

    return shop_



def getAllShopProducts(_batch_size=20):
    """
    input:  _batch_size =   Int of size of each batch of products pulled.  This is needed for
                            pagination because Shopify's API throttling.
    output: Return all_products_, a list of all product objects returned from open Shopify shop.
    """

    previous_end_id, all_products_ = 0, []
    while True:
        # Get current batch of products based on previous_end_id and _batch_size.
        products = shopify.Product.find(since_id=previous_end_id, limit=_batch_size)
        all_products_ += products
        # If size of current batch is less than _batch_size, stop pulling products.
        if len(products) < _batch_size:  break
        previous_end_id = products[-1].id

    return all_products_



def getShopProductDetails(_product):
    """
    input:  _product = A shopify product object.
    output: Return details_, a list of product details of each variant of product.  Many products
            have only a single variant, so return a list of a single product's details.
    Shopify Product Reference = https://shopify.dev/docs/admin-api/rest/reference/products/product
    """

    details_ = []
    product_details = {
        'vendor':       _product.vendor,
        'id':           _product.id,
        'title':        _product.title,
        'handle':       _product.handle,
        'updated_at':   _product.updated_at,
    }
    for variant in _product.variants:
        variant_details = {
            'variant_id':           variant.id,
            'variant_title':        variant.title,
            'variant_barcode':      variant.barcode,
            'variant_sku':          variant.sku,
            'variant_inv_qty':      variant.inventory_quantity,
            'variant_updated_at':   variant.updated_at,
        }
        details_ += [{ **product_details, **variant_details }]

    return details_



def prettyPrintShopProducts(_products):
    """
    input:  _products = A list of Shopify product objects.
    output: Pretty print to console product details from getShopProductDetails().
    """

    product_count = 0
    for product in _products:
        for details in getShopProductDetails(product):
            product_count += 1
            print("\nproduct count:", product_count)
            print(json.dumps(details, indent=4, sort_keys=True))



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
            _print = Bool determining whether batches are printed to console (for debug).
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
            batch_print = "\nIn batch {}...  retrieved {} orders...\norder ids:  {}"
            print_format = [batch_count, len(orders), ', '.join([ str(o.id) for o in orders ])]
            print(batch_print.format(*print_format))
        # Build all_orders_, check for while loop break condition, then if loop continues set next
        # loop's previous_end_id.
        all_orders_ += orders
        if len(orders) < _batch_size:  break
        previous_end_id = orders[-1].id

    return all_orders_



####################################################################################################
                                                                                 ###   TESTING   ###
                                                                                 ###################

shop_creds = getShopCreds(1799)

shop = openShop(shop_creds)
print(shop)

keyargs = {
    'fulfillment_status': 'unfulfilled',
    'financial_status': 'paid'
}
orders = getRecentShopOrders(_print=True, _keyargs=keyargs)


# all_products = getAllShopProducts()
#
# prettyPrintShopProducts(all_products)

# details = getProductDetails(all_products[12])
# print(details)


# print(shop_creds)

# openShop(shop_creds)
# getProducts()

# print(shop)
