import inspect
from unittest.mock import Mock

import pytest
from fastapi import BackgroundTasks
from fastapi_mail import FastMail
from pytest_mock import MockerFixture

from app.services.mail import MailService


@pytest.fixture
def background_tasks() -> Mock:
    return Mock(BackgroundTasks)


@pytest.fixture
def mail_sender() -> Mock:
    return Mock(FastMail)


@pytest.fixture
def service(
    background_tasks: Mock,
    mail_sender: Mock
) -> MailService:
    return MailService(
        background_tasks=background_tasks,
        mail_sender=mail_sender
    )


def test_send__add_target_to_background_tasks(
    mocker: MockerFixture,
    background_tasks: Mock,
    mail_sender: Mock,
    service: MailService
):
    send_methods = [
        getattr(service, method_name) for method_name in dir(service)
        if method_name.startswith('send_')
    ]
    message_schema = mocker.patch(
        'app.services.mail.service.MessageSchema'
    )

    for send_method in send_methods:
        call_kwargs = {
            param: Mock()
            for param in inspect.signature(send_method).parameters
        }
        send_method(**call_kwargs)

    assert background_tasks.add_task.call_count == len(send_methods)
    for call in background_tasks.add_task.call_args_list:
        assert call.args == (mail_sender.send_message,)
        assert call.kwargs['message'] == message_schema.return_value
