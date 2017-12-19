"""
ML_app Views Module
"""
from __future__ import unicode_literals

import json
import sys

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.debug import sensitive_variables
from django.views.generic import FormView, RedirectView, TemplateView
from django.views.generic.list import ListView
from meli import Meli

from .forms import ListingForm


# Create your views here.
class LoginView(TemplateView):
    """
    Displays a link to the mercadolibre site
    """
    template_name = 'login.html'

    @sensitive_variables('client_id', 'client_secret')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = settings.CLIENT_ID
        client_secret = settings.CLIENT_SECRET
        meli = Meli(client_id, client_secret)

        context['redirect_uri'] = meli.auth_url(
            redirect_URI=settings.CALLBACK_URL)

        self.request.session['CLIENT_ID'] = client_id
        self.request.session['CLIENT_SECRET'] = client_secret
        return context


class AuthorizeView(RedirectView):
    """
    Retrieves the access and refresh tokens and redirects to home
    """
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        try:
            code = request.GET['code']
            meli = Meli(
                self.request.session['CLIENT_ID'], self.request.session['CLIENT_SECRET'])
        except KeyError:
            return redirect('login')

        meli.authorize(
            code=code, redirect_URI=settings.CALLBACK_URL)
        response = meli.get(
            '/users/me', params={'access_token': meli.access_token})
        json_response = json.loads(response.content)
        self.request.session['ML_USER_ID'] = json_response['id']

        self.request.session['ACCESS_TOKEN'] = meli.access_token
        self.request.session['REFRESH_TOKEN'] = meli.refresh_token
        return super().get(request, *args, **kwargs)


class HomeView(TemplateView):
    """
    Displays the app functionality in a template
    """
    template_name = 'home.html'


class ListItemView(FormView):
    """
    Displays a form to create a new listing
    """
    form_class = ListingForm
    template_name = 'list_item.html'
    success_url = reverse_lazy('home')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs(), request=self.request)

    def form_valid(self, form):
        try:
            meli = Meli(client_id=self.request.session['CLIENT_ID'],
                        client_secret=self.request.session['CLIENT_SECRET'],
                        access_token=self.request.session['ACCESS_TOKEN'],
                        refresh_token=self.request.session['REFRESH_TOKEN'])
        except KeyError:
            return redirect('login')

        body = {
            "condition": form.cleaned_data['condition'],
            "warranty": form.cleaned_data['warranty'],
            "currency_id": form.cleaned_data['currency_id'],
            "accepts_mercadopago": form.cleaned_data['accepts_mercadopago'],
            "description": form.cleaned_data['description'],
            "listing_type_id": form.cleaned_data['listing_type_id'],
            "title": form.cleaned_data['title'],
            "available_quantity": form.cleaned_data['available_quantity'],
            "price": str(form.cleaned_data['price']),
            "buying_mode": form.cleaned_data['buying_mode'],
            "category_id": form.cleaned_data['category_id']}

        response = meli.post(
            "/items", body, {'access_token': meli.access_token})
        if response.status_code != 201:
            form.add_error(field=None, error=response.content)
            return super().form_invalid(form)
        return super().form_valid(form)


class ActiveListingsView(TemplateView):
    """
    Displays the active listings of the authenticated user
    """
    template_name = 'active_listings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publicaciones'] = self.get_publicaciones()
        return context

    def get_publicaciones(self):
        try:
            meli = Meli(client_id=self.request.session['CLIENT_ID'],
                        client_secret=self.request.session['CLIENT_SECRET'],
                        access_token=self.request.session['ACCESS_TOKEN'],
                        refresh_token=self.request.session['REFRESH_TOKEN'])
            ml_user_id = self.request.session['ML_USER_ID']
        except KeyError:
            return redirect('login')
        publicaciones_activas = list()

        response = meli.get(
            f'/users/{ml_user_id}/items/search', params={'access_token': meli.access_token})
        json_response = json.loads(response.content)
        publicaciones = json_response.get('results')
        if publicaciones:
            for publicacion in publicaciones:
                resp = meli.get(f'/items/{publicacion}',
                                params={'access_token': meli.access_token})
                json_publicacion = json.loads(resp.content)
                if json_publicacion['status'] == 'active':
                    publicaciones_activas.append({
                        'id': str(publicacion),
                        'permalink': json_publicacion['permalink'],
                        'price': json_publicacion['price'],
                        'title': json_publicacion['title']})
        return publicaciones_activas


class LogoutView(RedirectView):
    """
    Flushes the session and redirects to the login page
    """
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        self.request.session.flush()
        return super().get(request, *args, **kwargs)
