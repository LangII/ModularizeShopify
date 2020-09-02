
"""

ShopifyCustomMod.py

- Modularizing Shopify carts.
- Custom / client specific methods for Shopify carts.

Resources:

https://shopify.dev/docs/admin-api/rest/reference
- rest api docs
- referenced by Parker

https://github.com/Shopify/shopify_python_api
- python shopify github repo
- referenced by Parker

"""



def checkSubtotalPrice(_key, _order):
    """
    (used in getShipMethodByShippingLines() from ShopifyGetsMod.py)
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



def checkTagsForSubscription(_order):
    """
    (used in getOtherShipInfo() from ShopifyGetsMod.py)
    input:  _order = A Shopify Order object containing all order information.
    output: Return value_, a simple 'Yes' or 'No' indicating if order is a subscription or not.
    """

    value_ = 'Yes' if 'Subscription' in _order['tags'] else 'No'

    return value_
