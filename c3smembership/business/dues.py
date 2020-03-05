# -*- coding: utf-8 -*-
"""
Handle membership dues

TODO: The business layer must use a data layer repository for data manipulation
instead of using the database session and records directly.
"""

from datetime import datetime
from decimal import Decimal
import random
import string

from pyramid_mailer.message import Message

from c3smembership.data.model.base import DBSession
from c3smembership.data.model.base.dues15invoice import Dues15Invoice
from c3smembership.data.model.base.dues16invoice import Dues16Invoice
from c3smembership.data.model.base.dues17invoice import Dues17Invoice
from c3smembership.data.model.base.dues18invoice import Dues18Invoice
from c3smembership.data.model.base.dues19invoice import Dues19Invoice
from c3smembership.data.model.base.dues20invoice import Dues20Invoice
from c3smembership.data.repository.dues_invoice_repository import \
    DuesInvoiceRepository

from c3smembership.business.dues_calculation import QuarterlyDuesCalculator
from c3smembership.business.dues_texts import (
    make_dues15_invoice_email,
    make_dues16_invoice_email,
    make_dues17_invoice_email,
    make_dues18_invoice_email,
    make_dues19_invoice_email,
    make_dues20_invoice_email,
    make_dues_invoice_investing_email,
    make_dues_invoice_legalentity_email,
)

from c3smembership.mail_utils import (
    send_message, )


def make_random_string():
    """
    Generate a random string used as a dues token
    """
    return u''.join(random.choice(string.ascii_uppercase) for x in range(10))


def get_dues_calculator(year):
    """
    Get the dues calculator for the year

    The dues calculator bases on 50 € dues per year and calculates a quarterly
    amount.
    """
    return QuarterlyDuesCalculator(Decimal('50'), year)


def calculate_dues_create_invoice(year, member):
    """
    Calculate the dues and create an invoice record

    The invoice PDF is not created. If the dues were created before, the
    existing invoice record will be returned.
    """
    invoice = None
    # Get invoice if it exists already
    if invoice_calculated(year, member) is True:
        invoice = DuesInvoiceRepository.get_by_number(
            get_year_invoice_number(year, member), year)
    else:
        # Otherweise calculate dues and invoice for normal members
        if 'normal' in member.membership_type:
            dues_calculator = get_dues_calculator(year)
            dues_amount, dues_code, _ = \
                dues_calculator.calculate(member)
            invoice = create_invoice(year, member, dues_amount)
            store_dues(year, member, dues_amount, dues_code,
                       invoice.invoice_no, invoice.token)
            DBSession().flush()
    return invoice


def create_invoice(year, member, dues_amount):
    """
    Create the invoice record

    The invoice PDF is not created.
    """
    randomstring = make_random_string()

    max_invoice_no = DuesInvoiceRepository.get_max_invoice_number(year)
    new_invoice_no = int(max_invoice_no) + 1

    dues_invoice_class = get_dues_invoice_class(year)
    invoice = dues_invoice_class(
        invoice_no=new_invoice_no,
        invoice_no_string=(u'C3S-dues{0}-{1}'.format(
            year,
            str(new_invoice_no).zfill(4))),
        invoice_date=datetime.now(),
        invoice_amount=u'' + str(dues_amount),
        member_id=member.id,
        membership_no=member.membership_number,
        email=member.email,
        token=randomstring,
    )

    DBSession().add(invoice)
    return invoice


