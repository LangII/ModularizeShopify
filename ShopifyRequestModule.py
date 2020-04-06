
"""

ShopifyRequestModule.py

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



####################################################################################################
                                                                                 ###   METHODS   ###
                                                                                 ###################

def getShopCredsByCompanyName(_company_name):
    """
    input:  _company_name = String of client's company name.
    output: Return shop_creds_, dict of client's shopify credentials needed for shop access, from
            ShopifyCredentials module.
    """

    found_it = False
    for key, value in ShopifyCredentials.credentials.items():
        if _company_name == key[:key.index(' ')]:
            creds, found_it = value, True
            break
    if not found_it:
        exit("argued _company_name ({}) was not found in ShopifyCredentials".format(_company_name))

    creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
    shop_creds_ = { key: creds[key] for key in creds_dict_keys }

    return shop_creds_



def getShopCredsByCompanyId(_company_id):
    """
    input:  _company_id = String of client's company id.
    output: Return shop_creds_, dict of client's shopify credentials needed for shop access, from
            ShopifyCredentials module.
    """

    found_it = False
    for key, value in ShopifyCredentials.credentials.items():
        if str(_company_id) == key[key.index(' ') + 1:]:
            creds, found_it = value, True
            break
    if not found_it:
        exit("argued _company_id ({}) was not found in ShopifyCredentials".format(_company_id))

    creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
    shop_creds_ = { key: creds[key] for key in creds_dict_keys }

    return shop_creds_



def openShop(_creds):
    """
    input:  _creds = Dict of credentials for accessing Shopify shop with keys of:  'api_key',
            'password', 'shop_name', and 'api_version'.
    output: Return 'shop_', Shopify access object.
    """

    url_template = 'https://{}:{}@{}.myshopify.com/admin/api/{}'
    creds_list = [ _creds[k] for k in ['api_key', 'password', 'shop_name', 'api_version'] ]
    shop_url = url_template.format(*creds_list)
    shopify.ShopifyResource.set_site(shop_url)
    shop_ = shopify.Shop.current()

    return shop_



def getProducts():

    # print(shopify.Product.count())

    previous_id, max_get_qty, all_products = 0, 10, []
    while True:
        print("pass", previous_id)
        products = shopify.Product.find(since_id=previous_id, limit=max_get_qty)
        print(len(products))
        all_products += products
        if len(products) < max_get_qty:  break
        previous_id = products[-1].id

    print(len(all_products))




####################################################################################################
                                                                                 ###   TESTING   ###
                                                                                 ###################

shop_creds = getShopCredsByCompanyName('michael_hyatt_and_company')
# shop_creds = getShopCredsByCompanyId('1799')

openShop(shop_creds)
getProducts()

# print(shop)
