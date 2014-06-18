from django.shortcuts import render, get_object_or_404
from models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from campaigns.forms import *
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.db.models import Max
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from remindme import settings
from boto.ses import SESConnection
from django.core.urlresolvers import reverse
from datetime import datetime
from dateutil import tz
from dateutil import rrule
from itertools import chain
from django.contrib.staticfiles.storage import staticfiles_storage

fromAddress = 'krista@baydin.com'
fromName = "MyReminders"

HEADER = """
<!-- Inliner Build Version 4380b7741bb759d6cb997545f3add21ad48f010b -->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width" />
  </head>
  <body style="width: 100% !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; color: #222222; display: block; font-family: 'Helvetica', 'Arial', sans-serif; text-align: left; line-height: 19px; font-size: 14px; margin: 0; padding: 0;"><style type="text/css">
a:hover {
color: #1b75bb !important;
}
a:active {
color: #2795b6 !important;
}
a:visited {
color: ##64A629 !important;
}
h1 a:active {
color: #64A629 !important;
}
h2 a:active {
color: #64A629 !important;
}
h3 a:active {
color: #64A629 !important;
}
h4 a:active {
color: #64A629 !important;
}
h5 a:active {
color: #64A629 !important;
}
h6 a:active {
color: #64A629 !important;
}
h1 a:visited {
color: #64A629 !important;
}
h2 a:visited {
color: #64A629 !important;
}
h3 a:visited {
color: #64A629 !important;
}
h4 a:visited {
color: #64A629 !important;
}
h5 a:visited {
color: #64A629 !important;
}
h6 a:visited {
color: #64A629 !important;
}
table.button:hover td {
background: #2795b6 !important;
}
table.button:visited td {
background: #2795b6 !important;
}
table.button:active td {
background: #2795b6 !important;
}
table.button:hover td a {
color: #fff !important;
}
table.button:visited td a {
color: #fff !important;
}
table.button:active td a {
color: #fff !important;
}
table.button:hover td {
background: #2795b6 !important;
}
table.tiny-button:hover td {
background: #2795b6 !important;
}
table.small-button:hover td {
background: #2795b6 !important;
}
table.medium-button:hover td {
background: #2795b6 !important;
}
table.large-button:hover td {
background: #2795b6 !important;
}
table.button:hover td a {
color: #ffffff !important;
}
table.button:active td a {
color: #ffffff !important;
}
table.button td a:visited {
color: #ffffff !important;
}
table.tiny-button:hover td a {
color: #ffffff !important;
}
table.tiny-button:active td a {
color: #ffffff !important;
}
table.tiny-button td a:visited {
color: #ffffff !important;
}
table.small-button:hover td a {
color: #ffffff !important;
}
table.small-button:active td a {
color: #ffffff !important;
}
table.small-button td a:visited {
color: #ffffff !important;
}
table.medium-button:hover td a {
color: #ffffff !important;
}
table.medium-button:active td a {
color: #ffffff !important;
}
table.medium-button td a:visited {
color: #ffffff !important;
}
table.large-button:hover td a {
color: #ffffff !important;
}
table.large-button:active td a {
color: #ffffff !important;
}
table.large-button td a:visited {
color: #ffffff !important;
}
table.secondary:hover td {
background: #d0d0d0 !important; color: #555;
}
table.secondary:hover td a {
color: #555 !important;
}
table.secondary td a:visited {
color: #555 !important;
}
table.secondary:active td a {
color: #555 !important;
}
table.success:hover td {
background: #457a1a !important;
}
table.alert:hover td {
background: #970b0e !important;
}
.button:hover table td {
background: #56981D !important;
}
.tiny-button:hover table td {
background: #56981D !important;
}
.small-button:hover table td {
background: #56981D !important;
}
.medium-button:hover table td {
background: #56981D !important;
}
.large-button:hover table td {
background: #56981D !important;
}
.button:hover {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.button:active {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.button:visited {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.tiny-button:hover {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.tiny-button:active {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.tiny-button:visited {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.small-button:hover {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.small-button:active {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.small-button:visited {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.medium-button:hover {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.medium-button:active {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.medium-button:visited {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.large-button:hover {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.large-button:active {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.large-button:visited {
color: #ffffff !important; font-family: Helvetica, Arial, sans-serif; text-decoration: none;
}
.secondary:hover table td {
background: #d0d0d0 !important;
}
.success:hover table td {
background: #457a1a !important;
}
.alert:hover table td {
background: #970b0e !important;
}
table.facebook:hover td {
background: #2d4473 !important;
}
table.twitter:hover td {
background: #0087bb !important;
}
table.google-plus:hover td {
background: #CC0000 !important;
}
@media only screen and (max-width: 600px) {
  table[class="body"] img {
    width: auto !important; height: auto !important;
  }
  table[class="body"] .container {
    width: 95% !important;
  }
  table[class="body"] .row {
    width: 100% !important; display: block !important;
  }
  table[class="body"] .wrapper {
    display: block !important; padding-right: 0 !important;
  }
  table[class="body"] .columns {
    table-layout: fixed !important; float: none !important; width: 100% !important; padding-right: 0px !important; padding-left: 0px !important; display: block !important;
  }
  table[class="body"] .column {
    table-layout: fixed !important; float: none !important; width: 100% !important; padding-right: 0px !important; padding-left: 0px !important; display: block !important;
  }
  table[class="body"] .wrapper.first .columns {
    display: table !important;
  }
  table[class="body"] .wrapper.first .column {
    display: table !important;
  }
  table[class="body"] table.columns td {
    width: 100%;
  }
  table[class="body"] table.column td {
    width: 100%;
  }
  table[class="body"] td.offset-by-one {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-two {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-three {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-four {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-five {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-six {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-seven {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-eight {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-nine {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-ten {
    padding-left: 0 !important;
  }
  table[class="body"] td.offset-by-eleven {
    padding-left: 0 !important;
  }
  table[class="body"] .expander {
    width: 9999px !important;
  }
  table[class="body"] center {
    min-width: 0 !important;
  }
  table[class="body"] .hide-for-small {
    display: none !important;
  }
  table[class="body"] .show-for-desktop {
    display: none !important;
  }
  table[class="body"] .show-for-small {
    display: inherit !important;
  }
  table[class="body"] .hide-for-desktop {
    display: inherit !important;
  }
  table[class="body"] .right-text-pad {
    padding-left: 10px !important;
  }
  table[class="body"] .left-text-pad {
    padding-right: 10px !important;
  }
}
</style>
	<table class="body" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; height: 100%; width: 100%; padding: 0;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td class="center" align="center" valign="top" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: center; padding: 0;">
        <center style="width: 100%; min-width: 580px;">
         
             
          <table class="container" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: inherit; width: 580px; margin: 0 auto; padding: 0;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; padding: 0;" align="left" valign="top">
                
                <!-- content start -->
                <table class="row" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; padding: 0px;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td class="wrapper last" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; padding: 10px 0px 0px 10px;" align="left" valign="top">
                
                      <table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; padding: 0px 0px 10px;" align="left" valign="top">
                          		<br /><a href="{{HOME_URL}}" style="color: #33b5e5; text-decoration: none;"><img width="600" src="{{LOGO_URL}}" style="outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; width: auto; max-width: 100%; float: left; clear: both; display: block; border: none;" align="left" /></a></td>
                          <td class="expander" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; visibility: hidden; width: 0px; padding: 0;" align="left" valign="top"></td>
                        </tr></table></td>
                  </tr></table><table class="row" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; padding: 0px;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td class="wrapper last" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; padding: 10px 0px 0px 10px;" align="left" valign="top">

                      <table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; padding: 0px 0px 10px;" align="left" valign="top">

"""

