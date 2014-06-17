from django.contrib import admin
from campaigns.models import *
from django import forms
from models import *
from django.db import models
from django.contrib.contenttypes import generic

class CampaignAdmin(admin.ModelAdmin):
	readonly_fields=('slug','name','description','welcome_content')
	exclude=('welcome_subject','unsubscribe_subject','unsubscribe_content')

	
class DeadlineAddonInline(admin.StackedInline):
	model = DeadlineAddOn
	extra = 1

class DeadlineEmailAdmin(admin.ModelAdmin):
	inlines = [DeadlineAddonInline]
	list_filter = ('option',)

class DeadlineOptionInline(admin.StackedInline):
        verbose_name = 'Options (make at least one required!)'
	model = DeadlineOption
        extra = 1
	#readonly_fields=('send_time','subject','content_beginning','content_end',)
	#max_num=0

class DeadlineCampaignAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields' : ('slug','name','description','ontime_margin_in_weeks')
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
        extra = 1
	
class FixedCampaignAdmin(admin.ModelAdmin):
        fieldsets = (
                (None, {
                        'fields' : ('slug','name','description')
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
	readonly_fields = ('email_sent',)	
#	pass

class RelativeStartEmailInline(admin.StackedInline):
	model = RelativeStartEmail
	extra = 1

class RelativeStartCampaignAdmin(admin.ModelAdmin):
	
	inlines = [RelativeStartEmailInline]

	fieldsets = (
                (None, {
                        'fields' : ('slug','name','description')
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

class SubscriptionInline(generic.GenericTabularInline):
	model = Subscription
	readonly_fields=('object_id','content_type')

	
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
	readonly_fields = ('email_sent',)	


admin.site.register(Campaign,CampaignAdmin)
admin.site.register(FixedCampaign,FixedCampaignAdmin)
admin.site.register(DeadlineCampaign,DeadlineCampaignAdmin)
admin.site.register(DeadlineEmail,DeadlineEmailAdmin)
admin.site.register(FixedEmail,FixedEmailAdmin)
admin.site.register(RelativeStartCampaign,RelativeStartCampaignAdmin)
admin.site.register(Subscriber,SubscriberAdmin)
admin.site.register(Subscription)
admin.site.register(EmailQueue,EmailQueueAdmin)
