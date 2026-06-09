import smtplib
from email.mime.text import MIMEText

EMAIL = "gmaildummy987@gmail.com"
PASSWORD = "ixsl amkt lpyt mtte"

def send_otp(receiver, otp):

    msg = MIMEText(
        f"Kode OTP Anda adalah {otp}"
    )

    msg["Subject"] = "Verifikasi OTP"
    msg["From"] = EMAIL
    msg["To"] = receiver

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()
    server.login(EMAIL, PASSWORD)

    server.sendmail(
        EMAIL,
        receiver,
        msg.as_string()
    )

    server.quit()