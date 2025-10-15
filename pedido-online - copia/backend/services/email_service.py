import os
import smtplib
from email.message import EmailMessage


def send_email(to_address: str, subject: str, html_body: str):
    """
    Envía un correo electrónico con soporte HTML.
    Si no hay configuración SMTP, lo imprime en consola (modo log).
    """

    if os.getenv("EMAIL_MODE", "").lower() == "log" or not os.getenv("SMTP_HOST"):
        print("=== EMAIL LOG ===")
        print("To:     ", to_address)
        print("Subject:", subject)
        print("Body:\n", html_body)
        print("================")
        return

    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    pwd = os.getenv("SMTP_PASS", "")
    use_tls = os.getenv("SMTP_TLS", "true").lower() in ("1", "true", "yes")

    from_addr = os.getenv("MAIL_FROM", user or "no-reply@example.com")
    from_name = os.getenv("MAIL_FROM_NAME", "Pedidos App")

    msg = EmailMessage()
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content("Tu cliente de correo no soporta HTML.")
    msg.add_alternative(html_body, subtype="html")

    if use_tls:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            if user and pwd:
                server.login(user, pwd)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            if user and pwd:
                server.login(user, pwd)
            server.send_message(msg)
