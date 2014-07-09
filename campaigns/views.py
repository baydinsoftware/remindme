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
from django.core.urlresolvers import reverse
from datetime import datetime
from dateutil import tz
from dateutil import rrule
from itertools import chain
from django.contrib.staticfiles.storage import staticfiles_storage
from sendemail import send
import re
from django.shortcuts import redirect


def index(request):
  
	campaign_list = Campaign.objects.all()
	context = {'campaign_list':campaign_list}
	return render(request, 'campaigns/index.html',context)

	
def campaign(request,campaign_slug):
	campaign = get_object_or_404(Campaign,slug=campaign_slug)

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
			name = name[0].upper() + name[1:]
			email_address = form.cleaned_data['email_address']
			subscriber = Subscriber.objects.create(name=name,
						email_address=email_address)
			subscription = Subscription.objects.create(subscriber=subscriber,
						subscription=campaign)


			#send email with appropriate shortcodes replaced
			unsubscribe_link = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,subscriber.email_address)))
			overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:overview', args=(campaign.slug,)))
			home_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:campaign', args=(campaign.slug,)))
			logo_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),staticfiles_storage.url("images/%s_email_logo.png" % campaign.slug))
			fromName = campaign.name
			fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(campaign.slug)
			send(
				campaign.welcome_subject,
				campaign.welcome_content,
				email_address,
				fromName,
				fromAddress,
				{
					"{{name}}":name,
					"{{unsubscribe}}":unsubscribe_link,
					"{{overview_url}}":overview_url,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":campaign.name,
					"{{LOGO_URL}}":logo_url,
					"{{CAMPAIGN_SLUG}}":campaign.slug,
					}
			)
		    
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
			analytics = settings.ANALYTICS.get(campaign.slug)
			return render(request, 'campaigns/thanks.html', {
			  'subscriber': subscriber,'campaign':campaign,'analytics':analytics,
			  })
	    overview_url = reverse('campaigns:overview',args=(campaign.slug,))
	    description_text = campaign.description.replace("{{overview_url}}",overview_url)
	    analytics = settings.ANALYTICS.get(campaign.slug)
	    title = settings.CAMPAIGN_TITLE_LANDING.get(campaign.slug)
	    meta = settings.CAMPAIGN_LANDING_META.get(campaign.slug)
	    return render(request, 'campaigns/subscribe.html', {
		'form': form,'campaign':campaign,'description_text':description_text,
		'analytics':analytics,'title':title,'meta':meta,
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
				name = name[0].upper() + name[1:]
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
				all_options = chain(required_options, options)

				###Calculate ranges for each Welcome Email
				now_utc = datetime.utcnow().replace(tzinfo=utc_zone)
				before_date = now_utc + relativedelta(weeks=-campaign.ontime_margin_in_weeks)
				after_date = now_utc + relativedelta(weeks=campaign.ontime_margin_in_weeks)

				first_email = deadline_local #we're going to store the earliest email this subscriber would get to calculate appropriate welcome
				first_email_id = -2
				first_email_sent = deadline_utc
				first_email_months = str(0);
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

						#convert calucalted send date back to UTC
						send_date_utc = send_date_local.astimezone(utc_zone)

						now_utc = datetime.utcnow().replace(tzinfo=utc_zone)

						#if this intended send time is earlier than current earliest, save
						if first_email > send_date_utc:
							first_email = send_date_utc
							first_email_id = email.id
						#only add to queue if its send date has yet to happen
						if send_date_utc > now_utc:
							queue = EmailQueue.objects.create(send_date=send_date_utc,subscription=subscription,email=email)
						if first_email_sent > send_date_utc and send_date_utc > now_utc:
							first_email_sent = send_date_utc
							first_email_months = str(email.delta_months)
				months_away = 0
				for r in rrule.rrule(rrule.MONTHLY, bymonthday=(deadline_utc.day, -1), bysetpos=1, dtstart=now_utc, until=deadline_utc):
					months_away += 1
		
			    ###Send Appropriate Welcome Email
				if after_date > first_email and before_date < first_email:
					subject = campaign.welcome_subject
					body = campaign.welcome_content
					EmailQueue.objects.filter(subscription=subscription,object_id=first_email_id).delete()		
				elif after_date > first_email:
					subject = campaign.after_welcome_subject
					body = campaign.after_welcome_content
				else:
					subject = campaign.before_welcome_subject
					body = campaign.before_welcome_content
				
				#Send welcome email email with approrpaite information
				unsubscribe_link = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,subscriber.email_address)))
				overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:overview', args=(campaign.slug,)))
				home_url = settings.CAMPAIGN_URL.get(campaign.slug)
				logo_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),staticfiles_storage.url("images/%s_email_logo.png" % campaign.slug))
				fromName = campaign.name 
				fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(campaign.slug)
				send(
					subject,
					body,
					subscriber.email_address,
					fromName,
					fromAddress,
					{
					"{{name}}":name,
					"{{deadline}}":deadline.strftime("%b %d, %Y"),
					"{{first-email}}":first_email_sent.strftime("%b %d, %Y"),
					"{{first-email-months}}":first_email_months,
					"{{months-away}}":str(months_away),
					"{{unsubscribe}}":unsubscribe_link,
					"{{overview_url}}":overview_url,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":campaign.name,
					"{{LOGO_URL}}":logo_url,
					"{{CAMPAIGN_SLUG}}":campaign.slug,
					}
				)

				analytics = settings.ANALYTICS.get(campaign.slug)
				download_calendar = True
				return render(request, 'campaigns/thanks.html', {
					'subscriber': subscriber,'campaign':campaign, 'analytics':analytics,'download_calendar':download_calendar
				})
		overview_url = reverse('campaigns:overview',args=(campaign.slug,))
	#	overview_url = request.get_host()
		description_text = campaign.description.replace("{{overview_url}}",overview_url)
		analytics = settings.ANALYTICS.get(campaign.slug)
		title = settings.CAMPAIGN_TITLE_LANDING.get(campaign.slug)
		meta = settings.CAMPAIGN_LANDING_META.get(campaign.slug)
		return render(request, 'campaigns/subscribe.html', {
		'form': form,'campaign':campaign,'description_text':description_text,
		'analytics':analytics, 'title':title,'meta':meta
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
		    name = name[0].upper() + name[1:]
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

		    unsubscribe_link = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,subscriber.email_address)))
		    overview_url =  "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:overview', args=(campaign.slug,)))

		    home_url = settings.CAMPAIGN_URL.get(campaign.slug)
		    logo_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),staticfiles_storage.url("images/%s_email_logo.png" % campaign.slug))
		    fromName = campaign.name
		    fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(campaign.slug)
		    current_year = datetime.now().year
		    next_year = str(current_year + 1)
		    last_year = str(current_year - 1)
		    week = datetime.now() + timedelta(days=7)
		    fourdays = datetime.now() + timedelta(days=4)
		    send(
				campaign.welcome_subject,
				campaign.welcome_content,
				subscriber.email_address,
				fromName,
				fromAddress,
				{
					"{{name}}":name,
					"{{unsubscribe}}":unsubscribe_link,
					"{{overview_url}}":overview_url,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":campaign.name,
					"{{LOGO_URL}}":logo_url,
					"{{year}}":str(current_year),
					"{{year+}}":next_year,
					"{{year-}}":last_year,
					"{{week+}}":week.strftime("%A, %B %e"),
					"{{four_days}}":fourdays.strftime("%A, %B %e"),
					"{{CAMPAIGN_SLUG}}":campaign.slug,
					}
			)
		    analytics = settings.ANALYTICS.get(campaign.slug)
		    return render(request, 'campaigns/thanks.html', {
			  'subscriber': subscriber,'campaign':campaign,'analytics':analytics,
			  })	    
	    overview_url = reverse('campaigns:overview',args=(campaign.slug,))
	    description_text = campaign.description.replace("{{overview_url}}",overview_url)
	    analytics = settings.ANALYTICS.get(campaign.slug)
	    title = settings.CAMPAIGN_TITLE_LANDING.get(campaign.slug)
	    meta = settings.CAMPAIGN_LANDING_META.get(campaign.slug)
            return render(request, 'campaigns/subscribe.html', {
                'form': form,'campaign':campaign,'description_text':description_text,
                'analytics':analytics,'title':title,'meta':meta
                 })      
	  
		  
	#string = "this is %s" % type
	#return HttpResponse(string)

