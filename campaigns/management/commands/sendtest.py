from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from campaigns.models import FixedEmail, Subscription,EmailQueue,DeadlineCampaign,DeadlineOption,DeadlineAddOn
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from boto.ses import SESConnection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Charset
from remindme import settings

class Command(NoArgsCommand):
	help = "describe command here"

	def handle_noargs(self, **options):
		subject = 'hi krista'
		fromName = 'krista'
		fromAddress = 'krista@baydin.com'
		toAddressesStr = 'krissyishere@gmail.com'
		textBody = 'hihihi'
		htmlBody = 'body yo yo yo'
		Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
    		msg = MIMEMultipart('alternative')
    		msg['Subject'] = subject
    		msg['From'] = "" + str(fromName) + " <" + fromAddress + ">"
    		msg['To'] = toAddressesStr
    
    		connection = SESConnection(aws_access_key_id=settings.AWS_ACCESS_KEY, 
				aws_secret_access_key=settings.AWS_SECRET_KEY)
    		connection.send_email(fromName + " <" + fromAddress + ">", 
			subject, body=htmlBody, 
			to_addresses=toAddressesStr, text_body=textBody, 
			format="html", return_path=fromAddress)
