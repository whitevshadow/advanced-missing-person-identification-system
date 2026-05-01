import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path

from ..config import settings


def send_match_alert(
    *,
    to_email: str,
    missing_person_name: str,
    confidence_percent: float,
    sighting_city: str,
    sighting_description: str,
    image_path: str,
) -> dict:
    if not settings.smtp_user or not settings.smtp_password or not settings.smtp_from_email:
        return {
            "status": "skipped",
            "reason": "SMTP credentials are not configured",
        }

    message = EmailMessage()
    message["Subject"] = f"Missing Person Match Alert: {missing_person_name}"
    message["From"] = settings.smtp_from_email
    message["To"] = to_email

    message.set_content(
        "\n".join(
            [
                "A potential match has been detected.",
                f"Name: {missing_person_name}",
                f"Confidence: {confidence_percent}%",
                f"Sighting location: {sighting_city}",
                f"Reported description: {sighting_description or 'N/A'}",
            ]
        )
    )

    file_path = Path(image_path)
    if file_path.exists():
        mime_type, _ = mimetypes.guess_type(file_path.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        with file_path.open("rb") as attachment:
            message.add_attachment(
                attachment.read(),
                maintype=maintype,
                subtype=subtype,
                filename=file_path.name,
            )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)

    return {"status": "sent"}
