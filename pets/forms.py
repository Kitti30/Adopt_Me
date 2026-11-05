from django import forms

from .models import Pet

INPUT = (
    "w-full rounded-2xl border border-slate-200 px-4 py-3 "
    "focus:outline-none focus:ring-2 focus:ring-orange-400"
)


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name", "species", "breed", "gender", "age_months",
            "province", "description", "photo", "is_vaccinated", "is_neutered",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "h-5 w-5 rounded accent-orange-500"
            else:
                field.widget.attrs["class"] = INPUT
        self.fields["description"].widget.attrs["rows"] = 4
        self.fields["photo"].widget.attrs["accept"] = "image/*"