def store_dues(year, member, dues_amount, dues_code, invoice_no,
               invoice_token):
    """
    Store the dues

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    if year == 2015:
        member.set_dues15_amount(dues_amount)
        member.dues15_start = dues_code
        member.dues15_invoice_no = invoice_no
        member.dues15_token = invoice_token
    if year == 2016:
        member.set_dues16_amount(dues_amount)
        member.dues16_start = dues_code
        member.dues16_invoice_no = invoice_no
        member.dues16_token = invoice_token
    if year == 2017:
        member.set_dues17_amount(dues_amount)
        member.dues17_start = dues_code
        member.dues17_invoice_no = invoice_no
        member.dues17_token = invoice_token
    if year == 2018:
        member.set_dues18_amount(dues_amount)
        member.dues18_start = dues_code
        member.dues18_invoice_no = invoice_no
        member.dues18_token = invoice_token
    if year == 2019:
        member.set_dues19_amount(dues_amount)
        member.dues19_start = dues_code
        member.dues19_invoice_no = invoice_no
        member.dues19_token = invoice_token
    if year == 2020:
        member.set_dues20_amount(dues_amount)
        member.dues20_start = dues_code
        member.dues20_invoice_no = invoice_no
        member.dues20_token = invoice_token


def send_dues_email(request, year, member, invoice):
    """
    Send the dues email depending on the membership type

    Normal members get an email with the invoice URL. Investing members get a
    recommendation of how much dues to pay.
    """
    if 'normal' in member.membership_type:
        message = create_dues_email_normal(request, year, member, invoice)
    elif 'investing' in member.membership_type:
        message = create_dues_email_investing(request, member)

    if 'true' in request.registry.settings['testing.mail_to_console']:
        # pylint: disable=superfluous-parens
        print(message.body.encode('utf-8'))
    else:
        send_message(request, message)
    record_dues_email_sent(year, member)


def create_dues_email_normal(request, year, member, invoice):
    """
    Create the dues email for normal members
    """
    dues_calculator = get_dues_calculator(year)
    dues_description = dues_calculator.get_description(
        dues_calculator.calculate_quarter(member), member.locale)
    start_quarter = dues_description
    invoice_url = get_year_invoice_url(request, year, member)
    make_dues_invoice_email = make_year_dues_invoice_email(year)
    email_subject, email_body = make_dues_invoice_email(
        member, invoice, invoice_url, start_quarter)
    return Message(
        subject=email_subject,
        sender=request.registry.settings['c3smembership.notification_sender'],
        recipients=[member.email],
        body=email_body,
    )


def create_dues_email_investing(request, member):
    """
    Create the dues email for investing members
    """
    if member.is_legalentity:
        email_subject, email_body = \
            make_dues_invoice_legalentity_email(member)
    else:
        email_subject, email_body = \
            make_dues_invoice_investing_email(member)
    return Message(
        subject=email_subject,
        sender=request.registry.settings['c3smembership.notification_sender'],
        recipients=[member.email],
        body=email_body,
    )


def get_year_invoice_url(request, year, member):
    """
    Get the invoice url for the year

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    year_invoice_url = ''
    if year == 2015:
        year_invoice_url = request.route_url(
            'make_dues15_invoice_no_pdf',
            email=member.email,
            code=member.dues15_token,
            i=str(member.dues15_invoice_no).zfill(4))
    if year == 2016:
        year_invoice_url = request.route_url(
            'make_dues16_invoice_no_pdf',
            email=member.email,
            code=member.dues16_token,
            i=str(member.dues16_invoice_no).zfill(4))
    if year == 2017:
        year_invoice_url = request.route_url(
            'make_dues17_invoice_no_pdf',
            email=member.email,
            code=member.dues17_token,
            i=str(member.dues17_invoice_no).zfill(4))
    if year == 2018:
        year_invoice_url = request.route_url(
            'make_dues18_invoice_no_pdf',
            email=member.email,
            code=member.dues18_token,
            i=str(member.dues18_invoice_no).zfill(4))
    if year == 2019:
        year_invoice_url = request.route_url(
            'make_dues19_invoice_no_pdf',
            email=member.email,
            code=member.dues19_token,
            i=str(member.dues19_invoice_no).zfill(4))
    if year == 2020:
        year_invoice_url = request.route_url(
            'make_dues20_invoice_no_pdf',
            email=member.email,
            code=member.dues20_token,
            i=str(member.dues20_invoice_no).zfill(4))
    return year_invoice_url


def get_dues_invoice_class(year):
    """
    Get the dues invoice class for creating a database record

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    year_classes = {
        2015: Dues15Invoice,
        2016: Dues16Invoice,
        2017: Dues17Invoice,
        2018: Dues18Invoice,
        2019: Dues19Invoice,
        2020: Dues20Invoice,
    }
    return year_classes[year]


def get_year_invoice_number(year, member):
    """
    Get the year's invoice number

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    year_invoice_number = {
        2015: member.dues15_invoice_no,
        2016: member.dues16_invoice_no,
        2017: member.dues17_invoice_no,
        2018: member.dues18_invoice_no,
        2019: member.dues19_invoice_no,
        2020: member.dues20_invoice_no,
    }
    return year_invoice_number[year]


def invoice_calculated(year, member):
    """
    Check whether the invoice for the year was calculated

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    year_invoice_calculated = {
        2015: member.dues15_invoice,
        2016: member.dues16_invoice,
        2017: member.dues17_invoice,
        2018: member.dues18_invoice,
        2019: member.dues19_invoice,
        2020: member.dues20_invoice,
    }
    return year_invoice_calculated[year]


def record_dues_email_sent(year, member):
    """
    Record the fact that the dues email was sent and when it was sent

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    invoice_date = datetime.now()
    if year == 2015:
        member.dues15_invoice = True
        member.dues15_invoice_date = invoice_date
    if year == 2016:
        member.dues16_invoice = True
        member.dues16_invoice_date = invoice_date
    if year == 2017:
        member.dues17_invoice = True
        member.dues17_invoice_date = invoice_date
    if year == 2018:
        member.dues18_invoice = True
        member.dues18_invoice_date = invoice_date
    if year == 2019:
        member.dues19_invoice = True
        member.dues19_invoice_date = invoice_date
    if year == 2020:
        member.dues20_invoice = True
        member.dues20_invoice_date = invoice_date


def make_year_dues_invoice_email(year):
    """
    Get the make dues invoice email method for the year

    TODO: This is only a workaround until the data model has been cleaned up
    and there is an extra table to record dues per year and member.
    """
    year_make_email = {
        2015: make_dues15_invoice_email,
        2016: make_dues16_invoice_email,
        2017: make_dues17_invoice_email,
        2018: make_dues18_invoice_email,
        2019: make_dues19_invoice_email,
        2020: make_dues20_invoice_email,
    }
    return year_make_email[year]
