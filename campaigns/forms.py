from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from campaigns.models import *
from django.forms.extras.widgets import SelectDateWidget

class CreateForm(ModelForm):
	
	start= forms.DateField(initial=datetime.date.today,widget=SelectDateWidget)
	end = forms.DateField(initial=datetime.date.today,widget=SelectDateWidget)
	time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
	choices  = forms.ChoiceField(choices = ([('monthly','monthly'), ('yearly','yearly'), ]))
	class Meta:
		model = FixedEmail
		fields = ['subject','content','option','start','end','time','choices']


        def __init__(self, *args, **kwargs):
                super(CreateForm, self).__init__(*args, **kwargs)
	
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
		label = "Confirm email",
		required = True,
	)

	def __init__(self, *args, **kwargs):
	        campaign = kwargs.pop('campaign',None)
		super(DeadlineForm, self).__init__(*args, **kwargs)
		self.fields['options']= forms.ModelMultipleChoiceField(
			required=False,
			queryset = DeadlineOption.objects.filter(required=False,campaign=campaign),
			widget=OptionsWidget(
                  			fields=('description',),
                  			)
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



class FixedForm(ModelForm):

	confirm_email = forms.EmailField(
                label = "Confirm email",
                required = True,
        )

        def __init__(self, *args, **kwargs):
                campaign = kwargs.pop('campaign',None)
                super(FixedForm, self).__init__(*args, **kwargs)
                self.fields['options']= forms.ModelMultipleChoiceField(
                        queryset = FixedOption.objects.filter(campaign=campaign),
                        widget=OptionsWidget(
                  			fields=('description',),
                  			)
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


class OptionsWidget(forms.widgets.SelectMultiple):

  def __init__(self, *a, **kw):
      self.fields = kw.pop('fields', []) # list of attrs
      self.rns = kw.pop('related_null_string', 'Null')
      super(OptionsWidget, self).__init__(*a, **kw)

  def render(self, name, value, attrs=None, choices=()):
      from itertools import chain
      from django.forms.widgets import CheckboxInput
      from django.utils.encoding import force_unicode
      from django.utils.html import conditional_escape
      from django.utils.safestring import mark_safe

      if value is None: value = []
      has_id = attrs and 'id' in attrs
      final_attrs = self.build_attrs(attrs, name=name)
      output = []
      # Normalize to strings
      str_values = set([force_unicode(v) for v in value])
      for i, (option_value, option_label) in enumerate(chain(self.choices,
                                                             choices)):
          # If an ID attribute was given, add a numeric index as a suffix,
          # so that the checkboxes don't all have the same ID attribute.
          if has_id:
              final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
              label_for = u' for="%s"' % final_attrs['id']
          else:
              label_for = ''

          cb = CheckboxInput(
              final_attrs, check_test=lambda value: value in str_values)
          option_value = force_unicode(option_value)
          rendered_cb = cb.render(name, option_value)
          option_label = conditional_escape(force_unicode(option_label))
          instance = self.choices.queryset.model.objects.get(id=option_value)
          rendered_fields = []
          for f in self.fields:
              try:
                  v = getattr(instance, f)
                  if hasattr(v, 'all'):
                      v = list(getattr(v, 'all')())
                      if v:
                          v = ', '.join([unicode(s) for s in v])
                      else:
                          v = self.rns # set to related_null_string
                  elif isinstance(v, datetime.datetime):
                      v = v.strftime('%b %d, %Y')

                  if isinstance(v, bool):
                      rendered_fields.append(
                          '<td class="%s"><label><span class="%s">%s</span></label></td>' % (
                              f, str(v).lower(), str(v).lower() )
                       )

                  else:
                      rendered_fields.append(
                          '<td class="%s"><label>%s</label></td>' % (f, v))

              except AttributeError:
                  rendered_fields.append(
                      '<td class="%s">None</td>' % f)


          output.append('<tr><td class="checkbox">%s</td>%s</tr>'
                        % (rendered_cb, ''.join(rendered_fields)))

      #output.append(u'</table>')
      return mark_safe(u'\n'.join(output))

  def id_for_label(self, id_):
      # See the comment for RadioSelect.id_for_label()
      if id_:
          id_ += '_0'
      return id_
  id_for_label = classmethod(id_for_label)
