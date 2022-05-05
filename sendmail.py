import smtplib


def sendmail(message, tomail):
    

    FROM = "realestateprediction7@gmail.com"
    pwd = "Real12345"

    SUBJECT = "Real Estate Price Prediction"
    TEXT = message

    # Prepare actual message
    message = "Subject: %s \n\n%s" % (SUBJECT, TEXT)
    # print(message)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(FROM, pwd)
    server.sendmail(FROM, tomail, message)
    server.close()
    print ('successfully sent the mail')

if __name__ == "__main__":
    sendmail("Test Mail", "techvkj@gmail.com")

