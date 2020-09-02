
"""

ShopifyCartCustomsExt.py

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

from Required import Connections

conn = Connections.connect()
cur = conn.cursor(buffered=True)



####################################################################################################



class ShopifyCartCustomsExt:



    def checkSubtotalPrice(self, _key, _order):
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



    def checkTagsForSubscription(self, _order):
        """
        (used in getOtherShipInfo() from ShopifyGetsMod.py)
        input:  _order = A Shopify Order object containing all order information.
        output: Return value_, a simple 'Yes' or 'No' indicating if order is a subscription or not.
        """
        value_ = 'Yes' if 'Subscription' in _order['tags'] else 'No'
        return value_



    def isHyattSubscription(self, _order):
        """ If a Michael Hyatt order is designated as a subscription, query tblSubTracker to
        determine which color planner in series customer receives. Update tblSubTracker for next
        order in subscription. """
        disk_part_number_ = ''
        # See if _order email is in tblSubTracker.
        get_query = """SELECT ID, SubsShipped FROM tblSubTracker WHERE {} = '{}'"""
        cur.execute(get_query.format('Email', _order['contact_email']))
        results = cur.fetchone()
        if not results:
            # If _order email is not in tblSubTracker, see if _order name is in tblSubTracker.
            cur.execute(get_query.format('Attention', _order['shipping_address']['name']))
            results = cur.fetchone()
            # If both _order email and _order name are not in tblSubTracker, treat as new subscription.
            if not results:
                disk_part_number_ = '9781733970112bx' # olive
                set_query = """INSERT INTO tblSubTracker ({}) VALUES ('{}', '{}', '{}', '{}', '{}')"""
                format_largs = [
                    'CompanyID, Attention, Email, ShippingNumber, SubsShipped',
                    self.settings.credentials['company_id'], _order['shipping_address']['name'],
                    _order['contact_email'], _order['name'], 1
                ]
                set_query = set_query.format(*format_largs)
        # If _order email or _order name in tblSubTracker, treat as old subscription.
        if results:
            subs_id, subs_shipped = results
            if   subs_shipped == 1:  disk_part_number_ = '9781733970105bx' # eggplant
            elif subs_shipped == 2:  disk_part_number_ = '9781732189676bx' # poppy
            elif subs_shipped == 3:  disk_part_number_ = '9781732189683bx' # french blue
            elif subs_shipped == 4:  disk_part_number_ = '9781733970112bx' # olive
            # Increment SubsShipped, return to 1 if currently 4.
            subs_shipped_update = subs_shipped + 1 if subs_shipped != 4 else 1
            set_query = """UPDATE tblSubTracker SET SubsShipped = {} WHERE ID = {}"""
            set_query = set_query.format(subs_shipped_update, subs_id)
        # Populate subscription_update_queries to update table at end of script.
        self.settings.subscription_update_queries += [ set_query ]
        return disk_part_number_