END = """
</td>
                  </tr></table><table class="row footer" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 100%; position: relative; display: block; padding: 0px;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td class="wrapper" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; position: relative; background: #ebebeb; padding: 10px 10px 0px;" align="left" bgcolor="#ebebeb" valign="top">
                            
                      <table class="twelve columns" style="border-spacing: 0; border-collapse: collapse; vertical-align: top; text-align: left; width: 580px; margin: 0 auto; padding: 0;"><tr style="vertical-align: top; text-align: left; padding: 0;" align="left"><td class="eight sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 66.666666% !important; padding: 0px 3.448276% 10px 0px;" align="left" valign="top"> 
                          <small style="font-size: 10px;"> <a href="{{unsubscribe}}" style="color: #33b5e5; text-decoration: none;">Unsubscribe from these emails</a> 
                              <br />
                              You are receiving this offer because you signed up for My Tax Reminders, from the makers of <a href="http://http://www.boomeranggmail.com//" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang for Gmail</a>, <a href="http://www.boomerangcalendar.com/" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang Calendar</a>, <a href="http://www.baydin.com/boomerang/" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang for Outlook</a>, and <a href="http://www.inboxpause.com/" target="_blank" style="color: #33b5e5; text-decoration: none;">Inbox Pause</a>. 
                          </small></td>
                          <td class="three sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; width: 25% !important; padding: 0px 3.448276% 10px 0px;" align="left" valign="top">
                          	<small style="font-size: 10px;">
                            <strong>Our mailing address is:</strong>
                            <br />
                            Baydin Inc.
                            <br />
                            196A Castro St
                            <br />
                            Mountain View, CA 94041
                            </small>
                          </td>          
                          <td class="expander" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; visibility: hidden; width: 0px; padding: 0;" align="left" valign="top"></td>
                        </tr></table></td>
                  </tr></table><!-- container end below --></td>
            </tr></table></center>
			</td>
		</tr></table></body>
</html>
"""


