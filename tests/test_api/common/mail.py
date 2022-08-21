from email.mime.multipart import MIMEMultipart

from app.resources.mail.subjects import SUBJECT_FOR_THANK
from tests.test_api.dtos import MetaUser
from tests.utils.mail import check_mail_body_contains


__all__ = ['assert_thank_mail_is_correct']


def assert_thank_mail_is_correct(
    meta_user: MetaUser,
    mail: MIMEMultipart
) -> None:
    assert mail['subject'] == SUBJECT_FOR_THANK
    assert mail['to'] == meta_user.email
    assert check_mail_body_contains(mail, 'thank')
