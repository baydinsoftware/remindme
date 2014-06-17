from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from campaigns.models import FixedEmail, Subscription,EmailQueue,DeadlineCampaign,DeadlineOption,DeadlineAddOn
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from boto.ses import SESConnection
from remindme import settings
from django.http import HttpRequest
from django.core.urlresolvers import reverse
from dateutil import tz

class Command(NoArgsCommand):
	help = "describe command here"

	def handle_noargs(self, **options):
		now = datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
		connection = SESConnection(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY)
		fromName = "Krista's Reminders"
		fromAddress = 'krista@baydin.com'
	
		##Send appropriate FixedEmails
		mails = FixedEmail.objects.filter(send_date__lt=now,email_sent=False)	
		for mail in mails:
			subject = mail.subject
			body = mail.content
			
			option = mail.option
			subscriptions = Subscription.objects.filter(
						object_id=option.id,
						content_type=ContentType.objects.get_for_model(option)
						)
			for subscription in subscriptions:

				toAddressesStr = subscription.subscriber.email_address
				subject = subject.replace("{{name}}",subscription.subscriber.name)
                        	body = body.replace("{{name}}",subscription.subscriber.name)
				unsubscribe_link = "<a href='%s%s'>unsubscribe</a>" % (settings.ROOT_URL, reverse('campaigns:unsubscribe', args=(subscription.subscriber.id,)))
		    		body = body.replace("{{unsubscribe}}",unsubscribe_link)
                        	view_emails_here = "<a href='%s%s'>here</a>" % (settings.ROOT_URL, reverse('campaigns:emails', args=(option.campaign.slug,)))
		    		body = body.replace("{{view-emails}}",view_emails_here)
				htmlBody = body
				textBody = strip_tags(htmlBody)
				connection.send_email(fromName + " <" + fromAddress + ">", 
			  		subject, body=htmlBody, to_addresses=toAddressesStr, 
			  		text_body=textBody, format="html", 
			  		return_path=fromAddress)
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
			  	toAddressesStr = email_on_queue.subscription.subscriber.email_address
				subject = email_on_queue.email.subject
				body = email_on_queue.email.content_beginning
				my_subscriptions = Subscription.objects.filter(subscriber=email_on_queue.subscription.subscriber)
				for subscription in my_subscriptions:
					add_ons = DeadlineAddOn.objects.filter(email=email_on_queue.email,option=subscription.subscription)
					for add_on in add_ons:
						body += add_on.content
				body += email_on_queue.email.content_end
				subject = subject.replace("{{name}}",email_on_queue.subscription.subscriber.name)
                                body = body.replace("{{name}}",email_on_queue.subscription.subscriber.name)
				deadline_utc = email_on_queue.subscription.subscriber.deadline
                                subject = subject.replace("{{deadline}}",deadline_utc.strftime("%b %d, %Y"))
				body = body.replace("{{deadline}}",deadline_utc.strftime("%b %d, %Y"))
				unsubscribe_link = "<a href='%s%s'>unsubscribe</a>" % (settings.ROOT_URL, reverse('campaigns:unsubscribe', args=(subscription.subscriber.id,)))
		  		body = body.replace("{{unsubscribe}}",unsubscribe_link)
				view_emails_here = "<a href='%s%s'>here</a>" % (settings.ROOT_URL, reverse('campaigns:emails', args=(option.campaign.slug,)))
                                body = body.replace("{{view-emails}}",view_emails_here)
				htmlBody = body
				textBody = strip_tags(htmlBody)
                                
				connection.send_email(fromName + " <" + fromAddress + ">",
                                        subject, body=htmlBody, to_addresses=toAddressesStr,
                                        text_body=textBody, format="html",
                                        return_path=fromAddress)

				email_on_queue.email_sent = True
                                email_on_queue.save()

			except(ObjectDoesNotExist):
				#For Relative Start Emails
				toAddressesStr = email_on_queue.subscription.subscriber.email_address
				subject = email_on_queue.email.subject
				body = email_on_queue.email.content
				subject = subject.replace("{{name}}",email_on_queue.subscription.subscriber.name)
                                body = body.replace("{{name}}",email_on_queue.subscription.subscriber.name)
                  		unsubscribe_link = "<a href='%s%s'>unsubscribe</a>" % (settings.ROOT_URL, reverse('campaigns:unsubscribe', args=(email_on_queue.subscription.subscriber.id,)))
			        body = body.replace("{{unsubscribe}}",unsubscribe_link)
				view_emails_here = "<a href='%s%s'>here</a>" % (settings.ROOT_URL, reverse('campaigns:emails', args=(email_on_queue.subscription.subscription.slug,)))
                                body = body.replace("{{view-emails}}",view_emails_here)
				htmlBody = body
				textBody = strip_tags(htmlBody)
				
				connection.send_email(fromName + " <" + fromAddress + ">",
                                        subject, body=htmlBody, to_addresses=toAddressesStr,
                                        text_body=textBody, format="html",
                                        return_path=fromAddress)
				
				email_on_queue.email_sent = True
				email_on_queue.save()
		
