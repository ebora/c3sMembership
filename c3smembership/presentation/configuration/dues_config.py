# -*- coding: utf-8 -*-
"""
Pyramid application configuration for membership dues.
"""

import os

from c3smembership.data.model.base import DBSession
from c3smembership.data.model.base.c3smember import C3sMember
from c3smembership.data.model.base.dues15invoice import Dues15Invoice
from c3smembership.data.repository.payment_repository import \
    PaymentRepository

from c3smembership.business.dues_invoice_archiving import (
    DuesInvoiceArchiving
)
from c3smembership.business.payment_information import PaymentInformation

from c3smembership.presentation.configuration import Configuration
from c3smembership.presentation.views.dues_2015 import (
    make_invoice_pdf_pdflatex,
    make_reversal_pdf_pdflatex,
)
from c3smembership.presentation.views.payment_list import \
    payment_content_size_provider


class DuesConfig(Configuration):
    """
    Configuration for membership dues.
    """

    def configure(self):
        """
        Add the configuration of the module to the Pyramid configuration.
        """
        self.configure_routes()
        self.configure_registry()

    def configure_registry(self):
        """
        Configure the registry to contain the membership dues business layer.
        """

        # Invoices
        invoices_archive_path = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../invoices/'))
        self.config.registry.dues_invoice_archiving = DuesInvoiceArchiving(
            DBSession,
            C3sMember,
            Dues15Invoice,
            make_invoice_pdf_pdflatex,
            make_reversal_pdf_pdflatex,
            invoices_archive_path)

        # Payments
        self.config.registry.payment_information = PaymentInformation(
            PaymentRepository())
        self.config.make_pagination_route(
            'payment_list',
            payment_content_size_provider,
            sort_property_default='date',
            page_size_default=30)

    def configure_routes(self):
        """
        Configure the membership dues routes.
        """
        routes = [
            # Dues
            ('dues', '/dues'),

            # membership dues 2015
            ('send_dues15_invoice_email', '/dues15_invoice/{member_id}'),
            ('send_dues15_invoice_batch', '/dues15_invoice_batch'),
            (
                'make_dues15_invoice_no_pdf',
                '/dues15_invoice_no/{code}/C3S-dues15-{i}.pdf'
            ),
            # for backward compatibility
            (
                'make_dues15_invoice_no_pdf_email',
                '/dues15_invoice_no/{email}/{code}/C3S-dues15-{i}.pdf'
            ),
            ('dues15_reduction', '/dues15_reduction/{member_id}'),
            (
                'make_dues15_reversal_invoice_pdf',
                '/dues15_reversal/{code}/C3S-dues15-{no}-S.pdf'),
            # for backward compatibility
            (
                'make_dues15_reversal_invoice_pdf_email',
                '/dues15_reversal/{email}/{code}/C3S-dues15-{no}-S.pdf'
            ),
            ('dues15_notice', '/dues15_notice/{member_id}'),
            ('dues15_listing', '/dues15_listing'),

            # membership dues 2016
            ('send_dues16_invoice_email', '/dues16_invoice/{member_id}'),
            ('send_dues16_invoice_batch', '/dues16_invoice_batch'),
            (
                'make_dues16_invoice_no_pdf',
                '/dues16_invoice_no/{code}/C3S-dues16-{i}.pdf'
            ),
            # for backward compatibility
            (
                'make_dues16_invoice_no_pdf_email',
                '/dues16_invoice_no/{email}/{code}/C3S-dues16-{i}.pdf'
            ),
            ('dues16_reduction', '/dues16_reduction/{member_id}'),
            (
                'make_dues16_reversal_invoice_pdf',
                '/dues16_reversal/{code}/C3S-dues16-{no}-S.pdf'
            ),
            # for backward compatibility
            (
                'make_dues16_reversal_invoice_pdf_email',
                '/dues16_reversal/{email}/{code}/C3S-dues16-{no}-S.pdf'
            ),
            ('dues16_notice', '/dues16_notice/{member_id}'),
            ('dues16_listing', '/dues16_listing'),

            # membership dues 2017
            ('send_dues17_invoice_email', '/dues17_invoice/{member_id}'),
            ('send_dues17_invoice_batch', '/dues17_invoice_batch'),
            (
                'make_dues17_invoice_no_pdf',
                '/dues17_invoice_no/{code}/C3S-dues17-{i}.pdf'
            ),
            ('dues17_reduction', '/dues17_reduction/{member_id}'),
            (
                'make_dues17_reversal_invoice_pdf',
                '/dues17_reversal/{code}/C3S-dues17-{no}-S.pdf'
            ),
            ('dues17_notice', '/dues17_notice/{member_id}'),
            ('dues17_listing', '/dues17_listing'),

            # membership dues 2018
            (
                'dues18_invoice_pdf_backend',
                '/dues18_invoice/C3S-dues18-{i}.pdf'
            ),
            ('send_dues18_invoice_email', '/dues18_invoice/{member_id}'),
            ('send_dues18_invoice_batch', '/dues18_invoice_batch'),
            (
                'make_dues18_invoice_no_pdf',
                '/dues18_invoice_no/{code}/C3S-dues18-{i}.pdf'
            ),
            ('dues18_reduction', '/dues18_reduction/{member_id}'),

            (
                'dues18_reversal_pdf_backend',
                '/dues18_reversal/C3S-dues18-{i}-S.pdf'
            ),
            (
                'make_dues18_reversal_invoice_pdf',
                '/dues18_reversal/{code}/C3S-dues18-{no}-S.pdf'
            ),
            ('dues18_notice', '/dues18_notice/{member_id}'),
            ('dues18_listing', '/dues18_listing'),

            # Invoices
            ('batch_archive_pdf_invoices', '/batch_archive_pdf_invoices'),

            # Payments
            ('payment_list', '/payments'),
        ]
        self._add_routes(routes)