def index(request):
  
	campaign_list = Campaign.objects.all()
	context = {'campaign_list':campaign_list}
	return render(request, 'campaigns/index.html',context)

	
	
def campaign(request,campaign_slug):
	campaign = get_object_or_404(Campaign,slug=campaign_slug)
	
	connection = SESConnection(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY)
	
	##Determine which type of Campaign
	DEADLINE = 'deadline'
	FIXED = 'fixed'
	RELATIVE = 'relative'
	try:
	  campaign = DeadlineCampaign.objects.get(slug=campaign_slug)
	  options = DeadlineOption.objects.filter(campaign=campaign)
	  type = DEADLINE
	except(ObjectDoesNotExist):
	  try:
	    campaign = FixedCampaign.objects.get(slug=campaign_slug)
	    options = FixedOption.objects.filter(campaign=campaign)
	    type = FIXED
	  except(ObjectDoesNotExist):
	    campaign = RelativeStartCampaign.objects.get(slug=campaign_slug)
	    type = RELATIVE

	    
	if type == RELATIVE:
	    if request.method == 'GET':
		form = RelativeStartForm()
	    else:
		# A POST request: Handle Form Upload
		form = RelativeStartForm(request.POST) # Bind data from request.POST into a PostForm
		# If data is valid, proceeds to create a new post and redirect the user
		if form.is_valid():
		  
		    ###Save Data
		    name = form.cleaned_data['name']
		    email_address = form.cleaned_data['email_address']
		    subscriber = Subscriber.objects.create(name=name,
						email_address=email_address)
		    subscription = Subscription.objects.create(subscriber=subscriber,
						subscription=campaign)

		    ###Replace Shortcodes
		    subject = campaign.welcome_subject
		    body = campaign.welcome_content
		    subject = subject.replace("{{name}}",name)
		    body = body.replace("{{name}}",name)
		    unsubscribe_link = request.build_absolute_uri(reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,)))
		    body = body.replace("{{unsubscribe}}",unsubscribe_link)
		    view_emails_here = request.build_absolute_uri(reverse('campaigns:emails', args=(campaign.slug,)))
		    body = body.replace("{{view-emails}}",view_emails_here)
		   
		    ###Send Welcome Email
		    myHeader = HEADER.replace("{{HOME_URL}}",request.build_absolute_uri(reverse('campaigns:campaign', args=(campaign.slug,))))
		    myHeader = myHeader.replace("{{LOGO_URL}}",request.build_absolute_uri(staticfiles_storage.url("images/%s_logo.png" % campaign.slug)))
		    htmlBody = "%s%s%s" % (myHeader.replace("{{unsubscribe}}",unsubscribe_link),body,END.replace("{{unsubscribe}}",unsubscribe_link))
		    textBody = strip_tags(body)
		    toAddressesStr = subscriber.email_address
		    
		    connection.send_email(fromName + " <" + fromAddress + ">", 
			  subject, body=htmlBody, to_addresses=toAddressesStr, 
			  text_body=textBody, format="html", 
			  return_path=fromAddress)
		    
		    ###Put Emails in Queue
		    
		    timezone = request.POST['timezone']
		    
		    utc_zone = tz.gettz('UTC')
		    local_zone = tz.gettz(timezone)
		    
		    #date subscribed in database is saved as UTC
		    date_subscribed_utc = subscriber.date_subscribed.replace(tzinfo=utc_zone)
		    #convert date_subscribed to local to perform calculations of emails
		    date_subscribed_local = date_subscribed_utc.astimezone(local_zone)

		    emails = RelativeStartEmail.objects.filter(campaign=campaign)
		    for email in emails:
			  #date = datetime(2002, 10, 10, 6, 0, 0)
			  send_date_local = date_subscribed_local
			  #add number of months from subscription this email should be sent
			  if email.delta_months > 0:
				for dt in rrule.rrule(rrule.MONTHLY, dtstart=send_date_local, bymonthday=(send_date_local.day, -1), bysetpos=1, count=email.delta_months+1):
				      send_date_local = dt
			  #add number of days from subscription this email should be sent
			  if email.delta_days > 0:
				for dt in rrule.rrule(rrule.DAILY, dtstart=send_date_local, count=email.delta_days+1):
				      send_date_local = dt
				      
			  #get strict value of time email should be sent
			  send_time = email.send_time.replace(tzinfo=None)
			  #add this strict value of time to local send time
			  send_date_local = send_date_local.replace(hour=send_time.hour,minute=send_time.minute,second=send_time.second)
			  
			  #convert calucalted send date back to UTC
			  send_date_utc = send_date_local.astimezone(utc_zone)

			  #add email to queue with UTC time
			  queue = EmailQueue.objects.create(send_date=send_date_utc,subscription=subscription,email=email)
		    
		    ###Display Thank you screen
		    return render(request, 'campaigns/thanks.html', {
			  'subscriber': subscriber,'campaign':campaign
			  })	    
	
	    return render(request, 'campaigns/subscribe.html', {
		'form': form,'campaign':campaign
		  })
	elif type == DEADLINE:
	    if request.method == 'GET':
		form = DeadlineForm(campaign=campaign)
	    else:
		# A POST request: Handle Form Upload
		form = DeadlineForm(request.POST,campaign=campaign) # Bind data from request.POST into a PostForm
	
		# If data is valid, proceeds to create a new post and redirect the user
		if form.is_valid():
		  
		    ###Save Data
		    name = form.cleaned_data['name']
		    email_address = form.cleaned_data['email_address']
		    deadline = form.cleaned_data['deadline']
		    options = form.cleaned_data['options']
		    timezone = request.POST['timezone']
		    
		    utc_zone = tz.gettz('UTC')
		    local_zone = tz.gettz(timezone)
		    
		    #deadline given is in local
		    deadline_local = deadline.replace(tzinfo=local_zone)
		    #convert deadline to UTC to store
		    deadline_utc= deadline_local.astimezone(utc_zone)

		    subscriber = Subscriber.objects.create(name=name,
						email_address=email_address,deadline=deadline_utc)
		    required_options = DeadlineOption.objects.filter(campaign=campaign,required=True)		    
		    all_options = list(chain(required_options, options))
		    
		    first_email = deadline_local #we're going to store the earliest email this subscriber would get to calculate appropriate welcome
		    for option in all_options:
			subscription = Subscription.objects.create(subscriber=subscriber,
					subscription=option)
			
			#Add Emails for each option to EmailQueue
			emails = DeadlineEmail.objects.filter(option=option)
			for email in emails:
				#date = datetime(2002, 10, 10, 6, 0, 0)
				send_date_local = deadline_local + timedelta(days=-email.delta_days) + relativedelta(months=-email.delta_months)
				
				#get strict value of time email should be sent
				send_time = email.send_time.replace(tzinfo=None)
				
				#add this strict value of time to local send time
				send_date_local = send_date_local.replace(hour=send_time.hour,minute=send_time.minute,second=send_time.second)
				print "send_date_local %s" % send_date_local
				
				#convert calucalted send date back to UTC
				send_date_utc = send_date_local.astimezone(utc_zone)
				print "send_date_utc %s" % send_date_utc

				now_utc = datetime.utcnow().replace(tzinfo=utc_zone)
				
				#if this intended send time is earlier than current earliest, save
				if first_email > send_date_utc:
					first_email = send_date_utc
				#only add to queue if its send date has yet to happen
				if send_date_utc > now_utc:
					queue = EmailQueue.objects.create(send_date=send_date_utc,subscription=subscription,email=email)
						
		    ###Calculate ranges for each Welcome Email
		    print "first_email %s" % first_email 
		    now_utc = datetime.utcnow().replace(tzinfo=utc_zone)
		    print "now_utc %s" % now_utc 
		    before_date = now_utc + relativedelta(weeks=-campaign.ontime_margin_in_weeks)
		    print "before_date %s" % before_date 
		    after_date = now_utc + relativedelta(weeks=campaign.ontime_margin_in_weeks)
		    print "after_date %s" % after_date
		    
		    months_away = 0
		    for r in rrule.rrule(rrule.MONTHLY, bymonthday=(deadline_utc.day, -1), bysetpos=1, dtstart=now_utc, until=deadline_utc):
			months_away += 1
			
		    ###Send Appropriate Welcome Email
		    if after_date > first_email and before_date < first_email:
			subject = campaign.welcome_subject
			body = campaign.welcome_content
		    elif after_date > first_email:
			subject = campaign.after_welcome_subject
			body = campaign.after_welcome_content
		    else:
			subject = campaign.before_welcome_subject
			body = campaign.before_welcome_content
			
		    toAddressesStr = subscriber.email_address
		    
		    subject = subject.replace("{{name}}",name)
		    body = body.replace("{{name}}",name)
		    subject = subject.replace("{{deadline}}",deadline.strftime("%b %d, %Y"))
		    body = body.replace("{{deadline}}",deadline.strftime("%b %d, %Y"))
		    subject = subject.replace("{{first-email}}",first_email.strftime("%b %d, %Y"))
		    body = body.replace("{{first-email}}",first_email.strftime("%b %d, %Y"))
		    subject = subject.replace("{{months-away}}",str(months_away))
		    body = body.replace("{{months-away}}",str(months_away))
		    unsubscribe_link = request.build_absolute_uri(reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,)))
		    body = body.replace("{{unsubscribe}}",unsubscribe_link)
		    view_emails_here = request.build_absolute_uri(reverse('campaigns:emails', args=(campaign.slug,)))
		    body = body.replace("{{view-emails}}",view_emails_here)
		    
		    myHeader = HEADER.replace("{{HOME_URL}}",request.build_absolute_uri(reverse('campaigns:campaign', args=(campaign.slug,))))
		    myHeader = myHeader.replace("{{LOGO_URL}}",request.build_absolute_uri(staticfiles_storage.url("images/%s_logo.png" % campaign.slug)))
		    htmlBody = "%s%s%s" % (myHeader.replace("{{unsubscribe}}",unsubscribe_link),body,END.replace("{{unsubscribe}}",unsubscribe_link))
		    textBody = strip_tags(body)
		    
		    connection.send_email(fromName + " <" + fromAddress + ">", 
			  subject, body=htmlBody, to_addresses=toAddressesStr, 
			  text_body=textBody, format="html", 
			  return_path=fromAddress)

		    return render(request, 'campaigns/thanks.html', {
			  'subscriber': subscriber,'campaign':campaign
			  })	    

	    return render(request, 'campaigns/subscribe.html', {
		'form': form,'campaign':campaign
		  })	    
	elif type == FIXED:
	    if request.method == 'GET':
		form = FixedForm(campaign=campaign)
	    else:
		# A POST request: Handle Form Upload
		form = FixedForm(request.POST,campaign=campaign) # Bind data from request.POST into a PostForm
	
		# If data is valid, proceeds to create a new post and redirect the user
		if form.is_valid():
		    name = form.cleaned_data['name']
		    email_address = form.cleaned_data['email_address']
		    options = form.cleaned_data['options']
		    subscriber = Subscriber.objects.create(name=name,
						email_address=email_address)
		    required_options = DeadlineOption.objects.filter(campaign=campaign,required=True)
		    for required in required_options:
			subscription = Subscription.objects.create(subscriber=subscriber,
					subscription=required)
		    for option in options:
			subscription = Subscription.objects.create(subscriber=subscriber,
					subscription=option)
					
		    ###Send Welcome Email
		    toAddressesStr = subscriber.email_address

		    subject = campaign.welcome_subject
		    body = campaign.welcome_content
		    subject = subject.replace("{{name}}",name)
		    body = body.replace("{{name}}",name)
		    unsubscribe_link = request.build_absolute_uri(reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,)))
		    body = body.replace("{{unsubscribe}}",unsubscribe_link)
		    view_emails_here =  request.build_absolute_uri(reverse('campaigns:emails', args=(campaign.slug,)))
		    body = body.replace("{{view-emails}}",view_emails_here)

		    myHeader = HEADER.replace("{{HOME_URL}}",request.build_absolute_uri(reverse('campaigns:campaign', args=(campaign.slug,))))
		    myHeader = myHeader.replace("{{LOGO_URL}}",request.build_absolute_uri(staticfiles_storage.url("images/%s_logo.png" % campaign.slug)))
		    htmlBody = "%s%s%s" % (myHeader.replace("{{unsubscribe}}",unsubscribe_link),body,END.replace("{{unsubscribe}}",unsubscribe_link))
		    textBody = strip_tags(body)

		    connection.send_email(fromName + " <" + fromAddress + ">", 
			  subject, body=htmlBody, to_addresses=toAddressesStr, 
			  text_body=textBody, format="html", 
			  return_path=fromAddress)
			  
		    return render(request, 'campaigns/thanks.html', {
			  'subscriber': subscriber,'campaign':campaign
			  })	    
	
	    return render(request, 'campaigns/subscribe.html', {
		'form': form,'campaign':campaign
		  })	    
		  
		  
	#string = "this is %s" % type
	#return HttpResponse(string)

