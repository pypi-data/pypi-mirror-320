import imaplib
import email
from email.message import Message
import datetime
import time
import loggerutility as logger


class Email_Draft:
    def draft_email(self, email_config, email_details, response_content):
        try:
            with imaplib.IMAP4_SSL(host=email_config['host'], port=imaplib.IMAP4_SSL_PORT) as imap_ssl:
                imap_ssl.login(email_config['email'], email_config['password'])
                logger.log(f"login successfully")
                
                message = Message()
                message["From"] = email_config['email']
                message["To"] = email_details['sender']
                message["CC"] = email_details['cc']
                
                subject = email_details['subject']
                if not subject.startswith("Re:"):
                    subject = f"Re: {subject}"
                message["Subject"] = subject
                
                mail_details = f'{datetime.datetime.now().strftime("On %a, %b %d, %Y at %I:%M %p")} {email_details["sender"]} wrote:'
                message.set_payload(f"{response_content}\n\n{mail_details}\n\n{email_details['body']}")
                
                utf8_message = str(message).encode("utf-8")
                logger.log(f"utf8_message:: {utf8_message}")
                imap_ssl.append("[Gmail]/Drafts", '', imaplib.Time2Internaldate(time.time()), utf8_message)
                
                return True, utf8_message.decode("utf-8")
                
        except Exception as e:
            logger.log(f"Error creating draft: {str(e)}")
