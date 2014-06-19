from django.utils.html import strip_tags
from django.core.mail import EmailMessage,EmailMultiAlternatives
from boto.ses import SESConnection
from remindme import settings


def send(subject,body,toAddressesStr,fromName,fromAddress,replacements):
  connection = SESConnection(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY)

  ###Send Welcome Email
  htmlBody = "%s%s%s" % (HEADER,body,END)

  textBody = strip_tags(body)
  textBody = textBody.replace("&nbsp;","")
  textBody = textBody.replace("&rsquo;","'")
  textBody = textBody.replace("&lsquo;","'")
  textBody = textBody.replace("&rdquo;",'"')
  textBody = textBody.replace("&ldquo;",'"')

  for key, value in replacements.iteritems():
    textBody = textBody.replace(key,value)
    htmlBody = htmlBody.replace(key,value)
    subject = subject.replace(key,value)

  connection.send_email(fromName + " <" + fromAddress + ">", 
    subject, body=htmlBody, to_addresses=toAddressesStr, 
    text_body=textBody, format="html", 
    return_path=fromAddress)

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
                              You are receiving this email because you signed up for {{CAMPAIGN_NAME}}, from the makers of <a href="http://http://www.boomeranggmail.com//" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang for Gmail</a>, <a href="http://www.boomerangcalendar.com/" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang Calendar</a>, <a href="http://www.baydin.com/boomerang/" target="_blank" style="color: #33b5e5; text-decoration: none;">Boomerang for Outlook</a>, and <a href="http://www.inboxpause.com/" target="_blank" style="color: #33b5e5; text-decoration: none;">Inbox Pause</a>. 
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
