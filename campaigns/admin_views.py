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



def recursive_fixed(request):
        campaign = get_object_or_404(Campaign,slug="taxes")
        if request.method == 'GET':
                form = CreateForm()
        else:
                form = CreateForm(request.POST) # Bind data from request.POST into a PostForm
                if form.is_valid():
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        choice = form.cleaned_data['choices']
                        subject = form.cleaned_data['subject']
                        content = form.cleaned_data['content']
                        send_time = form.cleaned_data['time']
                        option = form.cleaned_data['option']
                        if choice == "monthly":
                                for r in rrule.rrule(rrule.MONTHLY, bymonthday=(start.day, -1), bysetpos=1, dtstart=start, until=end):
                                        send_date = r
                                        send_date = send_date.replace(hour=send_time.hour,minute=send_time.minute,second=send_time.second)
                                        email = FixedEmail.objects.create(send_date=send_date,subject=subject,content=content,option=option)
                        elif choice == "yearly":
                                for r in rrule.rrule(rrule.YEARLY, bysetpos=1, dtstart=start, until=end):
                                        send_date = r
                                        send_date = send_date.replace(hour=send_time.hour,minute=send_time.minute,second=send_time.second)
                                        email = FixedEmail.objects.create(send_date=send_date,subject=subject,content=content,option=option)
                        #return HttpResponse(x)
                        return redirect('/admin/campaigns/fixedemail/')
        return render(request, 'campaigns/create.html', {
            'form': form,'campaign':campaign,
              })

