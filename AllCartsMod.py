


from copy import deepcopy
from datetime import datetime, timedelta

from Required import Connections



conn = Connections.connect()
cur = conn.cursor()



def dupeCheckXmlShipUserdefval2(_company_id, _orders, _cart, _days_ago=0, _print=False):
    """
    input:  _orders =
            _company_id =
            _cart =
            _days_ago =
    output: Return ordering_, a list of orders from _ordering that are not duplicates of previous
            orders found in tblXmlShipData based on userdefval2.  If dupes are found they are
            returned as a list in dupes_.
    """

    # Ensure _cart is correctly argued.
    if _cart not in ['Shopify']:
        cart_check_exit =  "when calling dupeCheckXmlShipUserdefval2(), arg _cart only accepts"
        cart_check_exit += "'Shopify', not '{}', please try again"
        exit(cart_check_exit.format(_cart))

    # BLOCK...  Get list of previous userdefval2 values from argued conditions.
    query = """
        SELECT DISTINCT userdefval2 FROM tblXmlShipData WHERE CompanyID = {} AND ReqBy = '{}' {}
    """
    and_indate_ext = "AND inDate > '{}'"
    # Update query with AND inDate extension if needed based on _days_ago,
    if _days_ago == 0:
        query = query.format(_company_id, _cart, '')
    elif _days_ago > 0:
        days_ago_stamp = datetime.now() - timedelta(days=_days_ago)
        query = query.format(_company_id, _cart, and_indate_ext.format(days_ago_stamp))
    cur.execute(query)
    prev_userdefval2s = [ i[0] for i in cur.fetchall() ]

    # BLOCK...  Get ordering_ and dupes_ based on whether or not an order in ordering is in
    # prev_userdefval2.
    not_dupes_, dupes_ = [], []
    for order in _orders:
        # Update userdefval2 based on _cart.
        if _cart == 'Shopify':
            if _print:  print(">>>     checking order {}...  ".format(order.id), end='')
            userdefval2 = order.id
        # Basic conditionals checking if userdefval2 is in prev_userdefval2s and assigning order
        # accordingly.
        if userdefval2 not in prev_userdefval2s:
            not_dupes_ += [order]
            if _print:  print("is not a dupe")
        else:
            dupes_ += [order]
            if _print:  print("is a dupe")

    return not_dupes_, dupes_



def insertIntoXmlShipData(_ordering, _print=False):
    """
    input:  _ordering =
    output:
    """

    # Build ship_info_cols, sku_qty_cols, then concatenate for all_cols.
    ship_info_cols = [
        'CompanyID', 'inDate', 'ReqBy', 'Company', 'Attn', 'Addy1', 'Addy2', 'City', 'State', 'Zip',
        'Country', 'Phone', 'ShipMethod', 'ShipNumber', 'Email', 'userdefval2'
    ]
    sku_qty_cols = ['sku', 'qty']
    for i in range(2, 61):  sku_qty_cols += ['sku{}'.format(i), 'qty{}'.format(i)]
    all_cols = ship_info_cols + sku_qty_cols

    # BLOCK...  Build inserts.  Start by building empty_items_insert_list as default template for
    # items_insert_list.
    empty_items_insert_list = []
    for i, _ in enumerate(range(len(sku_qty_cols))):
        if i % 2 == 0:  empty_items_insert_list += ['\'\'']
        else:  empty_items_insert_list += ['0']
    # Build inserts_list (easier to build as list, then convert to string).
    inserts_list = []
    for order in _ordering:
        # Build ship_info_insert.
        ship_info_list = [ '\'{}\''.format(str(order['ship_info'][c])) for c in ship_info_cols ]
        ship_info_insert = ', '.join(ship_info_list)
        # Build items_insert.
        items_insert_list = deepcopy(empty_items_insert_list)
        counter = 0
        for sku, qty in order['items'].items():
            items_insert_list[counter] = '\'{}\''.format(sku)
            items_insert_list[counter + 1] = str(qty)
            counter += 2
        items_insert = ', '.join(items_insert_list)
        # Combine ship_info_insert and items_insert to build inserts_list.
        inserts_list += ['({}, {})'.format(ship_info_insert, items_insert)]
    # Convert inserts_list into inserts string.
    inserts = ',\n'.join([ i for i in inserts_list ])

    # With ship_info_cols, sku_qty_cols, and inserts, build and execute sql query.
    query = """INSERT INTO tblXmlShipData (\n{}\n)\nVALUES\n{}"""
    query = query.format(', '.join([ col for col in all_cols ]), inserts)
    if _print:  print(query)

    exit()

    # cur.execute(query)
    # conn.commit()
