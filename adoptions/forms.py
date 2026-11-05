from django import forms

from .models import AdoptionRequest

INPUT = (
    "w-full rounded-2xl border border-slate-200 px-4 py-3 "
    "focus:outline-none focus:ring-2 focus:ring-orange-400"
)


class AdoptionForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = [
            "housing_type", "ownership", "landlord_allows_pets",
            "household_members", "all_agree",
            "has_other_pets", "other_pets_detail",
            "experience", "hours_alone", "monthly_budget", "reason",
            "agree_terms",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "h-5 w-5 rounded accent-orange-500"
            else:
                field.widget.attrs["class"] = INPUT
        self.fields["experience"].widget.attrs["rows"] = 3
        self.fields["reason"].widget.attrs["rows"] = 3
        # ต้องติ๊กจึงจะส่งได้
        self.fields["all_agree"].required = True
        self.fields["agree_terms"].required = True

    def clean(self):
        data = super().clean()
        if data.get("ownership") == AdoptionRequest.Ownership.RENT and not data.get("landlord_allows_pets"):
            self.add_error(
                "landlord_allows_pets",
                "กรณีเช่า ต้องได้รับอนุญาตจากเจ้าของที่พักให้เลี้ยงสัตว์ก่อน",
            )
        return data