#!/bin/env/python
# -*- coding: utf-8 -*-

import unittest
from pyramid import testing

from c3smembership.models import (
    DBSession,
    Base,
    C3sMember,
    C3sStaff,
    Group,
)
from sqlalchemy import engine_from_config
import transaction
from datetime import date

DEBUG = False


class EditMemberTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.close()
            DBSession.remove()
            #print "closed and removed DBSession"
        except:
            pass
            #print "no session to close"
       # self.session = DBSession()
        my_settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'available_languages': 'da de en es fr',
            'c3smembership.dashboard_number': '30'}
        engine = engine_from_config(my_settings)
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        #self._insert_members()

        with transaction.manager:
                # a group for accountants/staff
            accountants_group = Group(name=u"staff")
            try:
                DBSession.add(accountants_group)
                DBSession.flush()
                #print("adding group staff")
            except:
                #print("could not add group staff.")
                pass
            # staff personnel
            staffer1 = C3sStaff(
                login=u"rut",
                password=u"berries",
                email=u"noreply@c3s.cc",
            )
            staffer1.groups = [accountants_group]
            try:
                DBSession.add(accountants_group)
                DBSession.add(staffer1)
                DBSession.flush()
            except:
                #print("it borked! (rut)")
                pass

        from c3smembership import main
        app = main({}, **my_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        DBSession.close()
        DBSession.remove()
        testing.tearDown()

    def test_edit_members(self):
        '''
        tests for the edit_member view
        '''
        # unauthorized access must be prevented
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/edit/1', status=403)
        assert('Access was denied to this resource' in res.body)
        res = self.testapp.get('/login', status=200)
        self.failUnless('login' in res.body)
        # try valid user
        form = res.form
        form['login'] = 'rut'
        form['password'] = 'berries'
        res2 = form.submit('submit', status=302)
        # # being logged in ...
        res3 = res2.follow()  # being redirected to dashboard_only
        #print('>'*20)
        #print(res3.body)
        #print('<'*20)
        res4 = res3.follow()  # being redirected to dashboard with parameters
        self.failUnless(
            'Dashboard' in res4.body)
        # # now that we are logged in,
        # # the login view should redirect us to the dashboard
        # res5 = self.testapp.get('/login', status=302)
        # # so yes: that was a redirect
        # res6 = res5.follow()
        # res6 = res6.follow()
        # #print(res4.body)
        # self.failUnless(
        #     'Dashboard' in res6.body)
        # # choose number of applications shown
        # res6a = self.testapp.get(
        #     '/dashboard',
        #     status=302,
        #     extra_environ={
        #         'num_display': '30',
        #     }
        # )
        # res6a = res6a.follow()

        # no member in DB, so redirecting to dashboard
        res = self.testapp.get('/edit/1', status=302)
        res2 = res.follow()

        with transaction.manager:
            member1 = C3sMember(  # german
                firstname=u'SomeFirstnäme',
                lastname=u'SomeLastnäme',
                email=u'some@shri.de',
                address1=u"addr one",
                address2=u"addr two",
                postcode=u"12345",
                city=u"Footown Mäh",
                country=u"Foocountry",
                locale=u"DE",
                date_of_birth=date.today(),
                email_is_confirmed=False,
                email_confirm_code=u'ABCDEFGFOO',
                password=u'arandompassword',
                date_of_submission=date.today(),
                membership_type=u'normal',
                member_of_colsoc=True,
                name_of_colsoc=u"GEMA",
                num_shares=u'23',
            )
        DBSession.add(member1)

        # now there is a member in the DB
        #
        # letzt try invalid input
        res = self.testapp.get('/edit/foo', status=302)
        res2 = res.follow()
        res3 = res2.follow()
        self.failUnless('Dashboard' in res4.body)

        if DEBUG:
            print '+' * 20
            print res2.body
            print '+' * 20
        # now try valid id
        res = self.testapp.get('/edit/1', status=200)
        if DEBUG:
            print(res.body)
        self.failUnless('Mitglied bearbeiten' in res.body)

        # now we change details, really editing that member
        form = res.form

        if DEBUG:
            print "form.fields: {}".format(form.fields)

        self.assertTrue(u'SomeFirstn\xe4me' in form['firstname'].value)

        form['firstname'] = 'EinVorname'
        form['lastname'] = 'EinNachname'
        form['email'] = 'info@c3s.cc'
        form['address1'] = 'adressteil 1'
        form['address2'] = 'adressteil 2'
        form['postcode'] = '12346'
        form['city'] = 'die city'
        form['country'] = 'FI'
        form['membership_type'] = 'investing'
        form['other_colsoc'] = 'no'
        form['name_of_colsoc'] = ''
        form['num_shares'] = 42

        # try to submit now. this must fail,
        # because the date of birth is wrong
        # ... and other dates are missing
        res2 = form.submit('submit', status=200)
        #print res2.body
        self.assertTrue(
            'is earlier than earliest date 2013-09-24' in res2.body)
        # set the date correctly
        form2 = res2.form
        form2['date_of_birth'] = '1999-12-30'
        form2['membership_date'] = '2013-09-24'
        form2['signature_received_date'] = '2013-09-24'
        form2['payment_received_date'] = '2013-09-24'

        self.assertTrue('EinVorname' in res2.body)

        # submit again
        res2 = form2.submit('submit', status=302)
        res3 = res2.follow()
        #print res3.body

        # more asserts
        #self.assertTrue('EinNachname' in res3.body)
        # self.assertTrue('info@c3s.cc' in res3.body)
        # self.assertTrue('adressteil 1' in res3.body)
        # self.assertTrue('adressteil 2' in res3.body)
        # self.assertTrue('12346' in res3.body)
        # self.assertTrue('die city' in res3.body)
        # self.assertTrue('FI' in res3.body)
        # self.assertTrue('investing' in res3.body)
        # self.assertTrue('42' in res3.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)
        #        self.assertTrue('' in res3.body)

        '''
        edit again ... changing membership acceptance status
        '''
        res = self.testapp.get('/edit/1', status=200)
        self.failUnless('Mitglied bearbeiten' in res.body)

        # now we change details, really editing that member
        form = res.form
        if DEBUG:
            print "form.fields: {}".format(form.fields)

        #self.assertTrue(u'SomeFirstn\xe4me' in form['firstname'].value)
        form2['membership_accepted'] = True
        res2 = form2.submit('submit', status=302)
        res3 = res2.follow()

        m1 = C3sMember.get_by_id(1)
        if DEBUG:
            print m1.shares  # yields []