def emails(request,campaign_slug):
	DEADLINE = 'deadline'
	FIXED = 'fixed'
	RELATIVE = 'relative'
  
	campaign = get_object_or_404(Campaign,slug=campaign_slug)

	try:
	  campaign = DeadlineCampaign.objects.get(slug=campaign_slug)
	  options = DeadlineOption.objects.filter(campaign=campaign)
	  type = DEADLINE
	except(ObjectDoesNotExist):
	  try:
	    campaign = FixedCampaign.objects.get(slug=campaign_slug)
	    options = FixedOption.objects.filter(campaign=campaign)
	    type = FIXED
	  except(ObjectDoesNotExist):
	    campaign = RelativeStartCampaign.objects.get(slug=campaign_slug)
	    type = RELATIVE
	    
	emails = []
	if type == FIXED:
		options = FixedOption.objects.filter(campaign=campaign)
		for option in options:
			option_emails = FixedEmail.objects.filter(option=option)
			emails = list(chain(emails, option_emails))
			
		emails.sort(key=lambda item:item.send_date, reverse=False)
		formatted_emails = []
		for email in emails:
			subject = email.subject.replace("{{name}}","you")
			body = email.content.replace("{{name}}","you")
			send_date = email.send_date.strftime("%b %d, %Y")
			formatted_emails.append({'subject':subject,'send_date':send_date,'content':body})
	elif type == RELATIVE:
		emails = RelativeStartEmail.objects.filter(campaign=campaign)
		formatted_emails = []
		for email in emails:
			subject = email.subject.replace("{{name}}","you")
			body = email.content.replace("{{name}}","you")
			if email.delta_months == 1:
				months = "1 month"
			elif email.delta_months > 1:
				months = "%s months" % str(email.delta_months)
			else:
				months = ""
			if email.delta_days == 1:
				days = "1 day"
			elif email.delta_days > 1:
				days = "%s days" % str(email.delta_days)
			else:
				days = ""
			send_date = "%s %s after subscription at %s" % (months, days, email.send_time.strftime("%I:%M %p"))
			formatted_emails.append({'subject':subject,'send_date':send_date,'content':body})
	elif type == DEADLINE:
		options = DeadlineOption.objects.filter(campaign=campaign)
		for option in options:
			option_emails = DeadlineEmail.objects.filter(option=option)
			emails = list(chain(emails, option_emails))
			
		emails.sort(key=lambda item:item.delta_days, reverse=False)
		emails.sort(key=lambda item:item.delta_months, reverse=False)
		formatted_emails = []
		for email in emails:
			body = email.content_beginning
			addons = DeadlineAddOn.objects.filter(email=email)
			for addon in addons:
				body += addon.content
			body += email.content_end
			subject = email.subject.replace("{{name}}","you")
			body = body.replace("{{name}}","you")
			subject = subject.replace("{{deadline}}","XXXX")
			body = body.replace("{{deadline}}","XXXX")
			subject = subject.replace("{{first-email}}","XXXX")
			body = body.replace("{{first-email}}","XXXX")
			subject = subject.replace("{{months-away}}","XX")
			body = body.replace("{{months-away}}","XX")
			if email.delta_months == 1:
				months = "1 month"
			elif email.delta_months > 1:
				months = "%s months" % str(email.delta_months)
			else:
				months = ""
			if email.delta_days == 1:
				days = "1 day"
			elif email.delta_days > 1:
				days = "%s days" % str(email.delta_days)
			else:
				days = ""
			send_date = "%s %s before deadline at %s" % (months, days, email.send_time.strftime("%I:%M %p"))
			formatted_emails.append({'subject':subject,'send_date':send_date,'content':body})
		
	return render(request, 'campaigns/emails.html', {
		'campaign': campaign,
		'emails':formatted_emails,
		})

