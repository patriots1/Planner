from django import forms

from django import forms

class EntryFormBuilder:
    def __init__(self):
        self.fields = {}

    def title(self):
        if 'title' not in self.fields:
            self.fields['title'] = forms.CharField(
                label="Title",
                max_length=32
            )
        return self

    def description(self):
        if 'description' not in self.fields:
            self.fields['description'] = forms.CharField(
                label="Description"
            )
        return self

    def priority(self):
        if 'priority' not in self.fields:
            self.fields['priority'] = forms.IntegerField(
                label="Priority",
                min_value=1,
                max_value=3
            )
        return self

    def due_date(self):
        if 'due_date' not in self.fields:
            self.fields['due_date'] = forms.DateField(
                label="Due Date",
                widget=forms.DateInput(attrs={'type': 'date'}),
            )
        return self

    def include_fields(self, include=None):
        """
        Dynamically include specified fields in the form.
        """
        if include:
            for field_name in include:
                if field_name == 'title':
                    self.title()
                elif field_name == 'description':
                    self.description()
                elif field_name == 'priority':
                    self.priority()
                elif field_name == 'due_date':
                    self.due_date()
        return self

    def build(self):
        """
        Dynamically create and return a Django form class with the specified fields.
        """
        class CustomForm(forms.Form):
            pass

        for field_name, field in self.fields.items():
            CustomForm.base_fields[field_name] = field
        return CustomForm

    

class EditSelectForm(forms.Form):
    options = [
        ("title", "Title"),
        ("description", "Description"),
        ("priority", "Priority"),
        ("due_date", "Due Date")
    ]
    choices = forms.MultipleChoiceField(
        choices=options,
        widget=forms.SelectMultiple,
        label="Select The Fields to Edit",
        required=True,
    )