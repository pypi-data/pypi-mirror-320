# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow-COREPOS -- Case/Special Order Tracker for CORE-POS
#  Copyright © 2025 Lance Edgar
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
New Order Batch Handler for CORE-POS
"""

import decimal

import sqlalchemy as sa
from sqlalchemy import orm

from sideshow.batch import neworder as base


class NewOrderBatchHandler(base.NewOrderBatchHandler):
    """
    Custom :term:`handler` for :term:`new order batches <new order
    batch>` which can use CORE-POS as external data source for
    customers and products.

    See parent class
    :class:`~sideshow:sideshow.batch.neworder.NewOrderBatchHandler`
    for more info.
    """

    def autocomplete_customers_external(self, session, term, user=None):
        """ """
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        op_session = corepos.make_session_office_op()

        # base query
        query = op_session.query(op_model.CustomerClassic)\
                          .join(op_model.MemberInfo,
                                op_model.MemberInfo.card_number == op_model.CustomerClassic.card_number)

        # filter query
        criteria = []
        for word in term.split():
            criteria.append(sa.or_(
                op_model.CustomerClassic.first_name.ilike(f'%{word}%'),
                op_model.CustomerClassic.last_name.ilike(f'%{word}%')))
        query = query.filter(sa.and_(*criteria))

        # sort query
        query = query.order_by(op_model.CustomerClassic.first_name,
                               op_model.CustomerClassic.last_name)

        # get data
        # TODO: need max_results option
        customers = query.all()

        # get results
        def result(customer):
            return {'value': str(customer.card_number),
                    'label': str(customer)}
        results = [result(c) for c in customers]

        op_session.close()
        return results

    def refresh_batch_from_external_customer(self, batch):
        """ """
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        op_session = corepos.make_session_office_op()

        if not batch.customer_id.isdigit():
            raise ValueError(f"invalid CORE-POS customer card number: {batch.customer_id}")

        try:
            customer = op_session.query(op_model.CustomerClassic)\
                                 .join(op_model.MemberInfo,
                                       op_model.MemberInfo.card_number == op_model.CustomerClassic.card_number)\
                                 .filter(op_model.CustomerClassic.card_number == int(batch.customer_id))\
                                 .filter(op_model.CustomerClassic.person_number == 1)\
                                 .options(orm.joinedload(op_model.CustomerClassic.member_info))\
                                 .one()
        except orm.exc.NoResultFound:
            raise ValueError(f"CORE-POS Customer not found: {batch.customer_id}")

        batch.customer_name = str(customer)
        batch.phone_number = customer.member_info.phone
        batch.email_address = customer.member_info.email

        op_session.close()

    def autocomplete_products_external(self, session, term, user=None):
        """ """
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        op_session = corepos.make_session_office_op()

        # base query
        query = op_session.query(op_model.Product)

        # filter query
        criteria = []
        for word in term.split():
            criteria.append(sa.or_(
                op_model.Product.brand.ilike(f'%{word}%'),
                op_model.Product.description.ilike(f'%{word}%')))
        query = query.filter(sa.and_(*criteria))

        # sort query
        query = query.order_by(op_model.Product.brand,
                               op_model.Product.description)

        # get data
        # TODO: need max_results option
        products = query.all()

        # get results
        def result(product):
            return {'value': product.upc,
                    'label': self.app.make_full_name(product.brand,
                                                     product.description,
                                                     product.size)}
        results = [result(c) for c in products]

        op_session.close()
        return results

    def get_product_info_external(self, session, product_id, user=None):
        """ """
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        op_session = corepos.make_session_office_op()

        try:
            product = op_session.query(op_model.Product)\
                                .filter(op_model.Product.upc == product_id)\
                                .one()
        except orm.exc.NoResultFound:
            raise ValueError(f"CORE-POS Product not found: {product_id}")

        data = {
            'product_id': product.upc,
            'scancode': product.upc,
            'brand_name': product.brand,
            'description': product.description,
            'size': product.size,
            'full_description': self.app.make_full_name(product.brand,
                                                        product.description,
                                                        product.size),
            'weighed': product.scale,
            'special_order': False,
            'department_id': product.department_number,
            'department_name': product.department.name if product.department else None,
            'case_size': self.get_case_size_for_external_product(product),
            'unit_price_reg': self.get_unit_price_reg_for_external_product(product),
            # TODO
            # 'vendor_name': product.vendor_name,
            # 'vendor_item_code': product.vendor_item_code,
        }

        op_session.close()
        return data

    def refresh_row_from_external_product(self, row):
        """ """
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        op_session = corepos.make_session_office_op()

        try:
            product = op_session.query(op_model.Product)\
                                .filter(op_model.Product.upc == row.product_id)\
                                .one()
        except orm.exc.NoResultFound:
            raise ValueError(f"CORE-POS Product not found: {row.product_id}")

        row.product_scancode = product.upc
        row.product_brand = product.brand
        row.product_description = product.description
        row.product_size = product.size
        row.product_weighed = product.scale
        row.department_id = product.department_number
        row.department_name = product.department.name if product.department else None
        row.special_order = False
        row.case_size = self.get_case_size_for_external_product(product)
        row.unit_cost = product.cost
        row.unit_price_reg = self.get_unit_price_reg_for_external_product(product)

        op_session.close()

    def get_case_size_for_external_product(self, product):
        """ """
        if product.vendor_items:
            item = product.vendor_items[0]
            if item.units is not None:
                return decimal.Decimal(f'{item.units:0.4f}')

    def get_unit_price_reg_for_external_product(self, product):
        """ """
        if product.normal_price is not None:
            return decimal.Decimal(f'{product.normal_price:0.3f}')
