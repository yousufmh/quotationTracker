import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


def send_log_email(report,message):
    username = ""
    send_from = ''
    send_to = ''
    # send_to = ''

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = " "+report+" Application Log Email"

    htmlBody = """\
        <html>
          <body>
            <p>Dear Team,<br><br>
               Kindly Check the """+report+""" Report System As it returned a log Message <br> """+message+""" 
            </p>
          </body>
        </html>
        """
    part2 = MIMEText(htmlBody , "html")
    msg.attach(part2)
    smtp = smtplib.SMTP('', )
    smtp.sendmail(send_from, send_to.split(',') , msg.as_string())
    smtp.quit()
# send_email("","Test")

def send_html_excel_outside(to,subject,message,attach,cc='',bcc=''):
    username=""
    password= ""
    send_from = ''
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = to
    msg['Cc'] = cc
    msg['Bcc'] = bcc
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    port = '587'
    smtp = smtplib.SMTP('',port)
    smtp.starttls()
    smtp.ehlo()
    smtp.login(username,password)
    fp = open(attach, 'rb')
    part = MIMEBase('application','vnd.ms-excel')
    part.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=attach)
    msg.attach(part)
    htmlBody = message
    part2 = MIMEText(htmlBody , "html")
    msg.attach(part2)
    smtp.sendmail(send_from, to.split(',') + msg['Cc'].split(',')+msg['Bcc'].split(','), msg.as_string())
    smtp.quit()

def send_html_excel_inside(to,subject,message,attach,cc='',bcc=''):
    username=""
    send_from = ''
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = to
    msg['Cc'] = cc
    msg['Bcc'] = bcc
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    smtp = smtplib.SMTP('',)
    fp = open(attach, 'rb')
    part = MIMEBase('application','vnd.ms-excel')
    part.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=attach)
    msg.attach(part)
    htmlBody = message
    part2 = MIMEText(htmlBody , "html")
    msg.attach(part2)
    smtp.sendmail(send_from, to.split(',') + msg['Cc'].split(',')+msg['Bcc'].split(','), msg.as_string())
    smtp.quit()

def send_html_table_inside(to,subject,message,cc='',bcc=''):
    username=""
    send_from = ''
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = to
    msg['Cc'] = cc
    msg['Bcc'] = bcc
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    smtp = smtplib.SMTP('',)
    htmlBody = message
    part2 = MIMEText(htmlBody , "html")
    msg.attach(part2)
    smtp.sendmail(send_from, to.split(',') + msg['Cc'].split(',')+msg['Bcc'].split(','), msg.as_string())
    smtp.quit()