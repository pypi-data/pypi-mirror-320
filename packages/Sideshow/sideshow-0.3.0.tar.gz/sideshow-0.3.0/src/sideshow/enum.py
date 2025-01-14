# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024 Lance Edgar
#
#  This file is part of Sideshow.
#
#  Sideshow is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sideshow is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sideshow.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Enum Values
"""

from enum import Enum
from collections import OrderedDict

from wuttjamaican.enum import *


ORDER_UOM_CASE          = 'CS'
"""
UOM code for ordering a "case" of product.

Sideshow will treat "case" orders somewhat differently as compared to
"unit" orders.
"""

ORDER_UOM_UNIT          = 'EA'
"""
UOM code for ordering a "unit" of product.

This is the default "unit" UOM but in practice all others are treated
the same by Sideshow, whereas "case" orders are treated somewhat
differently.
"""

ORDER_UOM_KILOGRAM      = 'KG'
"""
UOM code for ordering a "kilogram" of product.

This is treated same as "unit" by Sideshow.  However it should
(probably?) only be used for items where
e.g. :attr:`~sideshow.db.model.orders.OrderItem.product_weighed` is
true.
"""

ORDER_UOM_POUND         = 'LB'
"""
UOM code for ordering a "pound" of product.

This is treated same as "unit" by Sideshow.  However it should
(probably?) only be used for items where
e.g. :attr:`~sideshow.db.model.orders.OrderItem.product_weighed` is
true.
"""

ORDER_UOM = OrderedDict([
    (ORDER_UOM_CASE,            "Cases"),
    (ORDER_UOM_UNIT,            "Units"),
    (ORDER_UOM_KILOGRAM,        "Kilograms"),
    (ORDER_UOM_POUND,           "Pounds"),
])
"""
Dict of possible code -> label options for ordering unit of measure.

These codes are referenced by:

* :attr:`sideshow.db.model.batch.neworder.NewOrderBatchRow.order_uom`
* :attr:`sideshow.db.model.orders.OrderItem.order_uom`
"""


class PendingCustomerStatus(Enum):
    """
    Enum values for
    :attr:`sideshow.db.model.customers.PendingCustomer.status`.
    """
    PENDING = 'pending'
    READY = 'ready'
    RESOLVED = 'resolved'


class PendingProductStatus(Enum):
    """
    Enum values for
    :attr:`sideshow.db.model.products.PendingProduct.status`.
    """
    PENDING = 'pending'
    READY = 'ready'
    RESOLVED = 'resolved'


########################################
# Order Item Status
########################################

ORDER_ITEM_STATUS_UNINITIATED       = 1
ORDER_ITEM_STATUS_INITIATED         = 10
ORDER_ITEM_STATUS_PAID_BEFORE       = 50
# TODO: deprecate / remove this one
ORDER_ITEM_STATUS_PAID              = ORDER_ITEM_STATUS_PAID_BEFORE
ORDER_ITEM_STATUS_READY             = 100
ORDER_ITEM_STATUS_PLACED            = 200
ORDER_ITEM_STATUS_RECEIVED          = 300
ORDER_ITEM_STATUS_CONTACTED         = 350
ORDER_ITEM_STATUS_CONTACT_FAILED    = 375
ORDER_ITEM_STATUS_DELIVERED         = 500
ORDER_ITEM_STATUS_PAID_AFTER        = 550
ORDER_ITEM_STATUS_CANCELED          = 900
ORDER_ITEM_STATUS_REFUND_PENDING    = 910
ORDER_ITEM_STATUS_REFUNDED          = 920
ORDER_ITEM_STATUS_RESTOCKED         = 930
ORDER_ITEM_STATUS_EXPIRED           = 940
ORDER_ITEM_STATUS_INACTIVE          = 950

ORDER_ITEM_STATUS = OrderedDict([
    (ORDER_ITEM_STATUS_UNINITIATED,         "uninitiated"),
    (ORDER_ITEM_STATUS_INITIATED,           "initiated"),
    (ORDER_ITEM_STATUS_PAID_BEFORE,         "paid"),
    (ORDER_ITEM_STATUS_READY,               "ready"),
    (ORDER_ITEM_STATUS_PLACED,              "placed"),
    (ORDER_ITEM_STATUS_RECEIVED,            "received"),
    (ORDER_ITEM_STATUS_CONTACTED,           "contacted"),
    (ORDER_ITEM_STATUS_CONTACT_FAILED,      "contact failed"),
    (ORDER_ITEM_STATUS_DELIVERED,           "delivered"),
    (ORDER_ITEM_STATUS_PAID_AFTER,          "paid"),
    (ORDER_ITEM_STATUS_CANCELED,            "canceled"),
    (ORDER_ITEM_STATUS_REFUND_PENDING,      "refund pending"),
    (ORDER_ITEM_STATUS_REFUNDED,            "refunded"),
    (ORDER_ITEM_STATUS_RESTOCKED,           "restocked"),
    (ORDER_ITEM_STATUS_EXPIRED,             "expired"),
    (ORDER_ITEM_STATUS_INACTIVE,            "inactive"),
])