def overview(request,campaign_slug):
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
			subject = subject.replace("{{deadline}}","XX/XX/XX")
			body = body.replace("{{deadline}}","XX/XX/XX")
			subject = subject.replace("{{first-email}}","XX/XX/XX")
			body = body.replace("{{first-email}}","XX/XX/XX")
			subject = subject.replace("{{months-away}}","X")
			body = body.replace("{{months-away}}","X")
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
	analytics = settings.ANALYTICS.get(campaign.slug)
	title = settings.CAMPAIGN_TITLE_OVERVIEW.get(campaign.slug)
	meta = settings.CAMPAIGN_OVERVIEW_META.get(campaign.slug)
	return render(request, 'campaigns/overview.html', {
		'campaign': campaign,
		'emails':formatted_emails,
		'analytics':analytics,'title':title,'meta':meta,
		})

def unsubscribe(request,subscriber_id,subscriber_email_address,campaign_slug):
#	subscriber = get_object_or_404(Subscriber,id=subscriber_id)
	campaign = get_object_or_404(Campaign,slug=campaign_slug)
	try:
		subscriber = Subscriber.objects.get(id=subscriber_id,email_address=subscriber_email_address)
        	subscriptions = Subscription.objects.filter(subscriber=subscriber)
		
	except(ObjectDoesNotExist):
		analytics = settings.ANALYTICS.get(campaign.slug)
                message = """
                <p class='centered'>
                 Subscription not found.
                </p>
                """
                return render(request, 'campaigns/unsubscribe_confirmation.html', {
                          'campaign':campaign,
                          'analytics':analytics,
                          'message':message,
                                })

	if request.method == 'GET':
		return render(request, 'campaigns/unsubscribe.html', {
		'subscriptions': subscriptions,
		'subscriber':subscriber,
		'campaign':campaign,
		})
	else:
		
		for subscription in subscriptions:
			try: 
				subject = subscription.subscription.campaign.unsubscribe_subject
				body = subscription.subscription.campaign.unsubscribe_content
				slug = subscription.subscription.campaign.slug
				fromName = subscription.subscription.campaign.name
			except(AttributeError):
				subject = subscription.subscription.unsubscribe_subject
				body = subscription.subscription.unsubscribe_content
				slug = subscription.subscription.slug
				fromName = subscription.subscription.name

		overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:overview', args=(slug,)))
		home_url = settings.CAMPAIGN_URL.get(campaign.slug)
		logo_url = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),staticfiles_storage.url("images/%s_email_logo.png" % campaign.slug))
		unsubscribe_link = "%s%s" % (settings.CAMPAIGN_URL.get(campaign.slug),reverse('campaigns:unsubscribe', args=(campaign.slug,subscriber.id,subscriber.email_address)))
		fromName = campaign.name
		fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(campaign.slug)
		send(
				subject,
				body,
				subscriber.email_address,
				fromName,
				fromAddress,
				{
					"{{name}}":subscriber.name,
					"{{overview_url}}":overview_url,
					"{{HOME_URL}}":home_url,
					"{{CAMPAIGN_NAME}}":campaign.name,
					"{{LOGO_URL}}":logo_url,
					"{{unsubscribe}}":unsubscribe_link,
					 "{{CAMPAIGN_SLUG}}":campaign.slug,
					}
			)
			  
		analytics = settings.ANALYTICS.get(campaign.slug)
		message = """
		<p class='centered'>
                 We're sad to see you go, %s    
                </p>
		<p class='centered'>
                 Maybe we'll see you around.
                </p>
		""" % subscriber.name
		subscriber.delete()
		return render(request, 'campaigns/unsubscribe_confirmation.html', {
			  'subscriber': subscriber,
			  'campaign':campaign,
			  'analytics':analytics,
			  'message':message,
				})

