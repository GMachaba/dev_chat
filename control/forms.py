from django import forms
from django.db.models import Q
from django.forms.forms import Form
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
from control.models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
import pendulum


class LogInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        self.cleaned_data = super(LogInForm, self).clean()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user_obj = authenticate(username=username, password=password)
        if user_obj is None:
            raise forms.ValidationError('Wrong credentials please try again!')

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']

    def __init__(self, form_update=False, *args, **kwargs):
        super(RegionForm, self).__init__(*args, **kwargs)
        self.form_update = form_update

    def clean(self):
        if not self.form_update:
            form_data = self.cleaned_data
            name = form_data.get("name", None)
            if Region.objects.filter(name=name).exists():
                self.add_error('name',"This region exists")

    def save(self, *args, **kwargs):
        region = super(RegionForm, self).save(*args, **kwargs)
        region.name = self.cleaned_data['name'].upper()
        region.save()
        return region


data = list()
for s in Region.objects.filter(is_active=True,is_deleted=False).order_by("name"):
    data.append((s.id,s.name))

class UserProfileForm(forms.ModelForm):
    """Form definition for UserProfile."""
    full_name = forms.CharField(required=True)
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(is_active=True,is_deleted=False),widget=forms.CheckboxSelectMultiple, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)
    user_choice = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    location_data = forms.ChoiceField(choices=tuple(data),widget=forms.RadioSelect)

    class Meta:
        """Meta definition for UserProfileform."""

        model = UserProfile
        fields = [
            'full_name',
            'email',
            'phone_number',
            'user_choice',
            'location_data',
            'tag',
            'password'
        ]

        def __init__(self,form_update=False, *args, **kwargs):
            super(UserProfileForm,self).__init__(*args, **kwargs)
            self.form_update = form_update
            self.fields["phone_number"].required = True
            


            # print(data)
            # self.fields["location_data"].choices = tuple(data)

            # self.fields["user_type"].widget = forms.RadioSelect()
            # self.fields["tag"].queryset = Tag.objects.filter(is_active=True,is_deleted=False)

        def clean(self):
            if not self.form_update:
                form_data = self.cleaned_data
                email = form_data.get("email", None)
                phone_number = form_data.get("phone_number", None)
                if User.objects.filter(email=email).exists():
                    self.add_error('email',"This Email exists")
                if UserProfile.objects.filter(phone_number=phone_number).exists():
                    self.add_error("phone_number", "This Phone number exists")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name','description']

    def __init__(self, form_update=False, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.form_update = form_update

    def clean(self):
        if not self.form_update:
            form_data = self.cleaned_data
            name = form_data.get("name", None)
            if Tag.objects.filter(name=name).exists():
                self.add_error('name',"This Tag exists")

    def save(self, *args, **kwargs):
        tag = super(TagForm, self).save(*args, **kwargs)
        tag.name = self.cleaned_data['name'].upper()
        tag.description = self.cleaned_data["description"]
        tag.save()
        return tag


class StudentPostForm(forms.ModelForm):
    """Form definition for StudentPost."""
    tag_name = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(is_active=True,is_deleted=False),widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        """Meta definition for StudentPostform."""

        model = StudentPost
        fields = [
            'title',
            'description',
            'tag_name'
        ]


class PostCommentForm(forms.ModelForm):
    """Form definition for PostComment."""

    class Meta:
        """Meta definition for PostCommentform."""

        model = PostComment
        fields = ['description']
