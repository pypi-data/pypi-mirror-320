import imaplib
import email
import loggerutility as logger 
from flask import Flask,request
import json
import time


class Email_Read:
    def read_email(self, email_config):
        try:
            mail = imaplib.IMAP4_SSL(email_config['host'], email_config['port'])
            mail.login(email_config['email'], email_config['password'])
            logger.log("login successfully")
            mail.select('inbox')

            while True:
                status, email_ids = mail.search(None, 'UNSEEN')
                emails = []
                
                if status == 'OK':
                    email_ids = email_ids[0].split()

                    if not email_ids: 
                        logger.log("Email not found, going to check new mail")
                    else:
                    
                        for email_id in email_ids:
                            email_body = ""
                            status, data = mail.fetch(email_id, '(RFC822)')
                            
                            if status == 'OK':
                                raw_email = data[0][1]
                                msg = email.message_from_bytes(raw_email)
                                
                                sender_email = msg['From']
                                cc_email = msg['CC']
                                bcc_email = msg['BCC']
                                subject = msg['Subject']
                                
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            email_body += part.get_payload(decode=True).decode()
                                else:
                                    email_body = msg.get_payload(decode=True).decode()
                                    
                                emails.append({
                                    'id': email_id,
                                    'sender': sender_email,
                                    'cc': cc_email,
                                    'bcc': bcc_email,
                                    'subject': subject,
                                    'body': email_body
                                })
                        logger.log(f"emails:: {emails}")
                time.sleep(10)
        
        except Exception as e:
            logger.log(f"Error reading emails: {str(e)}")
            raise
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

    def Read_Email(self):
        try:
            # while True:
            data = request.get_data('jsonData', None)
            data = json.loads(data[9:])
            logger.log(f"jsondata:: {data}")

            reciever_email_addr = data.get("reciever_email_addr")
            receiver_email_pwd = data.get("receiver_email_pwd")
            host = data.get("host")
            port = data.get("port")

            if not all([reciever_email_addr, receiver_email_pwd, host, port]):
                raise ValueError("Missing required email configuration fields.")

            logger.log(f"\nReceiver Email Address: {reciever_email_addr}\t{type(reciever_email_addr)}", "0")
            logger.log(f"\nReceiver Email Password: {receiver_email_pwd}\t{type(receiver_email_pwd)}", "0")
            logger.log(f"\nHost: {host}\t{type(host)}", "0")
            logger.log(f"\nPort: {port}\t{type(port)}", "0")

            email_config = {
                'email': reciever_email_addr,
                'password': receiver_email_pwd,
                'host': host,
                'port': int(port)
            }

            emails = self.read_email(email_config)            
            logger.log(f"Read_Email response: {emails}")
            # return "Successfully read email"

        except Exception as e:
            logger.log(f"Error in Read_Email: {str(e)}")
            # return "Problem in reading email"
        


