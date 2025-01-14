# -*- coding: utf-8; -*-

import datetime
import decimal

import sqlalchemy as sa

from corepos.db.office_op import model as op_model, Session as OpSession

from wuttjamaican.testing import DataTestCase

from sideshow_corepos.batch import neworder as mod


class TestNewOrderBatchHandler(DataTestCase):

    def setUp(self):
        super().setUp()

        self.op_engine = sa.create_engine('sqlite://')
        self.config.core_office_op_engines = {'default': self.op_engine}
        self.config.core_office_op_engine = self.op_engine

        op_model.Base.metadata.create_all(bind=self.op_engine)

        self.op_session = OpSession(bind=self.op_engine)

    def tearDown(self):
        self.op_session.close()
        super().tearDown()

    def make_config(self, **kwargs):
        config = super().make_config(**kwargs)
        config.setdefault('wutta.enum_spec', 'sideshow.enum')
        return config

    def make_handler(self):
        return mod.NewOrderBatchHandler(self.config)

    def test_autocomplete_cutomers_external(self):
        handler = self.make_handler()

        # empty results by default
        self.assertEqual(handler.autocomplete_customers_external(self.session, 'foo'), [])

        # add a member
        member = op_model.MemberInfo(card_number=42)
        self.op_session.add(member)
        customer = op_model.CustomerClassic(first_name="Chuck", last_name="Norris",
                                            last_change=datetime.datetime.now())
        member.customers.append(customer)
        self.op_session.add(customer)
        self.op_session.flush()

        # search for chuck finds chuck
        results = handler.autocomplete_customers_external(self.session, 'chuck')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': '42',
            'label': "Chuck Norris",
        })

        # search for sally finds nothing
        self.assertEqual(handler.autocomplete_customers_external(self.session, 'sally'), [])

    def test_refresh_batch_from_external_customer(self):
        model = self.app.model
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        # add a member
        member = op_model.MemberInfo(card_number=42, phone='555-1234', email='chuck@example.com')
        self.op_session.add(member)
        customer = op_model.CustomerClassic(first_name="Chuck", last_name="Norris",
                                            last_change=datetime.datetime.now())
        member.customers.append(customer)
        self.op_session.add(customer)
        self.op_session.flush()

        # error if invalid customer_id
        batch.customer_id = 'BreakThings!'
        self.assertRaises(ValueError, handler.refresh_batch_from_external_customer, batch)

        # error if customer not found
        batch.customer_id = '9999'
        self.assertRaises(ValueError, handler.refresh_batch_from_external_customer, batch)

        # batch should reflect customer info
        batch.customer_id = '42'
        self.assertIsNone(batch.customer_name)
        self.assertIsNone(batch.phone_number)
        self.assertIsNone(batch.email_address)
        handler.refresh_batch_from_external_customer(batch)
        self.assertEqual(batch.customer_name, "Chuck Norris")
        self.assertEqual(batch.phone_number, '555-1234')
        self.assertEqual(batch.email_address, 'chuck@example.com')

    def test_autocomplete_products_local(self):
        handler = self.make_handler()

        # empty results by default
        self.assertEqual(handler.autocomplete_products_external(self.session, 'foo'), [])

        # add a product
        product = op_model.Product(upc='07430500132', brand="Bragg's",
                                   description="Vinegar", size='32oz')
        self.op_session.add(product)
        self.op_session.commit()

        # search for vinegar finds product
        results = handler.autocomplete_products_external(self.session, 'vinegar')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': '07430500132',
            'label': "Bragg's Vinegar 32oz",
        })

        # search for brag finds product
        results = handler.autocomplete_products_external(self.session, 'brag')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {
            'value': '07430500132',
            'label': "Bragg's Vinegar 32oz",
        })

        # search for juice finds nothing
        self.assertEqual(handler.autocomplete_products_external(self.session, 'juice'), [])

    def test_get_case_size_for_external_product(self):
        handler = self.make_handler()

        # null
        product = op_model.Product(upc='07430500132', brand="Bragg's",
                                   description="Vinegar", size='32oz')
        self.op_session.add(product)
        self.op_session.commit()
        self.op_session.refresh(product)
        self.assertIsNone(handler.get_case_size_for_external_product(product))

        # typical
        vendor = op_model.Vendor(id=42, name='Acme Distributors')
        self.op_session.add(vendor)
        item = op_model.VendorItem(vendor=vendor, sku='1234', units=12.34,
                                   vendor_item_id=1)
        product.vendor_items.append(item)
        self.op_session.commit()
        self.op_session.refresh(product)
        self.assertEqual(handler.get_case_size_for_external_product(product),
                         decimal.Decimal('12.3400'))

    def test_get_unit_price_reg_for_external_product(self):
        handler = self.make_handler()

        # null
        product = op_model.Product(upc='07430500132', brand="Bragg's",
                                   description="Vinegar", size='32oz')
        self.op_session.add(product)
        self.op_session.commit()
        self.op_session.refresh(product)
        self.assertIsNone(handler.get_unit_price_reg_for_external_product(product))

        # typical
        product.normal_price = 4.19
        self.op_session.commit()
        self.op_session.refresh(product)
        self.assertEqual(handler.get_unit_price_reg_for_external_product(product),
                         decimal.Decimal('4.19'))

    def test_get_product_info_external(self):
        model = self.app.model
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        vendor = op_model.Vendor(id=42, name='Acme Distributors')
        self.op_session.add(vendor)
        product = op_model.Product(upc='07430500132', brand="Bragg",
                                   description="Vinegar", size='32oz',
                                   normal_price=4.19)
        item = op_model.VendorItem(vendor=vendor, sku='1234', units=12.34,
                                   vendor_item_id=1)
        product.vendor_items.append(item)
        self.op_session.add(product)
        self.op_session.commit()

        # typical
        info = handler.get_product_info_external(self.session, '07430500132')
        self.assertEqual(info['product_id'], '07430500132')
        self.assertEqual(info['scancode'], '07430500132')
        self.assertEqual(info['brand_name'], 'Bragg')
        self.assertEqual(info['description'], 'Vinegar')
        self.assertEqual(info['size'], '32oz')
        self.assertEqual(info['full_description'], 'Bragg Vinegar 32oz')
        self.assertEqual(info['case_size'], decimal.Decimal('12.3400'))
        self.assertEqual(info['unit_price_reg'], decimal.Decimal('4.19'))

        # error if no product_id
        self.assertRaises(ValueError, handler.get_product_info_external, self.session, None)

        # error if product not found
        self.assertRaises(ValueError, handler.get_product_info_external, self.session, 'BADUPC')

    def test_refresh_row_from_external_product(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        row = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.add(row)
        self.session.flush()

        vendor = op_model.Vendor(id=42, name='Acme Distributors')
        self.op_session.add(vendor)
        product = op_model.Product(upc='07430500132', brand="Bragg",
                                   description="Vinegar", size='32oz',
                                   normal_price=4.19)
        item = op_model.VendorItem(vendor=vendor, sku='1234', units=12.34,
                                   vendor_item_id=1)
        product.vendor_items.append(item)
        self.op_session.add(product)
        self.op_session.commit()

        # error if invalid product_id
        row.product_id = 'BreakThings!'
        self.assertRaises(ValueError, handler.refresh_row_from_external_product, row)

        # error if product not found
        row.product_id = '9999'
        self.assertRaises(ValueError, handler.refresh_row_from_external_product, row)

        # row should reflect product info
        row.product_id = '07430500132'
        self.assertIsNone(row.product_scancode)
        self.assertIsNone(row.product_brand)
        self.assertIsNone(row.product_description)
        self.assertIsNone(row.product_size)
        self.assertIsNone(row.case_size)
        self.assertIsNone(row.unit_price_reg)
        handler.refresh_row_from_external_product(row)
        self.assertEqual(row.product_scancode, '07430500132')
        self.assertEqual(row.product_brand, "Bragg")
        self.assertEqual(row.product_description, "Vinegar")
        self.assertEqual(row.product_size, "32oz")
        self.assertEqual(row.case_size, decimal.Decimal('12.3400'))
        self.assertEqual(row.unit_price_reg, decimal.Decimal('4.19'))
