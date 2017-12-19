"""
ML_app Tests Module
"""
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse_lazy

from .views import Meli


# Create your tests here.
class LoginTest(TestCase):
    """Login view tests"""
    url = reverse_lazy('login')

    def test_login_page_is_accessible(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name='login.html', count=1)

    def test_login_page_returns_correct_html(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        html = response.content.decode('utf8')
        self.assertInHTML('Iniciar sesión en MercadoLibre', html, 1)
        self.assertIsNotNone(response.context['redirect_uri'])

    def test_login_page_setsup_session_variables(self):
        self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        session = self.client.session
        self.assertIsNotNone(session["CLIENT_ID"])
        self.assertIsNotNone(session["CLIENT_SECRET"])


class AuthorizeTest(TestCase):
    """Authorize view tests"""
    url = reverse_lazy('authorize')

    def setUp(self):
        session = self.client.session
        session['CLIENT_ID'] = 1234
        session['CLIENT_SECRET'] = 'test_secret'
        session.save()
        self.code = 'dfGDFGdfdfgd-1234'
        self.mock_response = Mock(spec=HttpResponse)
        self.mock_response.content = b'{"id":3135}'
        self.mock_access_token = 'test_access_token'

    def test_authorize_page_is_accessible(self):
        with patch('ML_app.views.Meli.authorize') as mock_meli_authorize:
            with patch('ML_app.views.Meli.get', return_value=self.mock_response) as mock_meli_get:
                response = self.client.get(
                    self.url, {'code': self.code}, **{'wsgi.url_scheme': 'https'})
                self.assertTrue(mock_meli_authorize.called)
                self.assertTrue(mock_meli_get.called)
                self.assertEqual(response.status_code, 302)

    def test_authorize_page_is_inccessible_without_code(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertRaises(KeyError)
        self.assertEqual(response.status_code, 302)

    def test_authorize_page_is_inccessible_session_variables(self):
        self.client.session.flush()
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertRaises(KeyError)
        self.assertEqual(response.status_code, 302)

    def test_authorize_page_sets_userid(self):
        with patch('ML_app.views.Meli.authorize'):
            with patch('ML_app.views.Meli.get', return_value=self.mock_response):
                self.client.get(
                    self.url, {'code': self.code}, **{'wsgi.url_scheme': 'https'})
                session = self.client.session
                self.assertIsNotNone(session['ML_USER_ID'])


class HomeTest(TestCase):
    """Home view tests"""
    url = reverse_lazy('home')

    def test_home_page_is_accessible(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name='home.html', count=1)

    def test_home_page_returns_correct_html(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        html = response.content.decode('utf8')
        self.assertInHTML('Publicar en MercadoLibre', html, 1)
        self.assertInHTML('Listar tus publicaciones activas', html, 1)
        self.assertInHTML('Cerrar sesión', html, 1)


class LogoutTest(TestCase):
    """Logout view tests"""
    url = reverse_lazy('logout')

    def setUp(self):
        session = self.client.session
        session['CLIENT_ID'] = 1234
        session['CLIENT_SECRET'] = 'test_secret'
        session['ACCESS_TOKEN'] = 'test_access_token'
        session['REFRESH_TOKEN'] = 'test_refresh_token'
        session.save()

    def test_logout_page_empties_session_data(self):
        self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        session = self.client.session
        self.assertIsNone(session.get('CLIENT_ID'))
        self.assertIsNone(session.get('CLIENT_SECRET'))
        self.assertIsNone(session.get('ACCESS_TOKEN'))
        self.assertIsNone(session.get('REFRESH_TOKEN'))

    def test_logout_page_redirects(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(response.status_code, 302)


class ActiveListingsTest(TestCase):
    """ActiveListings view tests"""
    url = reverse_lazy('active_listings')

    def setUp(self):
        session = self.client.session
        session['CLIENT_ID'] = 1234
        session['CLIENT_SECRET'] = 'test_secret'
        session['ACCESS_TOKEN'] = 'test_access_token'
        session['REFRESH_TOKEN'] = 'test_refresh_token'
        session['ML_USER_ID'] = 'test_ml_user_id'
        session.save()

    def test_active_listings_page_is_accessible(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name='active_listings.html', count=1)

    def test_active_listings_page_returns_correct_html(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        html = response.content.decode('utf8')
        self.assertInHTML('Publicaciones activas', html, 1)


class ListItemTest(TestCase):
    """ListItem view tests"""
    url = reverse_lazy('list_item')

    def setUp(self):
        session = self.client.session
        session['CLIENT_ID'] = 1234
        session['CLIENT_SECRET'] = 'test_secret'
        session['ACCESS_TOKEN'] = 'test_access_token'
        session['REFRESH_TOKEN'] = 'test_refresh_token'
        session.save()
        self.mock_get_currencies = [('ARS', 'Peso Argentino'), ('EUR', 'Euro')]
        self.mock_get_listing_types = [
            ('silver', 'Plata'), ('free', 'Gratuito')]
        self.mock_response_201 = Mock(spec=HttpResponse)
        self.mock_response_201.status_code = 201
        self.mock_response_201.content = b'{"id":3135}'
        self.mock_response_400 = Mock(spec=HttpResponse)
        self.mock_response_400.status_code = 400
        self.mock_response_400.content = '{"error_message":"Category ID non-existent"}'

    def test_list_item_page_is_accessible(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response=response, template_name='list_item.html', count=1)

    def test_list_item_page_returns_correct_html(self):
        response = self.client.get(self.url, **{'wsgi.url_scheme': 'https'})
        html = response.content.decode('utf8')
        self.assertInHTML('Nueva publicación', html)

    def test_list_item_page_creation(self):
        with patch('ML_app.form_utils.get_currencies', return_value=self.mock_get_currencies) as mock_get_currencies:
            with patch('ML_app.form_utils.get_listing_types', return_value=self.mock_get_listing_types) as mock_get_listing_types:
                with patch('ML_app.views.Meli.post', return_value=self.mock_response_201) as mock_meli_post:
                    response = self.client.post(
                        self.url, **{'wsgi.url_scheme': 'https'})
                    self.assertEqual(response.status_code, 200)

    def test_list_item_page_error(self):
        with patch('ML_app.form_utils.get_currencies', return_value=self.mock_get_currencies) as mock_get_currencies:
            with patch('ML_app.form_utils.get_listing_types', return_value=self.mock_get_listing_types) as mock_get_listing_types:
                with patch('ML_app.views.Meli.post', return_value=self.mock_response_400) as mock_meli_post:
                    response = self.client.post(
                        self.url, **{'wsgi.url_scheme': 'https'})
                    self.assertEqual(response.status_code, 200)
