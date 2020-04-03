
# Fix for legacy code...  Handling of unsupported HTTPS verification.
import ssl
try:  _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:  pass
else:  ssl._create_default_https_context = _create_unverified_https_context

import shopify
import ShopifyCredentials



def getShopCredsByCompanyName(_company_name):
    """
    input:  _company_name = String of client company name.
    output: Return shop_creds_, dict of credentials needed for base shop access.
    """

    creds = ShopifyCredentials.credentials[_company_name]
    creds_dict_keys = ['api_key', 'password', 'shop_name', 'api_version']
    shop_creds_ = { key: creds[key] for key in creds_dict_keys }

    return shop_creds_



def getShop(_creds):
    """
    input:  _creds['api_key'] = ...
            _creds['password'] = ...
            _creds['shop_name'] = ...
            _creds['api_version'] = ...
    output: Return 'shop_', ...
    """

    # url_template = 'https://%s:%s@%s.myshopify.com/admin/api/%s'
    url_template = 'https://{}:{}@{}.myshopify.com/admin/api/{}'
    creds_list = [ _creds[k] for k in ['api_key', 'password', 'shop_name', 'api_version'] ]
    # print(url_template)
    # print(creds_list)
    shop_url = url_template.format(*creds_list)
    # print(shop_url)
    # exit()
    shopify.ShopifyResource.set_site(shop_url)
    shop_ = shopify.Shop.current()

    return shop_

shop_creds = getShopCredsByCompanyName('apeiron_zoh')
shop = getShop(shop_creds)
print(shop)
