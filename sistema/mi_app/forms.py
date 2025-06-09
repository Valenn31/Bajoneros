from django import forms
from .models import Producto, PersonalizacionCampo, PersonalizacionOpcion, Cliente
from .models import Cliente, DireccionCliente
from datetime import date

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
        fields = '__all__'

class PersonalizacionOpcionForm(forms.ModelForm):
    class Meta:
        model = PersonalizacionOpcion
        fields = ['nombre', 'precio_extra']

from django.forms import inlineformset_factory
PersonalizacionOpcionFormSet = inlineformset_factory(
    PersonalizacionCampo,
    PersonalizacionOpcion,
    form=PersonalizacionOpcionForm,
    extra=1,
    can_delete=True
)

class RegistroClienteForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de nacimiento")

    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'fecha_nacimiento']

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        hoy = date.today()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad < 18:
            raise forms.ValidationError("Debes ser mayor de 18 años para registrarte.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class DireccionForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = ['nombre', 'calle', 'numero', 'piso', 'departamento', 'referencia']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CheckoutForm(forms.Form):
    direccion = forms.ModelChoiceField(
        queryset=None,
        label="Selecciona una dirección",
        required=True,
        empty_label="Selecciona una dirección"
    )

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente')
        super().__init__(*args, **kwargs)
        self.fields['direccion'].queryset = DireccionCliente.objects.filter(usuario=cliente)