def send_test(request,email_id,email_address):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
		return HttpResponse("Not a valid email.")
	else:

		DEADLINE = 'deadline'
		FIXED = 'fixed'
		RELATIVE = 'relative'
		try:
			email = DeadlineEmail.objects.get(id=email_id)
			type = DEADLINE
		except(ObjectDoesNotExist):
			try:
				email = FixedEmail.objects.get(id=email_id)
				type = FIXED
			except(ObjectDoesNotExist):
				email = Email.objects.get(id=email_id)
				type = RELATIVE

		if type == FIXED:
			print email_address
			unsubscribe_link = ""
			slug = email.option.campaign.slug
			overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(slug), reverse('campaigns:overview', args=(slug,)))
			home_url = settings.CAMPAIGN_URL.get(slug)
			logo_url = "%s/static/images/%s_email_logo.png" % (home_url,slug)
			current_year = datetime.now().year
			next_year = str(current_year + 1)
			last_year = str(current_year - 1)
			week = datetime.now() + timedelta(days=7)
			fourdays = datetime.now() + timedelta(days=4)
			fromName = email.option.campaign.name
			fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(slug)
			send(
			email.subject,
			email.content,
			email_address,
			email.option.campaign.name,
			fromAddress,
				{
				"{{name}}":"Baydin",
				"{{unsubscribe}}":unsubscribe_link,
				"{{overview_url}}":overview_url,
				"{{HOME_URL}}":settings.CAMPAIGN_URL.get(slug),
				"{{CAMPAIGN_NAME}}":email.option.campaign.name,
				"{{LOGO_URL}}":logo_url,
				"{{year}}":str(current_year),
                                "{{year+}}":next_year,
                                "{{year-}}":last_year,
				"{{week+}}":week.strftime("%A, %B %e"),
				"{{four_days}}":fourdays.strftime("%A, %B %e"),
				 "{{CAMPAIGN_SLUG}}":slug,
				}
			)
			return render(request, 'campaigns/email.html', {
				  'email': email,
				  'campaign_slug':slug,
				  'email_address':email_address,
				  })

		elif type == DEADLINE:
			body = email.content_beginning
			body += email.content_end

			deadline_utc = datetime.now().strftime("%b %d, %Y")
			slug = email.option.campaign.slug
			unsubscribe_link = ""
			overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(slug), reverse('campaigns:overview', args=(slug,)))
			home_url = settings.CAMPAIGN_URL.get(slug)
			logo_url = "%s/static/images/%s_email_logo.png" % (home_url, slug)
			fromName = email.option.campaign.name
			fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(slug)
			send(
			email.subject,
			body,
			email_address,
			fromName,
			fromAddress,
				{
				"{{name}}":"Baydin",
				"{{deadline}}":"Jan 01, 2001",
				"{{unsubscribe}}":unsubscribe_link,
				"{{overview_url}}":overview_url,
				"{{HOME_URL}}":home_url,
				"{{CAMPAIGN_NAME}}":email.option.campaign.name,
				"{{LOGO_URL}}":logo_url,
				 "{{CAMPAIGN_SLUG}}":slug,
				}
			)

			return render(request, 'campaigns/email.html', {
				  'email': email,
				  'body':body,
				  'campaign_slug':slug,
				  'email_address':email_address,
				  })
		else:
			return HttpResponse("Automatic tests for relative email unavailable. Alter times and try test subscriptions.")

