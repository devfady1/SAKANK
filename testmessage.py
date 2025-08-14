import smtplib
from email.mime.text import MIMEText

# إعداداتك
EMAIL_HOST_USER = "sakankoffichial@gmail.com"
EMAIL_HOST_PASSWORD = "reqgvrlkotaieeun"
DEFAULT_FROM_EMAIL = "noreply@sakany.com"

# بيانات الرسالة
to_email = "fadya5323@gmail.com"
subject = "Test Email"
body = "This is a test email from the project."

# تكوين الرسالة
msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = DEFAULT_FROM_EMAIL
msg["To"] = to_email

# إرسال الرسالة
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.sendmail(DEFAULT_FROM_EMAIL, to_email, msg.as_string())

print("✅ Test email sent successfully!")
