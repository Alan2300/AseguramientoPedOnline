import smtplib
from email.mime.text import MIMEText

def send_mail(subject, body):
    sender = "abimaruano@gmail.com"
    receiver = "abimaruano@gmail.com"
    password = "GuitAl2003" 

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"📧 Correo enviado: {subject}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        send_mail(sys.argv[1], sys.argv[2])
