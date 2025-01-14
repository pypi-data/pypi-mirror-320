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
Views for Orders
"""

import decimal
import logging

import colander
from sqlalchemy import orm

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import UserRef, WuttaMoney, WuttaQuantity, WuttaEnum, WuttaDictEnum

from sideshow.db.model import Order, OrderItem
from sideshow.batch.neworder import NewOrderBatchHandler
from sideshow.web.forms.schema import (OrderRef,
                                       LocalCustomerRef, LocalProductRef,
                                       PendingCustomerRef, PendingProductRef)


log = logging.getLogger(__name__)


class OrderView(MasterView):
    """
    Master view for :class:`~sideshow.db.model.orders.Order`; route
    prefix is ``orders``.

    Notable URLs provided by this class:

    * ``/orders/``
    * ``/orders/new``
    * ``/orders/XXX``
    * ``/orders/XXX/delete``

    Note that the "edit" view is not exposed here; user must perform
    various other workflow actions to modify the order.

    .. attribute:: batch_handler

       Reference to the new order batch handler, as returned by
       :meth:`get_batch_handler()`.  This gets set in the constructor.
    """
    model_class = Order
    editable = False
    configurable = True

    labels = {
        'order_id': "Order ID",
        'store_id': "Store ID",
        'customer_id': "Customer ID",
    }

    grid_columns = [
        'order_id',
        'store_id',
        'customer_id',
        'customer_name',
        'total_price',
        'created',
        'created_by',
    ]

    sort_defaults = ('order_id', 'desc')

    form_fields = [
        'order_id',
        'store_id',
        'customer_id',
        'local_customer',
        'pending_customer',
        'customer_name',
        'phone_number',
        'email_address',
        'total_price',
        'created',
        'created_by',
    ]

    has_rows = True
    row_model_class = OrderItem
    rows_title = "Order Items"
    rows_sort_defaults = 'sequence'
    rows_viewable = True

    row_labels = {
        'product_scancode': "Scancode",
        'product_brand': "Brand",
        'product_description': "Description",
        'product_size': "Size",
        'department_name': "Department",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    row_grid_columns = [
        'sequence',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'order_qty',
        'order_uom',
        'total_price',
        'status_code',
    ]

    PENDING_PRODUCT_ENTRY_FIELDS = [
        'scancode',
        'brand_name',
        'description',
        'size',
        'department_name',
        'vendor_name',
        'vendor_item_code',
        'case_size',
        'unit_cost',
        'unit_price_reg',
    ]

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # order_id
        g.set_link('order_id')

        # customer_id
        g.set_link('customer_id')

        # customer_name
        g.set_link('customer_name')

        # total_price
        g.set_renderer('total_price', g.render_currency)

    def get_batch_handler(self):
        """
        Returns the configured :term:`handler` for :term:`new order
        batches <new order batch>`.

        You normally would not need to call this, and can use
        :attr:`batch_handler` instead.

        :returns:
           :class:`~sideshow.batch.neworder.NewOrderBatchHandler`
           instance.
        """
        if hasattr(self, 'batch_handler'):
            return self.batch_handler
        return self.app.get_batch_handler('neworder')

    def create(self):
        """
        Instead of the typical "create" view, this displays a "wizard"
        of sorts.

        Under the hood a
        :class:`~sideshow.db.model.batch.neworder.NewOrderBatch` is
        automatically created for the user when they first visit this
        page.  They can select a customer, add items etc.

        When user is finished assembling the order (i.e. populating
        the batch), they submit it.  This of course executes the
        batch, which in turn creates a true
        :class:`~sideshow.db.model.orders.Order`, and user is
        redirected to the "view order" page.

        See also these methods which may be called from this one,
        based on user actions:

        * :meth:`start_over()`
        * :meth:`cancel_order()`
        * :meth:`assign_customer()`
        * :meth:`unassign_customer()`
        * :meth:`set_pending_customer()`
        * :meth:`get_product_info()`
        * :meth:`add_item()`
        * :meth:`update_item()`
        * :meth:`delete_item()`
        * :meth:`submit_order()`
        """
        enum = self.app.enum
        self.creating = True
        self.batch_handler = self.get_batch_handler()
        batch = self.get_current_batch()

        context = self.get_context_customer(batch)

        if self.request.method == 'POST':

            # first we check for traditional form post
            action = self.request.POST.get('action')
            post_actions = [
                'start_over',
                'cancel_order',
            ]
            if action in post_actions:
                return getattr(self, action)(batch)

            # okay then, we'll assume newer JSON-style post params
            data = dict(self.request.json_body)
            action = data.pop('action')
            json_actions = [
                'assign_customer',
                'unassign_customer',
                # 'update_phone_number',
                # 'update_email_address',
                'set_pending_customer',
                # 'get_customer_info',
                # # 'set_customer_data',
                'get_product_info',
                # 'get_past_items',
                'add_item',
                'update_item',
                'delete_item',
                'submit_order',
            ]
            if action in json_actions:
                try:
                    result = getattr(self, action)(batch, data)
                except Exception as error:
                    log.warning("error calling json action for order", exc_info=True)
                    result = {'error': self.app.render_error(error)}
                return self.json_response(result)

            return self.json_response({'error': "unknown form action"})

        context.update({
            'batch': batch,
            'normalized_batch': self.normalize_batch(batch),
            'order_items': [self.normalize_row(row)
                            for row in batch.rows],
            'default_uom_choices': self.get_default_uom_choices(),
            'default_uom': None, # TODO?
            'allow_unknown_products': (self.batch_handler.allow_unknown_products()
                                       and self.has_perm('create_unknown_product')),
            'pending_product_required_fields': self.get_pending_product_required_fields(),
        })
        return self.render_to_response('create', context)

    def get_current_batch(self):
        """
        Returns the current batch for the current user.

        This looks for a new order batch which was created by the
        user, but not yet executed.  If none is found, a new batch is
        created.

        :returns:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
           instance
        """
        model = self.app.model
        session = self.Session()

        user = self.request.user
        if not user:
            raise self.forbidden()

        try:
            # there should be at most *one* new batch per user
            batch = session.query(model.NewOrderBatch)\
                           .filter(model.NewOrderBatch.created_by == user)\
                           .filter(model.NewOrderBatch.executed == None)\
                           .one()

        except orm.exc.NoResultFound:
            # no batch yet for this user, so make one
            batch = self.batch_handler.make_batch(session, created_by=user)
            session.add(batch)
            session.flush()

        return batch

    def customer_autocomplete(self):
        """
        AJAX view for customer autocomplete, when entering new order.

        This invokes one of the following on the
        :attr:`batch_handler`:

        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_customers_external()`
        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_customers_local()`

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        session = self.Session()
        term = self.request.GET.get('term', '').strip()
        if not term:
            return []

        handler = self.get_batch_handler()
        if handler.use_local_customers():
            return handler.autocomplete_customers_local(session, term, user=self.request.user)
        else:
            return handler.autocomplete_customers_external(session, term, user=self.request.user)

    def product_autocomplete(self):
        """
        AJAX view for product autocomplete, when entering new order.

        This invokes one of the following on the
        :attr:`batch_handler`:

        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_products_external()`
        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_products_local()`

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        session = self.Session()
        term = self.request.GET.get('term', '').strip()
        if not term:
            return []

        handler = self.get_batch_handler()
        if handler.use_local_products():
            return handler.autocomplete_products_local(session, term, user=self.request.user)
        else:
            return handler.autocomplete_products_external(session, term, user=self.request.user)

    def get_pending_product_required_fields(self):
        """ """
        required = []
        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            require = self.config.get_bool(
                f'sideshow.orders.unknown_product.fields.{field}.required')
            if require is None and field == 'description':
                require = True
            if require:
                required.append(field)
        return required

    def start_over(self, batch):
        """
        This will delete the user's current batch, then redirect user
        back to "Create Order" page, which in turn will auto-create a
        new batch for them.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`cancel_order()`
        * :meth:`submit_order()`
        """
        # drop current batch
        self.batch_handler.do_delete(batch, self.request.user)
        self.Session.flush()

        # send back to "create order" which makes new batch
        route_prefix = self.get_route_prefix()
        url = self.request.route_url(f'{route_prefix}.create')
        return self.redirect(url)

    def cancel_order(self, batch):
        """
        This will delete the user's current batch, then redirect user
        back to "List Orders" page.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`start_over()`
        * :meth:`submit_order()`
        """
        self.batch_handler.do_delete(batch, self.request.user)
        self.Session.flush()

        # set flash msg just to be more obvious
        self.request.session.flash("New order has been deleted.")

        # send user back to orders list, w/ no new batch generated
        url = self.get_index_url()
        return self.redirect(url)

    def get_context_customer(self, batch):
        """ """
        context = {
            'customer_is_known': True,
            'customer_id': None,
            'customer_name': batch.customer_name,
            'phone_number': batch.phone_number,
            'email_address': batch.email_address,
        }

        # customer_id
        use_local = self.batch_handler.use_local_customers()
        if use_local:
            local = batch.local_customer
            if local:
                context['customer_id'] = local.uuid.hex
        else: # use external
            context['customer_id'] = batch.customer_id

        # pending customer
        pending = batch.pending_customer
        if pending:
            context.update({
                'new_customer_first_name': pending.first_name,
                'new_customer_last_name': pending.last_name,
                'new_customer_full_name': pending.full_name,
                'new_customer_phone': pending.phone_number,
                'new_customer_email': pending.email_address,
            })

        # declare customer "not known" only if pending is in use
        if (pending
            and not batch.customer_id and not batch.local_customer
            and batch.customer_name):
            context['customer_is_known'] = False

        return context

    def assign_customer(self, batch, data):
        """
        Assign the true customer account for a batch.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`unassign_customer()`
        * :meth:`set_pending_customer()`
        """
        customer_id = data.get('customer_id')
        if not customer_id:
            return {'error': "Must provide customer_id"}

        self.batch_handler.set_customer(batch, customer_id)
        return self.get_context_customer(batch)

    def unassign_customer(self, batch, data):
        """
        Clear the customer info for a batch.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`assign_customer()`
        * :meth:`set_pending_customer()`
        """
        self.batch_handler.set_customer(batch, None)
        return self.get_context_customer(batch)

    def set_pending_customer(self, batch, data):
        """
        This will set/update the batch pending customer info.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`assign_customer()`
        * :meth:`unassign_customer()`
        """
        self.batch_handler.set_customer(batch, data, user=self.request.user)
        return self.get_context_customer(batch)

    def get_product_info(self, batch, data):
        """
        Fetch data for a specific product.  (Nothing is modified.)

        Depending on config, this will fetch a :term:`local product`
        or :term:`external product` to get the data.

        This should invoke a configured handler for the query
        behavior, but that is not yet implemented.  For now it uses
        built-in logic only, which queries the
        :class:`~sideshow.db.model.products.LocalProduct` table.

        This is a "batch action" method which may be called from
        :meth:`create()`.
        """
        product_id = data.get('product_id')
        if not product_id:
            return {'error': "Must specify a product ID"}

        session = self.Session()
        use_local = self.batch_handler.use_local_products()
        if use_local:
            data = self.batch_handler.get_product_info_local(session, product_id)
        else:
            data = self.batch_handler.get_product_info_external(session, product_id)

        if 'error' in data:
            return data

        if 'unit_price_reg' in data and 'unit_price_reg_display' not in data:
            data['unit_price_reg_display'] = self.app.render_currency(data['unit_price_reg'])

        if 'unit_price_reg' in data and 'unit_price_quoted' not in data:
            data['unit_price_quoted'] = data['unit_price_reg']

        if 'unit_price_quoted' in data and 'unit_price_quoted_display' not in data:
            data['unit_price_quoted_display'] = self.app.render_currency(data['unit_price_quoted'])

        if 'case_price_quoted' not in data:
            if data.get('unit_price_quoted') is not None and data.get('case_size') is not None:
                data['case_price_quoted'] = data['unit_price_quoted'] * data['case_size']

        if 'case_price_quoted' in data and 'case_price_quoted_display' not in data:
            data['case_price_quoted_display'] = self.app.render_currency(data['case_price_quoted'])

        decimal_fields = [
            'case_size',
            'unit_price_reg',
            'unit_price_quoted',
            'case_price_quoted',
        ]

        for field in decimal_fields:
            if field in list(data):
                value = data[field]
                if isinstance(value, decimal.Decimal):
                    data[field] = float(value)

        return data

    def add_item(self, batch, data):
        """
        This adds a row to the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`update_item()`
        * :meth:`delete_item()`
        """
        row = self.batch_handler.add_item(batch, data['product_info'],
                                          data['order_qty'], data['order_uom'])

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def update_item(self, batch, data):
        """
        This updates a row in the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`add_item()`
        * :meth:`delete_item()`
        """
        model = self.app.model
        session = self.Session()

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify row UUID"}

        row = session.get(model.NewOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row.batch is not batch:
            return {'error': "Row is for wrong batch"}

        self.batch_handler.update_item(row, data['product_info'],
                                       data['order_qty'], data['order_uom'])

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def delete_item(self, batch, data):
        """
        This deletes a row from the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`add_item()`
        * :meth:`update_item()`
        """
        model = self.app.model
        session = self.app.get_session(batch)

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = session.get(model.NewOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row.batch is not batch:
            return {'error': "Row is for wrong batch"}

        self.batch_handler.do_remove_row(row)
        return {'batch': self.normalize_batch(batch)}

    def submit_order(self, batch, data):
        """
        This submits the user's current new order batch, hence
        executing the batch and creating the true order.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`start_over()`
        * :meth:`cancel_order()`
        """
        user = self.request.user
        reason = self.batch_handler.why_not_execute(batch, user=user)
        if reason:
            return {'error': reason}

        try:
            order = self.batch_handler.do_execute(batch, user)
        except Exception as error:
            log.warning("failed to execute new order batch: %s", batch,
                        exc_info=True)
            return {'error': self.app.render_error(error)}

        return {
            'next_url': self.get_action_url('view', order),
        }

    def normalize_batch(self, batch):
        """ """
        return {
            'uuid': batch.uuid.hex,
            'total_price': str(batch.total_price or 0),
            'total_price_display': self.app.render_currency(batch.total_price),
            'status_code': batch.status_code,
            'status_text': batch.status_text,
        }

    def get_default_uom_choices(self):
        """ """
        enum = self.app.enum
        return [{'key': key, 'value': val}
                for key, val in enum.ORDER_UOM.items()]

    def normalize_row(self, row):
        """ """
        enum = self.app.enum

        data = {
            'uuid': row.uuid.hex,
            'sequence': row.sequence,
            'product_id': None,
            'product_scancode': row.product_scancode,
            'product_brand': row.product_brand,
            'product_description': row.product_description,
            'product_size': row.product_size,
            'product_full_description': self.app.make_full_name(row.product_brand,
                                                                row.product_description,
                                                                row.product_size),
            'product_weighed': row.product_weighed,
            'department_display': row.department_name,
            'special_order': row.special_order,
            'case_size': float(row.case_size) if row.case_size is not None else None,
            'order_qty': float(row.order_qty),
            'order_uom': row.order_uom,
            'order_uom_choices': self.get_default_uom_choices(),
            'unit_price_quoted': float(row.unit_price_quoted) if row.unit_price_quoted is not None else None,
            'unit_price_quoted_display': self.app.render_currency(row.unit_price_quoted),
            'case_price_quoted': float(row.case_price_quoted) if row.case_price_quoted is not None else None,
            'case_price_quoted_display': self.app.render_currency(row.case_price_quoted),
            'total_price': float(row.total_price) if row.total_price is not None else None,
            'total_price_display': self.app.render_currency(row.total_price),
            'status_code': row.status_code,
            'status_text': row.status_text,
        }

        use_local = self.batch_handler.use_local_products()

        # product_id
        if use_local:
            if row.local_product:
                data['product_id'] = row.local_product.uuid.hex
        else:
            data['product_id'] = row.product_id

        # vendor_name
        if use_local:
            if row.local_product:
                data['vendor_name'] = row.local_product.vendor_name
        else: # use external
            pass                # TODO
        if not data.get('product_id') and row.pending_product:
            data['vendor_name'] = row.pending_product.vendor_name

        if row.unit_price_reg:
            data['unit_price_reg'] = float(row.unit_price_reg)
            data['unit_price_reg_display'] = self.app.render_currency(row.unit_price_reg)

        if row.unit_price_sale:
            data['unit_price_sale'] = float(row.unit_price_sale)
            data['unit_price_sale_display'] = self.app.render_currency(row.unit_price_sale)
        if row.sale_ends:
            sale_ends = row.sale_ends
            data['sale_ends'] = str(row.sale_ends)
            data['sale_ends_display'] = self.app.render_date(row.sale_ends)

        if row.pending_product:
            pending = row.pending_product
            data['pending_product'] = {
                'uuid': pending.uuid.hex,
                'scancode': pending.scancode,
                'brand_name': pending.brand_name,
                'description': pending.description,
                'size': pending.size,
                'department_id': pending.department_id,
                'department_name': pending.department_name,
                'unit_price_reg': float(pending.unit_price_reg) if pending.unit_price_reg is not None else None,
                'vendor_name': pending.vendor_name,
                'vendor_item_code': pending.vendor_item_code,
                'unit_cost': float(pending.unit_cost) if pending.unit_cost is not None else None,
                'case_size': float(pending.case_size) if pending.case_size is not None else None,
                'notes': pending.notes,
                'special_order': pending.special_order,
            }

        # display text for order qty/uom
        if row.order_uom == enum.ORDER_UOM_CASE:
            order_qty = self.app.render_quantity(row.order_qty)
            if row.case_size is None:
                case_qty = unit_qty = '??'
            else:
                case_qty = self.app.render_quantity(row.case_size)
                unit_qty = self.app.render_quantity(row.order_qty * row.case_size)
            CS = enum.ORDER_UOM[enum.ORDER_UOM_CASE]
            EA = enum.ORDER_UOM[enum.ORDER_UOM_UNIT]
            data['order_qty_display'] = (f"{order_qty} {CS} "
                                         f"(&times; {case_qty} = {unit_qty} {EA})")
        else:
            unit_qty = self.app.render_quantity(row.order_qty)
            EA = enum.ORDER_UOM[enum.ORDER_UOM_UNIT]
            data['order_qty_display'] = f"{unit_qty} {EA}"

        return data

    def get_instance_title(self, order):
        """ """
        return f"#{order.order_id} for {order.customer_name}"

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        order = f.model_instance

        # local_customer
        f.set_node('local_customer', LocalCustomerRef(self.request))

        # pending_customer
        if order.customer_id or order.local_customer:
            f.remove('pending_customer')
        else:
            f.set_node('pending_customer', PendingCustomerRef(self.request))

        # total_price
        f.set_node('total_price', WuttaMoney(self.request))

        # created_by
        f.set_node('created_by', UserRef(self.request))
        f.set_readonly('created_by')

    def get_xref_buttons(self, order):
        """ """
        buttons = super().get_xref_buttons(order)
        model = self.app.model
        session = self.Session()

        if self.request.has_perm('neworder_batches.view'):
            batch = session.query(model.NewOrderBatch)\
                           .filter(model.NewOrderBatch.id == order.order_id)\
                           .first()
            if batch:
                url = self.request.route_url('neworder_batches.view', uuid=batch.uuid)
                buttons.append(
                    self.make_button("View the Batch", primary=True, icon_left='eye', url=url))

        return buttons

    def get_row_grid_data(self, order):
        """ """
        model = self.app.model
        session = self.Session()
        return session.query(model.OrderItem)\
                      .filter(model.OrderItem.order == order)

    def configure_row_grid(self, g):
        """ """
        super().configure_row_grid(g)
        enum = self.app.enum

        # sequence
        g.set_label('sequence', "Seq.", column_only=True)
        g.set_link('sequence')

        # product_scancode
        g.set_link('product_scancode')

        # product_brand
        g.set_link('product_brand')

        # product_description
        g.set_link('product_description')

        # product_size
        g.set_link('product_size')

        # TODO
        # order_uom
        #g.set_renderer('order_uom', self.grid_render_enum, enum=enum.OrderUOM)

        # total_price
        g.set_renderer('total_price', g.render_currency)

        # status_code
        g.set_renderer('status_code', self.render_status_code)

    def render_status_code(self, item, key, value):
        """ """
        enum = self.app.enum
        return enum.ORDER_ITEM_STATUS[value]

    def get_row_action_url_view(self, item, i):
        """ """
        return self.request.route_url('order_items.view', uuid=item.uuid)

    def configure_get_simple_settings(self):
        """ """
        settings = [

            # batches
            {'name': 'wutta.batch.neworder.handler.spec'},

            # customers
            {'name': 'sideshow.orders.use_local_customers',
             # nb. this is really a bool but we present as string in config UI
             #'type': bool,
             'default': 'true'},

            # products
            {'name': 'sideshow.orders.use_local_products',
             # nb. this is really a bool but we present as string in config UI
             #'type': bool,
             'default': 'true'},
            {'name': 'sideshow.orders.allow_unknown_products',
             'type': bool,
             'default': True},
        ]

        # required fields for new product entry
        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            setting = {'name': f'sideshow.orders.unknown_product.fields.{field}.required',
                       'type': bool}
            if field == 'description':
                setting['default'] = True
            settings.append(setting)

        return settings

    def configure_get_context(self, **kwargs):
        """ """
        context = super().configure_get_context(**kwargs)

        context['pending_product_fields'] = self.PENDING_PRODUCT_ENTRY_FIELDS

        handlers = self.app.get_batch_handler_specs('neworder')
        handlers = [{'spec': spec} for spec in handlers]
        context['batch_handlers'] = handlers

        return context

    @classmethod
    def defaults(cls, config):
        cls._order_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix perm group
        config.add_wutta_permission_group(permission_prefix,
                                          model_title_plural,
                                          overwrite=False)

        # extra perm required to create order with unknown/pending product
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.create_unknown_product',
                                    f"Create new {model_title} for unknown/pending product")

        # customer autocomplete
        config.add_route(f'{route_prefix}.customer_autocomplete',
                         f'{url_prefix}/customer-autocomplete',
                         request_method='GET')
        config.add_view(cls, attr='customer_autocomplete',
                        route_name=f'{route_prefix}.customer_autocomplete',
                        renderer='json',
                        permission=f'{permission_prefix}.list')

        # product autocomplete
        config.add_route(f'{route_prefix}.product_autocomplete',
                         f'{url_prefix}/product-autocomplete',
                         request_method='GET')
        config.add_view(cls, attr='product_autocomplete',
                        route_name=f'{route_prefix}.product_autocomplete',
                        renderer='json',
                        permission=f'{permission_prefix}.list')


class OrderItemView(MasterView):
    """
    Master view for :class:`~sideshow.db.model.orders.OrderItem`;
    route prefix is ``order_items``.

    Notable URLs provided by this class:

    * ``/order-items/``
    * ``/order-items/XXX``

    Note that this does not expose create, edit or delete.  The user
    must perform various other workflow actions to modify the item.
    """
    model_class = OrderItem
    model_title = "Order Item"
    route_prefix = 'order_items'
    url_prefix = '/order-items'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'order_id': "Order ID",
        'product_id': "Product ID",
        'product_scancode': "Scancode",
        'product_brand': "Brand",
        'product_description': "Description",
        'product_size': "Size",
        'product_weighed': "Sold by Weight",
        'department_id': "Department ID",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    grid_columns = [
        'order_id',
        'customer_name',
        # 'sequence',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'order_qty',
        'order_uom',
        'total_price',
        'status_code',
    ]

    sort_defaults = ('order_id', 'desc')

    form_fields = [
        'order',
        # 'customer_name',
        'sequence',
        'product_id',
        'local_product',
        'pending_product',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'product_weighed',
        'department_id',
        'department_name',
        'special_order',
        'case_size',
        'unit_cost',
        'unit_price_reg',
        'unit_price_sale',
        'sale_ends',
        'unit_price_quoted',
        'case_price_quoted',
        'order_qty',
        'order_uom',
        'discount_percent',
        'total_price',
        'status_code',
        'paid_amount',
        'payment_transaction_number',
    ]

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        return query.join(model.Order)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        model = self.app.model
        # enum = self.app.enum

        # order_id
        g.set_sorter('order_id', model.Order.order_id)
        g.set_renderer('order_id', self.render_order_id)
        g.set_link('order_id')

        # customer_name
        g.set_label('customer_name', "Customer", column_only=True)

        # # sequence
        # g.set_label('sequence', "Seq.", column_only=True)

        # product_scancode
        g.set_link('product_scancode')

        # product_brand
        g.set_link('product_brand')

        # product_description
        g.set_link('product_description')

        # product_size
        g.set_link('product_size')

        # order_uom
        # TODO
        #g.set_renderer('order_uom', self.grid_render_enum, enum=enum.OrderUOM)

        # total_price
        g.set_renderer('total_price', g.render_currency)

        # status_code
        g.set_renderer('status_code', self.render_status_code)

    def render_order_id(self, item, key, value):
        """ """
        return item.order.order_id

    def render_status_code(self, item, key, value):
        """ """
        enum = self.app.enum
        return enum.ORDER_ITEM_STATUS[value]

    def get_instance_title(self, item):
        """ """
        enum = self.app.enum
        title = str(item)
        status = enum.ORDER_ITEM_STATUS[item.status_code]
        return f"({status}) {title}"

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        enum = self.app.enum
        item = f.model_instance

        # order
        f.set_node('order', OrderRef(self.request))

        # local_product
        f.set_node('local_product', LocalProductRef(self.request))

        # pending_product
        if item.product_id or item.local_product:
            f.remove('pending_product')
        else:
            f.set_node('pending_product', PendingProductRef(self.request))

        # order_qty
        f.set_node('order_qty', WuttaQuantity(self.request))

        # order_uom
        f.set_node('order_uom', WuttaDictEnum(self.request, enum.ORDER_UOM))

        # case_size
        f.set_node('case_size', WuttaQuantity(self.request))

        # unit_cost
        f.set_node('unit_cost', WuttaMoney(self.request, scale=4))

        # unit_price_reg
        f.set_node('unit_price_reg', WuttaMoney(self.request))

        # unit_price_quoted
        f.set_node('unit_price_quoted', WuttaMoney(self.request))

        # case_price_quoted
        f.set_node('case_price_quoted', WuttaMoney(self.request))

        # total_price
        f.set_node('total_price', WuttaMoney(self.request))

        # status
        f.set_node('status_code', WuttaDictEnum(self.request, enum.ORDER_ITEM_STATUS))

        # paid_amount
        f.set_node('paid_amount', WuttaMoney(self.request))

    def get_xref_buttons(self, item):
        """ """
        buttons = super().get_xref_buttons(item)

        if self.request.has_perm('orders.view'):
            url = self.request.route_url('orders.view', uuid=item.order_uuid)
            buttons.append(
                self.make_button("View the Order", url=url,
                                 primary=True, icon_left='eye'))

        return buttons


def defaults(config, **kwargs):
    base = globals()

    OrderView = kwargs.get('OrderView', base['OrderView'])
    OrderView.defaults(config)

    OrderItemView = kwargs.get('OrderItemView', base['OrderItemView'])
    OrderItemView.defaults(config)


def includeme(config):
    defaults(config)
