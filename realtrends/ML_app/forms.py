"""
ML_app Forms Module
"""
from __future__ import unicode_literals

from django import forms

from .form_utils import get_currencies, get_listing_types, get_meli_obj
from .views import Meli


# Create your forms here.
class ListingForm(forms.Form):
    title = forms.CharField(
        label='Título', widget=forms.TextInput(attrs={'autofocus': True}))
    category_id = forms.CharField(
        label='Categoría', help_text='MLA9558')
    price = forms.DecimalField(
        label='Precio', min_value=0.01, decimal_places=2, initial=1)
    currency_id = forms.ChoiceField(label='Moneda')
    available_quantity = forms.IntegerField(
        label='Cantidad disponible', required=False, min_value=1, initial=1)
    buying_mode = forms.ChoiceField(label='Modalidad de compra', choices=(
        ('buy_it_now', 'Comprar ahora'), ('auction', 'Subasta')))
    listing_type_id = forms.ChoiceField(label='Tipo de publicación')
    condition = forms.ChoiceField(label='Estado', choices=(
        ('new', 'Nuevo'), ('used', 'Usado'), ('not_specified', 'No especificado')))
    description = forms.CharField(label='Descripción', widget=forms.Textarea(
        attrs={'rows': 2, 'cols': 30}), required=False)
    video_id = forms.CharField(label='Video', required=False)
    warranty = forms.CharField(label='Garantía', required=False)
    seller_custom_field = forms.CharField(
        label='Campo propio del vendedor', required=False)
    accepts_mercadopago = forms.BooleanField(
        label='Aceptar MercadoPago', required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meli = get_meli_obj(request)
        self.fields['currency_id'].choices = get_currencies(meli)
        self.fields['listing_type_id'].choices = get_listing_types(meli)
