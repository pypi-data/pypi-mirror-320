# -*- coding: utf-8; -*-

import datetime
import decimal
from unittest.mock import patch

from sqlalchemy import orm
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.response import Response

from wuttaweb.forms.schema import WuttaMoney

from sideshow.batch.neworder import NewOrderBatchHandler
from sideshow.testing import WebTestCase
from sideshow.web.views import orders as mod
from sideshow.web.forms.schema import OrderRef, PendingProductRef


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestOrderView(WebTestCase):

    def make_view(self):
        return mod.OrderView(self.request)

    def make_handler(self):
        return NewOrderBatchHandler(self.config)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.PendingProduct)
        self.assertNotIn('order_id', grid.linked_columns)
        self.assertNotIn('total_price', grid.renderers)
        view.configure_grid(grid)
        self.assertIn('order_id', grid.linked_columns)
        self.assertIn('total_price', grid.renderers)

    def test_create(self):
        self.pyramid_config.include('sideshow.web.views')
        self.config.setdefault('wutta.batch.neworder.handler.spec',
                               'sideshow.batch.neworder:NewOrderBatchHandler')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'current_route_url', return_value='/orders/new'):

                # this will require some perms
                with patch.multiple(self.request, create=True,
                                    user=user, is_root=True):

                    # fetch page to start things off
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)
                    response = view.create()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    batch1 = self.session.query(model.NewOrderBatch).one()

                    # start over; deletes current batch
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        POST={'action': 'start_over'}):
                        response = view.create()
                        self.assertIsInstance(response, HTTPFound)
                        self.assertIn('/orders/new', response.location)
                        self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

                    # fetch again to get new batch
                    response = view.create()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    batch2 = self.session.query(model.NewOrderBatch).one()
                    self.assertIsNot(batch2, batch1)

                    # set pending customer
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        json_body={'action': 'set_pending_customer',
                                                   'first_name': 'Fred',
                                                   'last_name': 'Flintstone',
                                                   'phone_number': '555-1234',
                                                   'email_address': 'fred@mailinator.com'}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        self.assertEqual(response.json_body, {
                            'customer_is_known': False,
                            'customer_id': None,
                            'customer_name': 'Fred Flintstone',
                            'phone_number': '555-1234',
                            'email_address': 'fred@mailinator.com',
                            'new_customer_full_name': 'Fred Flintstone',
                            'new_customer_first_name': 'Fred',
                            'new_customer_last_name': 'Flintstone',
                            'new_customer_phone': '555-1234',
                            'new_customer_email': 'fred@mailinator.com',
                        })

                    # invalid action
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        POST={'action': 'bogus'},
                                        json_body={'action': 'bogus'}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        self.assertEqual(response.json_body, {'error': 'unknown form action'})

                    # add item
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        json_body={'action': 'add_item',
                                                   'product_info': {
                                                       'scancode': '07430500132',
                                                       'description': 'Vinegar',
                                                       'unit_price_reg': 5.99,
                                                   },
                                                   'order_qty': 1,
                                                   'order_uom': enum.ORDER_UOM_UNIT}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        data = response.json_body
                        self.assertEqual(sorted(data), ['batch', 'row'])

                    # add item, w/ error
                    with patch.object(NewOrderBatchHandler, 'add_item', side_effect=RuntimeError):
                        with patch.multiple(self.request, create=True,
                                            method='POST',
                                            json_body={'action': 'add_item',
                                                       'product_info': {
                                                           'scancode': '07430500116',
                                                           'description': 'Vinegar',
                                                           'unit_price_reg': 3.59,
                                                       },
                                                       'order_qty': 1,
                                                       'order_uom': enum.ORDER_UOM_UNIT}):
                            response = view.create()
                            self.assertIsInstance(response, Response)
                            self.assertEqual(response.content_type, 'application/json')
                            self.assertEqual(response.json_body, {'error': 'RuntimeError'})

    def test_get_current_batch(self):
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        # user is required
        self.assertRaises(HTTPForbidden, view.get_current_batch)

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    # batch is auto-created
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    self.assertIs(batch.created_by, user)

                    # same batch is returned subsequently
                    batch2 = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    self.assertIs(batch2, batch)

    def test_customer_autocomplete(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()
        view.batch_handler = handler

        with patch.object(view, 'Session', return_value=self.session):

            # empty results by default
            self.assertEqual(view.customer_autocomplete(), [])
            with patch.object(self.request, 'GET', new={'term': 'foo'}, create=True):
                self.assertEqual(view.customer_autocomplete(), [])

            # add a customer
            customer = model.LocalCustomer(full_name="Chuck Norris")
            self.session.add(customer)
            self.session.flush()

            # search for chuck finds chuck
            with patch.object(self.request, 'GET', new={'term': 'chuck'}, create=True):
                result = view.customer_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': customer.uuid.hex,
                    'label': "Chuck Norris",
                })

            # search for sally finds nothing
            with patch.object(self.request, 'GET', new={'term': 'sally'}, create=True):
                result = view.customer_autocomplete()
                self.assertEqual(result, [])

            # external lookup not implemented by default
            with patch.object(handler, 'use_local_customers', return_value=False):
                with patch.object(self.request, 'GET', new={'term': 'sally'}, create=True):
                    self.assertRaises(NotImplementedError, view.customer_autocomplete)

    def test_product_autocomplete(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()
        view.batch_handler = handler

        with patch.object(view, 'Session', return_value=self.session):

            # empty results by default
            self.assertEqual(view.product_autocomplete(), [])
            with patch.object(self.request, 'GET', new={'term': 'foo'}, create=True):
                self.assertEqual(view.product_autocomplete(), [])

            # add a product
            product = model.LocalProduct(brand_name="Bragg's", description="Vinegar")
            self.session.add(product)
            self.session.flush()

            # search for vinegar finds product
            with patch.object(self.request, 'GET', new={'term': 'vinegar'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': product.uuid.hex,
                    'label': "Bragg's Vinegar",
                })

            # search for brag finds product
            with patch.object(self.request, 'GET', new={'term': 'brag'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': product.uuid.hex,
                    'label': "Bragg's Vinegar",
                })

            # search for juice finds nothing
            with patch.object(self.request, 'GET', new={'term': 'juice'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(result, [])

            # external lookup not implemented by default
            with patch.object(handler, 'use_local_products', return_value=False):
                with patch.object(self.request, 'GET', new={'term': 'juice'}, create=True):
                    self.assertRaises(NotImplementedError, view.product_autocomplete)

    def test_get_pending_product_required_fields(self):
        model = self.app.model
        view = self.make_view()

        # only description is required by default
        fields = view.get_pending_product_required_fields()
        self.assertEqual(fields, ['description'])

        # but config can specify otherwise
        self.config.setdefault('sideshow.orders.unknown_product.fields.brand_name.required', 'true')
        self.config.setdefault('sideshow.orders.unknown_product.fields.description.required', 'false')
        self.config.setdefault('sideshow.orders.unknown_product.fields.size.required', 'true')
        self.config.setdefault('sideshow.orders.unknown_product.fields.unit_price_reg.required', 'true')
        fields = view.get_pending_product_required_fields()
        self.assertEqual(fields, ['brand_name', 'size', 'unit_price_reg'])

    def test_get_context_customer(self):
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()
        view.batch_handler = handler

        user = model.User(username='barney')
        self.session.add(user)

        # with external customer
        with patch.object(handler, 'use_local_customers', return_value=False):
            batch = handler.make_batch(self.session, created_by=user,
                                       customer_id=42, customer_name='Fred Flintstone',
                                       phone_number='555-1234', email_address='fred@mailinator.com')
            self.session.add(batch)
            self.session.flush()
            context = view.get_context_customer(batch)
            self.assertEqual(context, {
                'customer_is_known': True,
                'customer_id': 42,
                'customer_name': 'Fred Flintstone',
                'phone_number': '555-1234',
                'email_address': 'fred@mailinator.com',
            })

        # with local customer
        local = model.LocalCustomer(full_name="Betty Boop")
        self.session.add(local)
        batch = handler.make_batch(self.session, created_by=user,
                                   local_customer=local, customer_name='Betty Boop',
                                   phone_number='555-8888')
        self.session.add(batch)
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'customer_is_known': True,
            'customer_id': local.uuid.hex,
            'customer_name': 'Betty Boop',
            'phone_number': '555-8888',
            'email_address': None,
        })

        # with pending customer
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, dict(
            full_name="Fred Flintstone",
            first_name="Fred", last_name="Flintstone",
            phone_number='555-1234', email_address='fred@mailinator.com',
        ))
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'customer_is_known': False,
            'customer_id': None,
            'customer_name': 'Fred Flintstone',
            'phone_number': '555-1234',
            'email_address': 'fred@mailinator.com',
            'new_customer_full_name': 'Fred Flintstone',
            'new_customer_first_name': 'Fred',
            'new_customer_last_name': 'Flintstone',
            'new_customer_phone': '555-1234',
            'new_customer_email': 'fred@mailinator.com',
        })

        # with no customer
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'customer_is_known': True, # nb. this is for UI default
            'customer_id': None,
            'customer_name': None,
            'phone_number': None,
            'email_address': None,
        })

    def test_start_over(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    result = view.start_over(batch)
                    self.assertIsInstance(result, HTTPFound)
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

    def test_cancel_order(self):
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    result = view.cancel_order(batch)
                    self.assertIsInstance(result, HTTPFound)
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

    def test_assign_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        weirdal = model.LocalCustomer(full_name="Weird Al")
        self.session.add(weirdal)
        self.session.flush()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()

                    # normal
                    self.assertIsNone(batch.local_customer)
                    self.assertIsNone(batch.pending_customer)
                    context = view.assign_customer(batch, {'customer_id': weirdal.uuid.hex})
                    self.assertIsNone(batch.pending_customer)
                    self.assertIs(batch.local_customer, weirdal)
                    self.assertEqual(context, {
                        'customer_is_known': True,
                        'customer_id': weirdal.uuid.hex,
                        'customer_name': 'Weird Al',
                        'phone_number': None,
                        'email_address': None,
                    })

                    # missing customer_id
                    context = view.assign_customer(batch, {})
                    self.assertEqual(context, {'error': "Must provide customer_id"})

    def test_unassign_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    view.set_pending_customer(batch, {'first_name': 'Jack',
                                                      'last_name': 'Black'})

                    # normal
                    self.assertIsNone(batch.local_customer)
                    self.assertIsNotNone(batch.pending_customer)
                    self.assertEqual(batch.customer_name, 'Jack Black')
                    context = view.unassign_customer(batch, {})
                    # nb. pending record remains, but not used
                    self.assertIsNotNone(batch.pending_customer)
                    self.assertIsNone(batch.customer_name)
                    self.assertIsNone(batch.local_customer)
                    self.assertEqual(context, {
                        'customer_is_known': True,
                        'customer_id': None,
                        'customer_name': None,
                        'phone_number': None,
                        'email_address': None,
                        'new_customer_full_name': 'Jack Black',
                        'new_customer_first_name': 'Jack',
                        'new_customer_last_name': 'Black',
                        'new_customer_phone': None,
                        'new_customer_email': None,
                    })

    def test_set_pending_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'first_name': 'Fred',
            'last_name': 'Flintstone',
            'phone_number': '555-1234',
            'email_address': 'fred@mailinator.com',
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()

                    # normal
                    self.assertIsNone(batch.pending_customer)
                    context = view.set_pending_customer(batch, data)
                    self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
                    self.assertEqual(context, {
                        'customer_is_known': False,
                        'customer_id': None,
                        'customer_name': 'Fred Flintstone',
                        'phone_number': '555-1234',
                        'email_address': 'fred@mailinator.com',
                        'new_customer_full_name': 'Fred Flintstone',
                        'new_customer_first_name': 'Fred',
                        'new_customer_last_name': 'Flintstone',
                        'new_customer_phone': '555-1234',
                        'new_customer_email': 'fred@mailinator.com',
                    })

    def test_get_product_info(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        local = model.LocalProduct(scancode='07430500132',
                                   brand_name='Bragg',
                                   description='Vinegar',
                                   size='32oz',
                                   case_size=12,
                                   unit_price_reg=decimal.Decimal('5.99'))
        self.session.add(local)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(view, 'batch_handler', create=True, new=handler):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()

                    # typical, for local product
                    context = view.get_product_info(batch, {'product_id': local.uuid.hex})
                    self.assertEqual(context['product_id'], local.uuid.hex)
                    self.assertEqual(context['scancode'], '07430500132')
                    self.assertEqual(context['brand_name'], 'Bragg')
                    self.assertEqual(context['description'], 'Vinegar')
                    self.assertEqual(context['size'], '32oz')
                    self.assertEqual(context['full_description'], 'Bragg Vinegar 32oz')
                    self.assertEqual(context['case_size'], 12)
                    self.assertEqual(context['unit_price_reg'], 5.99)

                    # error if no product_id
                    context = view.get_product_info(batch, {})
                    self.assertEqual(context, {'error': "Must specify a product ID"})

                    # error if product not found
                    mock_uuid = self.app.make_true_uuid()
                    self.assertRaises(ValueError, view.get_product_info,
                                      batch, {'product_id': mock_uuid.hex})

                    with patch.object(handler, 'use_local_products', return_value=False):

                        # external lookup not implemented by default
                        self.assertRaises(NotImplementedError, view.get_product_info,
                                          batch, {'product_id': '42'})

                        # external lookup may return its own error
                        with patch.object(handler, 'get_product_info_external',
                                          return_value={'error': "something smells fishy"}):
                            context = view.get_product_info(batch, {'product_id': '42'})
                            self.assertEqual(context, {'error': "something smells fishy"})

    def test_add_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_UNIT,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # normal pending product
                    result = view.add_item(batch, data)
                    self.assertIn('batch', result)
                    self.assertIn('row', result)
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 1)
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)

                    # external product not yet supported
                    with patch.object(handler, 'use_local_products', return_value=False):
                        with patch.dict(data, product_info='42'):
                            self.assertRaises(NotImplementedError, view.add_item, batch, data)

    def test_update_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.session.flush()
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # missing row uuid
                    result = view.update_item(batch, data)
                    self.assertEqual(result, {'error': "Must specify row UUID"})

                    # row not found
                    with patch.dict(data, uuid=self.app.make_true_uuid()):
                        result = view.update_item(batch, data)
                        self.assertEqual(result, {'error': "Row not found"})

                    # row for wrong batch
                    batch2 = handler.make_batch(self.session, created_by=user)
                    self.session.add(batch2)
                    row2 = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
                    handler.add_row(batch2, row2)
                    self.session.flush()
                    with patch.dict(data, uuid=row2.uuid):
                        result = view.update_item(batch, data)
                        self.assertEqual(result, {'error': "Row is for wrong batch"})

                    # true product not yet supported
                    with patch.object(handler, 'use_local_products', return_value=False):
                        self.assertRaises(NotImplementedError, view.update_item, batch, {
                            'uuid': row.uuid,
                            'product_info': '42',
                            'order_qty': 1,
                            'order_uom': enum.ORDER_UOM_UNIT,
                        })

                    # update row, pending product
                    with patch.dict(data, uuid=row.uuid, order_qty=2):
                        with patch.dict(data['product_info'], scancode='07430500116'):
                            self.assertEqual(row.product_scancode, '07430500132')
                            self.assertEqual(row.order_qty, 1)
                            result = view.update_item(batch, data)
                            self.assertEqual(sorted(result), ['batch', 'row'])
                            self.assertEqual(row.product_scancode, '07430500116')
                            self.assertEqual(row.order_qty, 2)
                            self.assertEqual(row.pending_product.scancode, '07430500116')
                            self.assertEqual(result['row']['product_scancode'], '07430500116')
                            self.assertEqual(result['row']['order_qty'], 2)

    def test_delete_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.session.flush()
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # missing row uuid
                    result = view.delete_item(batch, data)
                    self.assertEqual(result, {'error': "Must specify a row UUID"})

                    # row not found
                    with patch.dict(data, uuid=self.app.make_true_uuid()):
                        result = view.delete_item(batch, data)
                        self.assertEqual(result, {'error': "Row not found"})

                    # row for wrong batch
                    batch2 = handler.make_batch(self.session, created_by=user)
                    self.session.add(batch2)
                    row2 = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
                    handler.add_row(batch2, row2)
                    self.session.flush()
                    with patch.dict(data, uuid=row2.uuid):
                        result = view.delete_item(batch, data)
                        self.assertEqual(result, {'error': "Row is for wrong batch"})

                    # row is deleted
                    data['uuid'] = row.uuid
                    self.assertEqual(len(batch.rows), 1)
                    self.assertEqual(batch.row_count, 1)
                    result = view.delete_item(batch, data)
                    self.assertEqual(sorted(result), ['batch'])
                    self.session.refresh(batch)
                    self.assertEqual(len(batch.rows), 0)
                    self.assertEqual(batch.row_count, 0)

    def test_submit_order(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.assertEqual(len(batch.rows), 1)
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # execute not allowed yet (no customer)
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {'error': "Must assign the customer"})

                    # execute not allowed yet (no phone number)
                    view.set_pending_customer(batch, {'full_name': 'John Doe'})
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {'error': "Customer phone number is required"})

                    # submit/execute ok
                    view.set_pending_customer(batch, {'full_name': 'John Doe',
                                                      'phone_number': '555-1234'})
                    result = view.submit_order(batch, {})
                    self.assertEqual(sorted(result), ['next_url'])
                    self.assertIn('/orders/', result['next_url'])

                    # error (already executed)
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {
                        'error': f"ValueError: batch has already been executed: {batch}",
                    })

    def test_get_default_uom_choices(self):
        enum = self.app.enum
        view = self.make_view()

        uoms = view.get_default_uom_choices()
        self.assertEqual(uoms, [{'key': key, 'value': val}
                                for key, val in enum.ORDER_UOM.items()])

    def test_normalize_batch(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        pending = {
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'unit_price_reg': 5.99,
            'case_size': 12,
        }
        row = handler.add_item(batch, pending, 1, enum.ORDER_UOM_CASE)
        self.session.commit()

        data = view.normalize_batch(batch)
        self.assertEqual(data, {
            'uuid': batch.uuid.hex,
            'total_price': '71.880',
            'total_price_display': '$71.88',
            'status_code': None,
            'status_text': None,
        })

    def test_normalize_row(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()
        view.batch_handler = handler

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        # add 1st row w/ pending product
        pending = {
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'unit_price_reg': 5.99,
            'case_size': 12,
            'vendor_name': 'Acme Warehouse',
            'vendor_item_code': '1234',
        }
        row1 = handler.add_item(batch, pending, 2, enum.ORDER_UOM_CASE)

        # typical, pending product
        data = view.normalize_row(row1)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['uuid'], row1.uuid.hex)
        self.assertEqual(data['sequence'], 1)
        self.assertIsNone(data['product_id'])
        self.assertEqual(data['product_scancode'], '07430500132')
        self.assertEqual(data['product_full_description'], 'Bragg Vinegar 32oz')
        self.assertEqual(data['case_size'], 12)
        self.assertEqual(data['vendor_name'], 'Acme Warehouse')
        self.assertEqual(data['order_qty'], 2)
        self.assertEqual(data['order_uom'], 'CS')
        self.assertEqual(data['order_qty_display'], '2 Cases (&times; 12 = 24 Units)')
        self.assertEqual(data['unit_price_reg'], 5.99)
        self.assertEqual(data['unit_price_reg_display'], '$5.99')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 5.99)
        self.assertEqual(data['unit_price_quoted_display'], '$5.99')
        self.assertEqual(data['case_price_quoted'], 71.88)
        self.assertEqual(data['case_price_quoted_display'], '$71.88')
        self.assertEqual(data['total_price'], 143.76)
        self.assertEqual(data['total_price_display'], '$143.76')
        self.assertIsNone(data['special_order'])
        self.assertEqual(data['status_code'], row1.STATUS_OK)
        self.assertEqual(data['pending_product'], {
            'uuid': row1.pending_product_uuid.hex,
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'department_id': None,
            'department_name': None,
            'unit_price_reg': 5.99,
            'vendor_name': 'Acme Warehouse',
            'vendor_item_code': '1234',
            'unit_cost': None,
            'case_size': 12.0,
            'notes': None,
            'special_order': None,
        })

        # the next few tests will morph 1st row..

        # unknown case size
        row1.pending_product.case_size = None
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertIsNone(data['case_size'])
        self.assertEqual(data['order_qty_display'], '2 Cases (&times; ?? = ?? Units)')

        # order by unit
        row1.order_uom = enum.ORDER_UOM_UNIT
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertEqual(data['order_uom'], enum.ORDER_UOM_UNIT)
        self.assertEqual(data['order_qty_display'], '2 Units')

        # item on sale
        row1.pending_product.case_size = 12
        row1.unit_price_sale = decimal.Decimal('5.19')
        row1.sale_ends = datetime.datetime(2099, 1, 5, 20, 32)
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertEqual(data['unit_price_sale'], 5.19)
        self.assertEqual(data['unit_price_sale_display'], '$5.19')
        self.assertEqual(data['sale_ends'], '2099-01-05 20:32:00')
        self.assertEqual(data['sale_ends_display'], '2099-01-05')
        self.assertEqual(data['unit_price_quoted'], 5.19)
        self.assertEqual(data['unit_price_quoted_display'], '$5.19')
        self.assertEqual(data['case_price_quoted'], 62.28)
        self.assertEqual(data['case_price_quoted_display'], '$62.28')

        # add 2nd row w/ local product
        local = model.LocalProduct(brand_name="Lay's",
                                   description="Potato Chips",
                                   vendor_name='Acme Distribution',
                                   unit_price_reg=3.29)
        self.session.add(local)
        self.session.flush()
        row2 = handler.add_item(batch, local.uuid.hex, 1, enum.ORDER_UOM_UNIT)

        # typical, local product
        data = view.normalize_row(row2)
        self.assertEqual(data['uuid'], row2.uuid.hex)
        self.assertEqual(data['sequence'], 2)
        self.assertEqual(data['product_id'], local.uuid.hex)
        self.assertIsNone(data['product_scancode'])
        self.assertEqual(data['product_full_description'], "Lay's Potato Chips")
        self.assertIsNone(data['case_size'])
        self.assertEqual(data['vendor_name'], 'Acme Distribution')
        self.assertEqual(data['order_qty'], 1)
        self.assertEqual(data['order_uom'], 'EA')
        self.assertEqual(data['order_qty_display'], '1 Units')
        self.assertEqual(data['unit_price_reg'], 3.29)
        self.assertEqual(data['unit_price_reg_display'], '$3.29')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 3.29)
        self.assertEqual(data['unit_price_quoted_display'], '$3.29')
        self.assertIsNone(data['case_price_quoted'])
        self.assertEqual(data['case_price_quoted_display'], '')
        self.assertEqual(data['total_price'], 3.29)
        self.assertEqual(data['total_price_display'], '$3.29')
        self.assertIsNone(data['special_order'])
        self.assertEqual(data['status_code'], row2.STATUS_OK)
        self.assertNotIn('pending_product', data)

        # the next few tests will morph 2nd row..

        def refresh_external(row):
            row.product_scancode = '012345'
            row.product_brand = 'Acme'
            row.product_description = 'Bricks'
            row.product_size = '1 ton'
            row.product_weighed = True
            row.department_id = 1
            row.department_name = "Bricks & Mortar"
            row.special_order = False
            row.case_size = None
            row.unit_cost = decimal.Decimal('599.99')
            row.unit_price_reg = decimal.Decimal('999.99')

        # typical, external product
        with patch.object(handler, 'use_local_products', return_value=False):
            with patch.object(handler, 'refresh_row_from_external_product', new=refresh_external):
                handler.update_item(row2, '42', 1, enum.ORDER_UOM_UNIT)
                data = view.normalize_row(row2)
        self.assertEqual(data['uuid'], row2.uuid.hex)
        self.assertEqual(data['sequence'], 2)
        self.assertEqual(data['product_id'], '42')
        self.assertEqual(data['product_scancode'], '012345')
        self.assertEqual(data['product_full_description'], 'Acme Bricks 1 ton')
        self.assertIsNone(data['case_size'])
        self.assertNotIn('vendor_name', data) # TODO
        self.assertEqual(data['order_qty'], 1)
        self.assertEqual(data['order_uom'], 'EA')
        self.assertEqual(data['order_qty_display'], '1 Units')
        self.assertEqual(data['unit_price_reg'], 999.99)
        self.assertEqual(data['unit_price_reg_display'], '$999.99')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 999.99)
        self.assertEqual(data['unit_price_quoted_display'], '$999.99')
        self.assertIsNone(data['case_price_quoted'])
        self.assertEqual(data['case_price_quoted_display'], '')
        self.assertEqual(data['total_price'], 999.99)
        self.assertEqual(data['total_price_display'], '$999.99')
        self.assertFalse(data['special_order'])
        self.assertEqual(data['status_code'], row2.STATUS_OK)
        self.assertNotIn('pending_product', data)

    def test_get_instance_title(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        self.session.add(order)
        self.session.flush()

        title = view.get_instance_title(order)
        self.assertEqual(title, "#42 for Fred Flintstone")

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.commit()

        # viewing (no customer)
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=order)
            # nb. this is to avoid include/exclude ambiguity
            form.remove('items')
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIn('pending_customer', form)
            self.assertIsInstance(schema['total_price'].typ, WuttaMoney)

        # assign local customer
        local = model.LocalCustomer(first_name='Jack', last_name='Black',
                                    phone_number='555-1234')
        self.session.add(local)
        order.local_customer = local
        self.session.flush()

        # viewing (local customer)
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=order)
            # nb. this is to avoid include/exclude ambiguity
            form.remove('items')
            view.configure_form(form)
            self.assertNotIn('pending_customer', form)
            schema = form.get_schema()
            self.assertIsInstance(schema['total_price'].typ, WuttaMoney)

    def test_get_xref_buttons(self):
        self.pyramid_config.add_route('neworder_batches.view', '/batch/neworder/{uuid}')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):

            # nb. this requires perm to view batch
            with patch.object(self.request, 'is_root', new=True):

                # order has no batch, so no buttons
                buttons = view.get_xref_buttons(order)
                self.assertEqual(buttons, [])

                # mock up a batch to get a button
                batch = handler.make_batch(self.session,
                                           id=order.order_id,
                                           created_by=user,
                                           executed=datetime.datetime.now(),
                                           executed_by=user)
                self.session.add(batch)
                self.session.flush()
                buttons = view.get_xref_buttons(order)
                self.assertEqual(len(buttons), 1)
                button = buttons[0]
                self.assertIn("View the Batch", button)

    def test_get_row_grid_data(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        order.items.append(model.OrderItem(product_id='07430500132',
                                           product_scancode='07430500132',
                                           order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                           status_code=enum.ORDER_ITEM_STATUS_INITIATED))
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            query = view.get_row_grid_data(order)
            self.assertIsInstance(query, orm.Query)
            items = query.all()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].product_scancode, '07430500132')

    def test_configure_row_grid(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        order.items.append(model.OrderItem(product_id='07430500132',
                                           product_scancode='07430500132',
                                           order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                           status_code=enum.ORDER_ITEM_STATUS_INITIATED))
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            grid = view.make_grid(model_class=model.OrderItem, data=order.items)
            self.assertNotIn('product_scancode', grid.linked_columns)
            view.configure_row_grid(grid)
            self.assertIn('product_scancode', grid.linked_columns)

    def test_render_status_code(self):
        enum = self.app.enum
        view = self.make_view()
        result = view.render_status_code(None, None, enum.ORDER_ITEM_STATUS_INITIATED)
        self.assertEqual(result, "initiated")
        self.assertEqual(result, enum.ORDER_ITEM_STATUS[enum.ORDER_ITEM_STATUS_INITIATED])

    def test_get_row_action_url_view(self):
        self.pyramid_config.add_route('order_items.view', '/order-items/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        item = model.OrderItem(product_id='07430500132',
                               product_scancode='07430500132',
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        url = view.get_row_action_url_view(item, 0)
        self.assertIn(f'/order-items/{item.uuid}', url)

    def test_configure(self):
        self.pyramid_config.add_route('home', '/')
        self.pyramid_config.add_route('login', '/auth/login')
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        view = self.make_view()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.multiple(self.config, usedb=True, preferdb=True):

                # sanity check
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertIsNone(allowed)
                self.assertEqual(self.session.query(model.Setting).count(), 0)

                # fetch initial page
                response = view.configure()
                self.assertIsInstance(response, Response)
                self.assertNotIsInstance(response, HTTPFound)
                self.session.flush()
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertIsNone(allowed)
                self.assertEqual(self.session.query(model.Setting).count(), 0)

                # post new settings
                with patch.multiple(self.request, create=True,
                                    method='POST',
                                    POST={
                                        'sideshow.orders.allow_unknown_products': 'true',
                                    }):
                    response = view.configure()
                self.assertIsInstance(response, HTTPFound)
                self.session.flush()
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertTrue(allowed)
                self.assertTrue(self.session.query(model.Setting).count() > 1)


class TestOrderItemView(WebTestCase):

    def make_view(self):
        return mod.OrderItemView(self.request)

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)
        self.assertNotIn('order_id', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('order_id', grid.linked_columns)

    def test_render_order_id(self):
        model = self.app.model
        view = self.make_view()
        order = model.Order(order_id=42)
        item = model.OrderItem()
        order.items.append(item)
        self.assertEqual(view.render_order_id(item, None, None), 42)

    def test_render_status_code(self):
        enum = self.app.enum
        view = self.make_view()
        self.assertEqual(view.render_status_code(None, None, enum.ORDER_ITEM_STATUS_INITIATED),
                         'initiated')

    def test_get_instance_title(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        item = model.OrderItem(product_brand='Bragg',
                               product_description='Vinegar',
                               product_size='32oz',
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        title = view.get_instance_title(item)
        self.assertEqual(title, "(initiated) Bragg Vinegar 32oz")

    def test_configure_form(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_INITIATED)

        # viewing, w/ pending product
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=item)
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIsInstance(schema['order'].typ, OrderRef)
            self.assertIn('pending_product', form)
            self.assertIsInstance(schema['pending_product'].typ, PendingProductRef)

        # viewing, w/ local product
        local = model.LocalProduct()
        item.local_product = local
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=item)
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIsInstance(schema['order'].typ, OrderRef)
            self.assertNotIn('pending_product', form)

    def test_get_xref_buttons(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        item = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        # nb. this requires perms
        with patch.object(self.request, 'is_root', new=True):

            # one button by default
            buttons = view.get_xref_buttons(item)
            self.assertEqual(len(buttons), 1)
            self.assertIn("View the Order", buttons[0])