def unsubscribe(request,subscriber_id,campaign_slug):
	subscriber = get_object_or_404(Subscriber,id=subscriber_id)
	campaign = get_object_or_404(Campaign,slug=campaign_slug)
	subscriptions = Subscription.objects.filter(subscriber=subscriber)

	if request.method == 'GET':
		return render(request, 'campaigns/unsubscribe.html', {
		'subscriptions': subscriptions,
		'subscriber':subscriber,
		'campaign':campaign,
		})
	else:
		connection = SESConnection(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY)
		
		for subscription in subscriptions:
			try: 
				subject = subscription.subscription.campaign.unsubscribe_subject
				body = subscription.subscription.campaign.unsubscribe_content
				slug = subscription.subscription.campaign.slug

			except(AttributeError):
				subject = subscription.subscription.unsubscribe_subject
				body = subscription.subscription.unsubscribe_content
				slug = subscription.subscription.slug

		toAddressesStr = subscriber.email_address

		subject = subject.replace("{{name}}",subscriber.name)
		body = body.replace("{{name}}",subscriber.name)
		view_emails_here = request.build_absolute_uri(reverse('campaigns:emails', args=(slug,)))
		body = body.replace("{{view-emails}}",view_emails_here)
		
		myHeader = HEADER.replace("{{HOME_URL}}",request.build_absolute_uri(reverse('campaigns:campaign', args=(campaign.slug,))))
		myHeader = myHeader.replace("{{LOGO_URL}}",request.build_absolute_uri(staticfiles_storage.url("images/%s_logo.png" % campaign.slug)))
		htmlBody = "%s%s%s" % (myHeader,body,END)
		textBody = strip_tags(body)

		connection.send_email(fromName + " <" + fromAddress + ">", 
			  subject, body=htmlBody, to_addresses=toAddressesStr, 
			  text_body=textBody, format="html", 
			  return_path=fromAddress)
			  
		subscriber.delete()

		return render(request, 'campaigns/unsubscribe_confirmation.html', {
			  'subscriber': subscriber,
			  'campaign':campaign,
			  })
