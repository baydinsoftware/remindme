from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from campaigns.models import *
from django.forms.extras.widgets import SelectDateWidget

class RelativeStartForm(ModelForm):
	confirm_email = forms.EmailField(
		label="Confirm email",
		required=True,
	)
	class Meta:
		model = Subscriber
		fields = ['name','email_address','confirm_email']

	def __init__(self, *args, **kwargs):

      		if kwargs.get('instance'):
        		email = kwargs['instance'].email
        		kwargs.setdefault('initial', {})['confirm_email'] = email

        	return super(RelativeStartForm, self).__init__(*args, **kwargs)
	
	def clean(self):
		cleaned_data = super(RelativeStartForm,self).clean()
 		if (cleaned_data.get('email_address') !=
        	    cleaned_data.get('confirm_email')):
        	    raise ValidationError("Email addresses must match.")
		return cleaned_data



class DeadlineForm(ModelForm):

	confirm_email = forms.EmailField(
		label = "Confirm Email",
		required = True,
	)

	def __init__(self, *args, **kwargs):
	        campaign = kwargs.pop('campaign',None)
		super(DeadlineForm, self).__init__(*args, **kwargs)
		self.fields['options']= forms.ModelMultipleChoiceField(
			required=False,
			queryset = DeadlineOption.objects.filter(required=False,campaign=campaign),
			widget=forms.CheckboxSelectMultiple,
			)
		self.fields['deadline'].required = True
		self.fields['deadline'].widget = SelectDateWidget()
	
	class Meta:
		model = Subscriber
		fields = ['name','email_address','confirm_email','deadline']

	def clean(self):
                cleaned_data = super(DeadlineForm,self).clean()
                if (cleaned_data.get('email_address') !=
                    cleaned_data.get('confirm_email')):
                    raise ValidationError("Email addresses must match.")
                return cleaned_data


class MyMultipleModelChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return "%s | &s" % (obj.name, obj.field1)

class FixedForm(ModelForm):

	confirm_email = forms.EmailField(
                label = "Confirm Email",
                required = True,
        )

        def __init__(self, *args, **kwargs):
                campaign = kwargs.pop('campaign',None)
                super(FixedForm, self).__init__(*args, **kwargs)
                self.fields['options']= forms.ModelMultipleChoiceField(
                        queryset = FixedOption.objects.filter(campaign=campaign),
                        widget=forms.CheckboxSelectMultiple,
                        )
        
        class Meta:
                model = Subscriber
                fields = ['name','email_address','confirm_email']


	def clean(self):
                cleaned_data = super(FixedForm,self).clean()
                if (cleaned_data.get('email_address') !=
                    cleaned_data.get('confirm_email')):
                    raise ValidationError("Email addresses must match.")
                return cleaned_data





