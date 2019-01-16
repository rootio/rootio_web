import smtplib
from ..config import DefaultConfig


class RootIOMailMessage:

    def __init__(self):
        self.__smtp_server = DefaultConfig.MAIL_SERVER
        self.__smtp_username = DefaultConfig.MAIL_USERNAME
        self.__smtp_password = DefaultConfig.MAIL_PASSWORD
        self.__headers = dict()
        self.__message = ''
        self.__to = []
        self.__from = ''
        self.__subject = ''
        self.__body = ''

    def add_to_address(self, to_address):
        self.__to.append(to_address)

    def set_from(self, from_address):
        self.__from = from_address

    def set_header(self, h_name, h_value):
        self.__headers[h_name] = h_value

    # This should receive a list of tuples
    def set_headers(self, headers):
        for header in headers:
            self.set_header(header[0], header[1])

    def set_subject(self, subject):
        self.__subject = "Subject: %s \r\n\r\n" % subject

    def set_body(self, body):
        self.__body = body

    def append_to_body(self, extra_body):
        self.__body = "\n".join((self.__body, extra_body))

    def __create_message(self):
        # Prepend headers to body
        headers = ''
        for name, value in self.__headers.items():
            headers += '{}: {}\r\n'.format(name, value)
        self.__message = ''.join([
            headers,
            self.__subject,
            self.__body
        ])

    def send_message(self):
        smtp_server = smtplib.SMTP(self.__smtp_server)
        smtp_server.starttls()
        smtp_server.login(self.__smtp_username, self.__smtp_password)
        self.__create_message()
        smtp_server.sendmail(self.__from, self.__to, self.__message)
        smtp_server.quit()
        return True
