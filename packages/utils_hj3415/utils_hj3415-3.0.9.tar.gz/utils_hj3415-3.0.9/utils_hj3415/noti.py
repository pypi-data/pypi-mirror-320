import os
import json
import datetime
import nest_asyncio

from telegram import Bot
from telegram.error import TelegramError

import asyncio
import telegram
import textwrap
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mail_to(title: str, text: str, to_mail:str) -> bool:
    """
    Sends an email with the specified title and text to a recipient using a Gmail account.

    This function sends an email from the Gmail account specified in environment variables.
    It attaches the current timestamp along with the provided text in the email body.
    The function uses SMTP with TLS for sending the email. Proper error handling for
    authentication, SMTP issues, and other exceptions is implemented.

    Arguments:
        title: The subject/title of the email.
        text: The body text of the email to be sent.
        to_mail: The recipient's email address.

    Raises:
        smtplib.SMTPAuthenticationError: If authentication with the SMTP server fails.
        smtplib.SMTPException: For general SMTP-related errors during email transmission.
        Exception: For any unexpected errors not covered by specific exceptions.

    Returns:
        bool: Returns True if the email was successfully sent, otherwise False.
    """
    from_mail = os.getenv('GMAIL_USER')
    app_pass = os.getenv('GMAIL_APP_PASS')
    if not from_mail or not app_pass:
        print('GMAIL_USER or GMAIL_APP_PASS is not set.')
        return False
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['Subject'] = title
    msg['To'] = to_mail
    current_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg.attach(MIMEText(f"{current_time_str}\n{text}"))

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(from_mail, app_pass)
            smtp.sendmail(from_mail, to_mail, msg.as_string())
            print(f'Sent mail form {from_mail} to {to_mail} successfully.')
            return True
        except smtplib.SMTPAuthenticationError as auth_err:
            print(f'Authentication failed: {auth_err}')
            return False
        except smtplib.SMTPException as smtp_err:
            print(f'SMTP error occurred: {smtp_err}')
            return False
        except Exception as e:
            print(f'Unexpected error occurred: {e}')
            return False


nest_asyncio.apply()


async def send_messge(bot: Bot, chat_id: str, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"Message sent to {bot}: {text}")
    except TelegramError as e:
        print(f"Failed to send message: {e}")


def telegram_to(botname: str, text: str):
    """
    Sends a message to a specified Telegram bot and chat using the given bot name
    and text. The function retrieves bot tokens and chat ID from the environment
    variables 'TELEGRAM_BOT_TOKENS' and 'TELEGRAM_CHAT_ID'. It selects the correct
    bot credentials based on the provided bot name, validates configurations, and
    sends the message asynchronously.

    Parameters:
        botname: str
            The name of the bot used to identify the appropriate credentials
            from the provided environment variable.
        text: str
            The message content to be sent to the specified chat.

    Raises:
        Exception:
            If the 'TELEGRAM_CHAT_ID' environment variable is not set.
        Exception:
            If the 'TELEGRAM_BOT_TOKENS' environment variable is not set.
        Exception:
            If there is an error decoding the 'TELEGRAM_BOT_TOKENS' environment
            variable as a JSON object.
        Exception:
            If the specified bot name is not found in the parsed bot dictionary.
    """
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not chat_id:
        raise Exception('TELEGRAM_CHAT_ID is not set.')
    bot_tokens = os.getenv('TELEGRAM_BOT_TOKENS')
    if not bot_tokens:
        raise Exception('TELEGRAM_BOT_TOKENS is not set.')

    # 문자열 -> 딕셔너리 변환
    try:
        bot_dict = json.loads(bot_tokens)
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON: {e}")

    if botname in bot_dict.keys():
        bot = telegram.Bot(token=bot_dict[botname])
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_messge(bot, chat_id, textwrap.dedent(text)))
    else:
        raise Exception(f'Invalid bot name : {botname} / {bot_dict.keys()}')