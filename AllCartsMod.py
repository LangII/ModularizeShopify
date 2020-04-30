


from datetime import datetime, timedelta

from Required import Connections



conn = Connections.connect()
cur = conn.cursor()



def xmlDupeCheckUserdefval2(_ordering, _company_id, _cart, _days_ago=0):
    """
    input:  _ordering =
            _company_id =
            _cart =
            _days_ago =
    output:
    """

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
    prev_userdefval2 = [ i[0] for i in cur.fetchall() ]

    # Get ordering_ and dupes_ based on whether or not an order in ordering is in prev_userdefval2.
    ordering_, dupes_ = [], []
    for order in _ordering:
        if order['ship_info']['userdefval2'] not in prev_userdefval2:  ordering_ += [order]
        else:  dupes_ += [order]

    return ordering_, dupes_
