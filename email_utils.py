from fastapi_mail import FastMail, MessageSchema, MessageType
from config import conf

async def send_welcome_email(email: str, first_name: str):
    subject = "Welcome to Social Media App!"
    body = f"""
    <h3>Hello {first_name},</h3>
    <p>Welcome aboard! Your account has been successfully created.</p>
    <p>We’re excited to have you with us.</p>
    <br>
    Regards,<br>
    Stixis Team
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
