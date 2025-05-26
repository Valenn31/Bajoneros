from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'disponible', 'personalizable', 'campos_personalizacion', 'imagen']
        widgets = {
            'campos_personalizacion': forms.CheckboxSelectMultiple,
        }