def send_test_addons(request,email_id,email_address):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
		return HttpResponse("Not a valid email.")
	else:
		email = DeadlineEmail.objects.get(id=email_id)
		options = DeadlineOption.objects.filter(campaign=email.option.campaign)
		body = email.content_beginning
		for option in options:
			add_ons = DeadlineAddOn.objects.filter(email=email,option=option)
			for add_on in add_ons:
				body += add_on.content
				body += """
"""
		body += email.content_end

		deadline_utc = datetime.now().strftime("%b %d, %Y")
		slug = email.option.campaign.slug
		unsubscribe_link = ""
		overview_url = "%s%s" % (settings.CAMPAIGN_URL.get(slug), reverse('campaigns:overview', args=(slug,)))
		home_url = settings.CAMPAIGN_URL.get(slug)
		logo_url = "%s/static/images/%s_email_logo.png" % (home_url, slug)
		fromName = email.option.campaign.name
		fromAddress = settings.CAMPAIGN_FROM_ADDRESS.get(slug)
		send(
		email.subject,
		body,
		email_address,
		fromName,
		fromAddress,
			{
			"{{name}}":"Baydin",
			"{{deadline}}":"Jan 01, 2000",
			"{{unsubscribe}}":unsubscribe_link,
			"{{overview_url}}":overview_url,
			"{{HOME_URL}}":home_url,
			"{{CAMPAIGN_NAME}}":email.option.campaign.name,
			"{{LOGO_URL}}":logo_url,
			 "{{CAMPAIGN_SLUG}}":slug,
			}
		)

		return render(request, 'campaigns/email.html', {
			  'email': email,
			  'body':body,
			  'campaign_slug':slug,
			  'email_address':email_address,
			  })

def download(request):

	slug = request.POST['slug']
	subscriber_id = request.POST['subscriber_id']
	subscriber = get_object_or_404(Subscriber,id=subscriber_id)
	campaign = get_object_or_404(Campaign,slug=slug)

	trail = ""
	subscriptions = Subscription.objects.filter(subscriber=subscriber)

	for subscription in subscriptions:
		events = EmailQueue.objects.filter(subscription=subscription)
		for event in events:
			time = event.send_date
			description = "Look out for an email or visit %s for more info on this reminder." % (settings.CAMPAIGN_URL.get(slug))
			trail = """%s
BEGIN:VEVENT
SUMMARY:%s
UID:%s-%s
DESCRIPTION:%s
DTSTART;TZID=UTC:%s
DTEND;TZID=UTC:%s
END:VEVENT""" % (trail,event.email.subject,settings.CAMPAIGN_FROM_ADDRESS.get(slug),event.id,description,time.strftime('%Y%m%dT%H%M%S'),time.strftime('%Y%m%dT%H%M%S'))

	response = HttpResponse(content_type='text')
	response['Content-Disposition'] = 'attachment; filename="%s_reminders_calendar.ics"' % slug
	response.write("""BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
PRODID:-//Baydin//%s//EN%s
END:VCALENDAR""" % (campaign.name,trail))

	return response

