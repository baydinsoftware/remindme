from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from campaigns.models import FixedEmail, Subscription,EmailQueue,DeadlineCampaign,DeadlineOption,DeadlineAddOn
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from remindme import settings
from django.http import HttpRequest
from django.core.urlresolvers import reverse
from dateutil import tz
from campaigns.sendemail import send


class Command(NoArgsCommand):
	help = "describe command here"

	def handle_noargs(self, **options):
		now = datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
		fromName = "Krista's Reminders"
		fromAddress = 'krista@baydin.com'

		##Send appropriate FixedEmails
		mails = FixedEmail.objects.filter(send_date__lt=now,email_sent=False)	
		for mail in mails:

			option = mail.option
			subscriptions = Subscription.objects.filter(
				object_id=option.id,
				content_type=ContentType.objects.get_for_model(option)
			)
			view_emails_here = "%s%s" % (settings.CAMPAIGN_URL.get(option.campaign.slug), reverse('campaigns:emails', args=(option.campaign.slug,)))
			home_url = settings.CAMPAIGN_URL.get(option.campaign.slug)
			logo_url = "%s/static/images/%s_logo.png" % (home_url,option.campaign.slug)
			for subscription in subscriptions:

				unsubscribe_link = "%s/%s/unsubscribe/%s" % (settings.CAMPAIGN_URL.get(option.campaign.slug), option.campaign.slug, subscription.subscriber.id)
				fromName = option.campaign.name
				send(
				mail.subject,
				mail.content,
				subscription.subscriber.email_address,
				fromName,
				fromAddress,
					{
					"{{name}}":subscription.subscriber.name,
					"{{unsubscribe}}":unsubscribe_link,
					"{{view-emails}}":view_emails_here,
					"{{HOME_URL}}":settings.CAMPAIGN_URL.get(option.campaign.slug),
					"{{CAMPAIGN_NAME}}":option.campaign.name,
					"{{LOGO_URL}}":logo_url,
					}
				)

			mail.email_sent = True
			mail.save()

		
		#Proper Queue Query that only takes emails that should have been sent
		emails_from_queue = EmailQueue.objects.filter(send_date__lte=now,email_sent=False)

		#Imporper Queue Query that sends everything regardless of send date/time for testing
		#emails_from_queue = EmailQueue.objects.filter(email_sent=False)

		for email_on_queue in emails_from_queue:
			try:
				#For Deadline Emails
				campaign = DeadlineOption.objects.get(name=email_on_queue.subscription.subscription.name)
				options = DeadlineOption.objects.filter(campaign=campaign)
				body = email_on_queue.email.content_beginning
				my_subscriptions = Subscription.objects.filter(subscriber=email_on_queue.subscription.subscriber)
				for subscription in my_subscriptions:
					add_ons = DeadlineAddOn.objects.filter(email=email_on_queue.email,option=subscription.subscription)
					for add_on in add_ons:
						body += add_on.content
						body += """
"""
				body += email_on_queue.email.content_end

				deadline_utc = email_on_queue.subscription.subscriber.deadline.strftime("%b %d, %Y")
				slug = email_on_queue.subscription.subscription.campaign.slug
				unsubscribe_link = "%s/%s/unsubscribe/%s" % (settings.CAMPAIGN_URL.get(slug), slug, subscription.subscriber.id)
				view_emails_here = "%s%s" % (settings.CAMPAIGN_URL.get(slug), reverse('campaigns:emails', args=(slug,)))
				home_url = settings.CAMPAIGN_URL.get(slug)
				logo_url = "%s/static/images/%s_logo.png" % (home_url, slug)
				fromName = email_on_queue.subscription.subscription.campaign.name
				send(
				email_on_queue.email.subject,
				body,
				email_on_queue.subscription.subscriber.email_address,
				fromName,
				fromAddress,
					{
					"{{name}}":email_on_queue.subscription.subscriber.name,
					"{{deadline}}":deadline_utc,
					"{{unsubscribe}}":unsubscribe_link,
					"{{view-emails}}":view_emails_here,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":campaign.name,
					"{{LOGO_URL}}":logo_url,
					}
				)
				email_on_queue.email_sent = True
				email_on_queue.save()

			except(ObjectDoesNotExist):
				#For Relative Start Emails

				slug = email_on_queue.subscription.subscription.slug
				unsubscribe_link = "%s/%s/unsubscribe/%s" % (settings.CAMPAIGN_URL.get(slug), slug, email_on_queue.subscription.subscriber.id)
				view_emails_here = "%s%s" % (settings.CAMPAIGN_URL.get(slug), reverse('campaigns:emails', args=(slug,)))
				home_url = settings.CAMPAIGN_URL.get(slug)
				logo_url = "%s/static/images/%s_logo.png" % (home_url, slug)
				fromName = email_on_queue.subscription.subscription.name
				send(
				email_on_queue.email.subject,
				email_on_queue.email.content,
				email_on_queue.subscription.subscriber.email_address,
				fromName,
				fromAddress,
					{
					"{{name}}":email_on_queue.subscription.subscriber.name,
					"{{unsubscribe}}":unsubscribe_link,
					"{{view-emails}}":view_emails_here,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":email_on_queue.subscription.subscription.name,
					"{{LOGO_URL}}":logo_url,
					}
				)

				email_on_queue.email_sent = True
				email_on_queue.save()

