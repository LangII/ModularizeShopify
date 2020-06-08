
"""

ShopifyOtherMod.py

- Modularizing Shopify carts.
- General / Standard methods for Shopify carts.

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

import os
import importlib.util
import json
from datetime import datetime, timedelta

import shopify

###   OBSOLETE (2020-04-13)   ###
# from carts_settings.Credentials import all_credentials



####################################################################################################
                                                                                 ###   METHODS   ###
                                                                                 ###################

def getShopSettings(_company_name):
    """
    input:  _company_name = String of company name in naming format (excluding '_shop_settings.py')
                            from the company's corresponding file name in the Shopify module
                            shops_settings directory.
    output: Return shop_settings_, a module containing designated data for processing company's
            Shopify orders.
    """

    # Build needed directory and file strings, then use importlib.util to programmatically access
    # directory and import module based on string designation of file name.
    file_path = '{}/shops_settings/{}_shopify_settings.py'.format(os.getcwd(), _company_name)
    file_name = '{}_shopify_settings'.format(_company_name)
    spec = importlib.util.spec_from_file_location(file_name, file_path)
    shop_settings_ = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shop_settings_)

    return shop_settings_



def openShop(_settings, _print=False):
    """
    input:  _settings = A Shopify settings module in a json similar syntax.  This method requires
                        access to credentials for the Shopify API call.
            _print =    Bool determining whether actions are printed to console (for debug).
    output: Return 'shop_', Shopify object identifier.
    """

    # Get shop_creds from _settings.
    creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
    shop_creds = { key: _settings.credentials[key] for key in creds_dict_keys }

    # Call to Shopify to get access to 'shop_name' with shop_creds.
    url_template = 'https://{}:{}@{}.myshopify.com/admin/api/{}'
    creds_list = [ shop_creds[k] for k in ['api_key', 'password', 'shop_name', 'api_version'] ]
    shopify.ShopifyResource.set_site(url_template.format(*creds_list))
    shop_ = shopify.Shop.current()
    if _print:  print("\n>>> you now have API access to the *{}* Shopify shop".format(shop_.name))

    return shop_



def getAllShopProducts(_batch_size=250):
    """
    input:  _batch_size =   Int of size of each batch of products pulled.  This is needed for
                            pagination due to Shopify's API throttling.
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
    Shopify Product reference:  https://shopify.dev/docs/admin-api/rest/reference/products/product
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



def prettyPrintShopOrder(_shop_order):
    """ Quick indented json print. """

    print(json.dumps(_shop_order, sort_keys=True, indent=4))



####################################################################################################
                                                                                 ###   TESTING   ###
                                                                                 ###################

# shop_settings = getShopSettings('apeironzoh')
# shop_creds = getShopCreds(shop_settings)
# openShop(shop_creds)
#
# products = getAllShopProducts()
# prettyPrintShopProducts(products)



####################################################################################################
                                                                                ###   OBSOLETE   ###
                                                                                ####################

###   OBSOLETE (2020-04-16)   ###
# def getShopCreds(_settings):
#     """
#     input:
#     output:
#     """
#
#     # shop_settings = getShopSettings(_company_name)
#
#     # Get specific values from credentials.
#     creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
#     shop_creds_ = { key: _settings.credentials[key] for key in creds_dict_keys }
#
#     return shop_creds_



###   OBSOLETE (2020-04-13)   ###
# def getShopCreds(_by):
#     """
#     input:  _by =   String of customer's company name or company id (will also accept int of company
#                     id).
#     output: Return shop_creds_, dict of client's shopify credentials needed for shop access, from
#             ShopifyCredentials module.
#     """
#
#     # global all_credentials
#
#     if not _by:  exit("getShopCreds() requires string argument of company name or company id")
#
#     # Perform general maintenance of _by and determine by_type.
#     _by = str(_by).strip()
#     by_type = 'id' if all([ char.isdigit() for char in _by ]) else 'name'
#
#     # BLOCK...  Get creds by searching ShopifyCredentials.py credentials attribute.
#     found_it = False
#     for key, value in all_credentials.items():
#         # Use by_type to determine identifier.
#         identifier = key[:key.index('_')] if by_type == 'name' else key[key.index('_') + 1:]
#         if _by == identifier:
#             creds, found_it = value, True
#             break
#     if not found_it:
#         not_found_print = "argued '{}' of type '{}' was not found in call to getShopCreds()"
#         exit(not_found_print.format(_by, by_type))
#
#     # Get specific values from creds.
#     creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
#     shop_creds_ = { key: creds[key] for key in creds_dict_keys }
#
#     return shop_creds_
