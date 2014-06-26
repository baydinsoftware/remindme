from django.contrib import admin
from campaigns.models import *
from django import forms
from models import *
from django.db import models
from django.contrib.contenttypes import generic

class CampaignAdmin(admin.ModelAdmin):
	readonly_fields=('slug','name','description','overview','welcome_content')
	exclude=('welcome_subject','unsubscribe_subject','unsubscribe_content')

	
class DeadlineAddonInline(admin.StackedInline):
	model = DeadlineAddOn
	extra = 1

class DeadlineEmailAdmin(admin.ModelAdmin):
	inlines = [DeadlineAddonInline]
	list_filter = ('option',)
	list_display = ['subject', 'option','delta_months','delta_days','my_url_field']
	def my_url_field(self, obj):
		
		text = """
		<script type="text/javascript">
		<!--
		function send_test_%s(loc) {
			var y=window.prompt("Please enter email for test")
			href = loc.concat("../../../../campaigns/send_test/%s/")
			window.location.href = href.concat(y);
		}
		function send_test_addons_%s(loc) {
			var y=window.prompt("Please enter email for test")
			href = loc.concat("../../../../campaigns/send_test_addons/%s/")
			window.location.href = href.concat(y);
		}
		//-->
		</script>

		

		<a onclick="return send_test_%s(this.href);">Send without add ons</a><br />
		<a onclick="return send_test_addons_%s(this.href);">Send with add ons</a> 	""" % (obj.id, obj.id,obj.id,obj.id,obj.id,obj.id)
		return text
		#return '<a href="%s%s">%s</a>' % ('http://url-to-prepend.com/', obj.subject, obj.subject)
	my_url_field.allow_tags = True
	my_url_field.short_description = 'Send Test Email'

class DeadlineOptionInline(admin.StackedInline):
        verbose_name = 'Options (make at least one required!)'
	model = DeadlineOption
        extra = 2
	#readonly_fields=('send_time','subject','content_beginning','content_end',)
	#max_num=0

class DeadlineCampaignAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields' : ('slug','name','deadline_name','options_question','description','overview','ontime_margin_in_weeks')
		}),
		('Welcome Email (recieved when user subscribes)',{
			'fields': ('welcome_subject','welcome_content'),
			#'classes':('collapse',),
		}),
		('Unsubscribe Email (recieved when user unsubscribes)',{
                        'fields': ('unsubscribe_subject','unsubscribe_content'),
		#	'classes':('collapse',),
		}),
		("Before Welcome Email (recieved when user subscribes before first email)",{
			'fields':('before_welcome_subject','before_welcome_content'),
		#	'classes':('collapse',),
		}),
		 ('After Welcome Email (recieved when user subscribes after first email)',{
                        'fields':('after_welcome_subject','after_welcome_content'),
                  #      'classes':('collapse',),
                }),
	)
	inlines = [DeadlineOptionInline]

class FixedOptionInline(admin.StackedInline):
        verbose_name = 'Options'
        model = FixedOption
        extra = 2
	
class FixedCampaignAdmin(admin.ModelAdmin):
        fieldsets = (
                (None, {
                        'fields' : ('slug','name','options_question','description','overview')
                }),
                ('Welcome Email (recieved when user subscribes)',{
                        'fields': ('welcome_subject','welcome_content'),
                 #       'classes':('collapse',),
                }),
		('Unsubscribe Email (recieved when user unsubscribes)',{
                        'fields': ('unsubscribe_subject','unsubscribe_content'),
                #        'classes':('collapse',),
                }),
	)
	inlines = [FixedOptionInline]

class FixedEmailAdmin(admin.ModelAdmin):
	def render_change_form(self, request, context, *args, **kwargs):
        	# here we define a custom template
        	self.change_form_template = "campaigns/admin/change_form_help_text.html"
        	extra = {
   	    	    'help_text': "ADD MULTIPLE RECURSIVE EMAILS HERE: http://www.mytaxreminders.com/admin/recursive_fixed"
        	}

        	context.update(extra)
        	return super(FixedEmailAdmin, self).render_change_form(request,
            	context, *args, **kwargs)

	#readonly_fields = ('email_sent',)	
	list_filter = ('option',)
	list_display = ['subject', 'option','send_date','my_url_field']
	def my_url_field(self, obj):
		
		text = """
		<script type="text/javascript">
		<!--
		function send_test_%s(loc) {
			var y=window.prompt("Please enter email for test")
			href = loc.concat("../../../../campaigns/send_test/%s/")
			window.location.href = href.concat(y);
		#}
		//-->
		</script>
		<a onclick="return send_test_%s(this.href);">Click</a> 	""" % (obj.id,obj.id,obj.id)
		return text
		#return '<a href="%s%s">%s</a>' % ('http://url-to-prepend.com/', obj.subject, obj.subject)
	my_url_field.allow_tags = True
	my_url_field.short_description = 'Send Test Email'

class RelativeStartEmailInline(admin.StackedInline):
	model = RelativeStartEmail
	extra = 1

class RelativeStartCampaignAdmin(admin.ModelAdmin):
	
	inlines = [RelativeStartEmailInline]

	fieldsets = (
                (None, {
                        'fields' : ('slug','name','description','overview')
                }),
                ('Welcome Email (recieved when user subscribes)',{
                        'fields': ('welcome_subject','welcome_content'),
                       # 'classes':('collapse',),
                }),
                ('Unsubscribe Email (recieved when user unsubscribes)',{
                        'fields': ('unsubscribe_subject','unsubscribe_content'),
                        #'classes':('collapse',),
                }),
        )

class SubscriptionInline(admin.StackedInline):
	model = Subscription
	readonly_fields=('subscription',)
	fields=('subscription',)
	extra = 0
	def has_add_permission(self, request):
		return False

class SubscriberAdmin(admin.ModelAdmin):
	fieldsets = (
                (None, {
                        'fields' : ('name','email_address','date_subscribed',)
                }),
                ('Deadline (if applicable)',{
                        'fields': ('deadline',),
                        'classes':('collapse',),
                }),
        )
	inlines = [SubscriptionInline]
	readonly_fields=('date_subscribed',)

	
class EmailQueueAdmin(admin.ModelAdmin):
	list_filter = ('email_sent',)
	readonly_fields = ('subscription','email_sent','email')	
	fields=('send_date','subscription','email','email_sent')

#admin.site.register(Campaign,CampaignAdmin)
admin.site.register(FixedCampaign,FixedCampaignAdmin)
admin.site.register(DeadlineCampaign,DeadlineCampaignAdmin)
admin.site.register(DeadlineEmail,DeadlineEmailAdmin)
admin.site.register(FixedEmail,FixedEmailAdmin)
admin.site.register(RelativeStartCampaign,RelativeStartCampaignAdmin)
admin.site.register(Subscriber,SubscriberAdmin)
admin.site.register(EmailQueue,EmailQueueAdmin)
