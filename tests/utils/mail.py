from email.mime.multipart import MIMEMultipart


__all__ = ['check_mail_body_contains']


def check_mail_body_contains(
    mail: MIMEMultipart,
    needle: str
) -> bool:
    if mail.is_multipart():
        return any(
            _check_payload_contains(part, needle)
            for part in mail.get_payload()
        )
    return _check_payload_contains(mail, needle)


def _check_payload_contains(
    payload: MIMEMultipart,
    needle: str
) -> bool:
    normalized_needle = needle.casefold()
    normalized_payload = (
        payload.get_payload(decode=True)
        .decode()
        .casefold()
    )
    return normalized_needle in normalized_payload
