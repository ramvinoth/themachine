import smtplib
import IdGenerator
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders



def sendEmail(fromAddr, toAddrList, ccAddrList, subject, labelAsStr, randomid,
              login, password, smtpServer='smtp.gmail.com:587'):

    # Taken from http://rosettacode.org/wiki/Send_an_email#Python
    message = MIMEMultipart()
    message['From'] = fromAddr
    message['To']= ','.join(toAddrList)
    message['Cc'] =  ','.join(ccAddrList)
    message['Subject']= subject	
    message.preamble = 'We have sighted the Human known as %s.' %labelAsStr
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("found_Faces/found_%s_%s.jpg" %(labelAsStr ,randomid), "rb").read())
    Encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename="found.jpg"')
    
    #message.attach(MIMEImage(file("found_Faces/found.jpg").read()))
    message.attach(part)
    server = smtplib.SMTP(smtpServer)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(fromAddr, toAddrList, message.as_string())
    server.quit()
    return problems
