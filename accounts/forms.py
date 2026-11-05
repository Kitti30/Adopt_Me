from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

INPUT = (
    "w-full rounded-2xl border border-slate-200 px-4 py-3 "
    "focus:outline-none focus:ring-2 focus:ring-orange-400"
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="อีเมล")
    phone = forms.CharField(label="เบอร์โทร", max_length=20)
    province = forms.CharField(label="จังหวัด", max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
                province=self.cleaned_data["province"],
            )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT