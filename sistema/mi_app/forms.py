from django import forms
from .models import Producto, PersonalizacionCampo, PersonalizacionOpcion

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'disponible', 'personalizable', 'campos_personalizacion', 'imagen']
        widgets = {
            'campos_personalizacion': forms.CheckboxSelectMultiple,
        }

class PersonalizacionCampoForm(forms.ModelForm):
    class Meta:
        model = PersonalizacionCampo
        fields = ['nombre', 'es_multiple']

class PersonalizacionOpcionForm(forms.ModelForm):
    class Meta:
        model = PersonalizacionOpcion
        fields = ['nombre', 'precio_extra']

PersonalizacionOpcionFormSet = forms.inlineformset_factory(
    PersonalizacionCampo,
    PersonalizacionOpcion,
    form=PersonalizacionOpcionForm,
    extra=1,
    can_delete=True
)