from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from tinymce.models import HTMLField
from dateutil import tz

class Email(models.Model):
	subject = models.CharField(max_length=100)
	def __unicode__(self):
                return self.subject

class Campaign(models.Model):
        slug = models.SlugField(unique=True,help_text='Name displayed in URL' )

	name = models.CharField(max_length=200)        
	description = HTMLField(help_text="Text displayed on subscribe page. You can use the following shortcodes: {{overview_url}}. You can directly paste HTML entities such as: &squ;")
	overview = HTMLField(help_text="Text displayed on the overview page. You can directly paste HTML entities such as: &squ;",default="Overview for this campaign is unavailable.")
        
	welcome_subject = models.CharField(max_length=100,help_text='This email is sent immediately when user subscribes')
	welcome_content = HTMLField(help_text="You can use the following shortcodes: {{name}} {{overview_url}} {{unsubscribe}} **{{deadline}} {{first-email}} {{months-away}}*deadline-only. You can directly paste HTML entities such as: &squ;")
        
	unsubscribe_subject = models.CharField(max_length=100,help_text='This email will eventually be sent when user unsubscribes')
        unsubscribe_content = HTMLField(help_text="You can use the following shortcodes: {{name}} You can directly paste HTML entities such as: &squ;")

	def __unicode__(self):
                return self.name

class DeadlineCampaign(Campaign):

	before_welcome_subject = models.CharField(max_length=100,help_text='This email is sent in place of standard welcome if user subscribes some amount of time before first email would be sent as determine by ontime margin above')
        before_welcome_content = HTMLField(help_text="You can use the following shortcodes: {{name}} {{overview_url}} {{deadline}} {{first-email}} {{unsubscribe}} {{months-away}} You can directly paste HTML entities such as: &squ;")

        after_welcome_subject = models.CharField(max_length=100,help_text='This email is sent in place of standard welcome if user subscribes some amount of time after first email would be sent as determine by ontime margin above')
	after_welcome_content = HTMLField(help_text="You can use the following shortcodes: {{name}} {{overview_url}} {{deadline}} {{first-email}} {{unsubscribe}} {{months-away}} You can directly paste HTML entities such as: &squ;")
	deadline_name = models.CharField(max_length=100,help_text='Name for deadline field on subscription page')
	options_question = models.CharField(max_length=100,help_text='Question for options on subscription page',default="Which would you like to recieve reminders about?")
	ontime_margin_in_weeks = models.IntegerField(help_text='Number of weeks before and after first email would be sent that is considered an "on time" start for which user recieves standard welcome email')

class DeadlineOption(models.Model):
	name = models.CharField(max_length=100)
	description = HTMLField(help_text='This is the text that will be displayed on the subscription page. You can directly paste HTML entities such as: &squ;')
	required = models.BooleanField(default=False,help_text='Subscribing to this campaign should automatically subscribe users to this option.')
	campaign = models.ForeignKey(DeadlineCampaign)

	def __unicode__(self):
		return "%s: %s" % (self.campaign.name,self.name)

class DeadlineEmail(Email):
	delta_months = models.IntegerField(help_text='Number of months before deadline this email should be sent. Use negative integers to send after deadline.  Note: Any changes after initial creation will only affect future subscribers. ')        
	delta_days = models.IntegerField(help_text='Number of days before deadline this email should be sent (compounds on top of months). Use negative integers to send after deadline. Note: Any changes after initial creation will only affect future subscribers.')
	
        send_time = models.TimeField()
	content_beginning = HTMLField(help_text='The content of email preceding any "add-ons" from other subscriptions. You can use the following shortcodes: {{name}} {{deadline}} {{overview_url}} {{unsubscribe}} You can directly paste HTML entities such as: &squ;')
	content_end = HTMLField(help_text='The content of email following the "add-ons" from other subscriptions. You can use the following shortcodes: {{name}} {{deadline}} {{overview_url}} {{unsubscribe}} You can directly paste HTML entities such as: &squ; ')
	option = models.ForeignKey(DeadlineOption, help_text='This email is sent only to subscribers of the option selected here. ')

class DeadlineAddOn(models.Model):
	content = HTMLField(help_text='You can use the following shortcodes: {{name}} {{deadline}} {{overview_url}} {{unsubscribe}} You can directly paste HTML entities such as: &squ;')
	email = models.ForeignKey(DeadlineEmail)
	option = models.ForeignKey(DeadlineOption, help_text='This content will appear between content beginning and end from above only if the user is also subscribed to the option selected here.')

#######

class RelativeStartCampaign(Campaign):
	pass

class RelativeStartEmail(Email):
	delta_months = models.IntegerField(help_text='Number of months before deadline this email should be sent.  Note: Any changes after initial creation will only affect future subscribers.')        
	delta_days = models.IntegerField(help_text='Number of days before deadline this email should be sent (compounds on top of months). Note: Any changes after initial creation will only affect future subscribers.')
        send_time = models.TimeField(help_text="Currently CA time- need to change to base of local users time")
	content = HTMLField(help_text="You can use the following shortcodes: {{name}} {{overview_url}} {{unsubscribe}} You can directly paste HTML entities such as: &squ;")
	campaign = models.ForeignKey(RelativeStartCampaign)

#######

class FixedCampaign(Campaign):
	options_question = models.CharField(max_length=100,help_text='Question for options on subscription page',default="Which would you like to recieve reminders about?")

class FixedOption(models.Model):
	name = models.CharField(max_length=100)
	description = HTMLField(help_text='This is the text that will be displayed on the subscription page. You can directly paste HTML entities such as: &squ;')
	campaign = models.ForeignKey(FixedCampaign)

	def __unicode__(self):
		return "%s: %s" % (self.campaign.name,self.name)

class FixedEmail(Email):
	send_date = models.DateTimeField(help_text="This date/time is in UTC. Emails to all subscribers will be sent at this time UTC regardless of your or the subscribers' time zone. UTC is 8hr ahead of CA (7hr during Summer Day Light Savings).")
	content = HTMLField(help_text="You can use the following shortcodes: {{name}} {{unsubscribe}} {{overview_url}}. You can directly paste HTML entities such as: &squ;")
	option = models.ForeignKey(FixedOption, help_text='This email will be sent to users subscribed to this option.')
	email_sent = models.BooleanField(default=False, help_text="This is automatically set to true when this email has been sent to all subscribers.")

#######

class Subscriber(models.Model):
	name = models.CharField(max_length=100)
	email_address = models.EmailField()
	
	date_subscribed = models.DateTimeField(auto_now_add=True)
	
	deadline = models.DateTimeField(null=True,blank=True)
	
	def __unicode__(self):
        	return "%s (%s)" % (self.name, self.email_address)

class Subscription(models.Model):
	subscriber = models.ForeignKey(Subscriber)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	subscription = generic.GenericForeignKey('content_type','object_id')
		
	def __unicode__(self):
		return "%s subscribed to %s" % (self.subscriber.name,self.subscription)

######

class EmailQueue(models.Model):
	send_date = models.DateTimeField()
	subscription = models.ForeignKey(Subscription)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	email = generic.GenericForeignKey('content_type','object_id')
	email_sent = models.BooleanField(default=False,help_text="This is automatically set to true when this email has been sent.")

	def __unicode__(self):
		return "%s (%s) send to %s on %s UTC" % (self.email.subject,
			  self.subscription.subscription,self.subscription.subscriber,
			  self.send_date.strftime("%b %d, %Y %H:%M"))
