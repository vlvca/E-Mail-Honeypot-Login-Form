import socket
import threading
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


HONEYPOT_PORT = 80


EMAIL_ADDRESS = "YOUR MAIL ADRESS HERE"
EMAIL_PASSWORD = "YOUR PASSWORD/AUTH HERE"
RECIPIENT_EMAIL = "RECIPENT EMAIL HERE"


def get_mac_address():

    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)])
    return mac_address


def send_email_notification(subject, body):
    try:

        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = RECIPIENT_EMAIL
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))


        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, message.as_string())
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Error sending email notification: {e}")


def handle_client(client_socket, client_address):
    print(f'Connection from {client_address}')
    password = None
    try:

        request_data = client_socket.recv(4096).decode('utf-8')


        password_index = request_data.find('password=')
        if password_index != -1:
            password = request_data[password_index + 9:].split('&')[0]
            print(f"Password entered: {password}")


        client_ip = client_address[0]
        client_mac = get_mac_address()
        print(f"Client IP Address: {client_ip}, MAC Address: {client_mac}")


        visit_subject = "Honeypot Visit Notification"
        visit_body = f"Date and Time: {datetime.now()}\nClient IP Address: {client_ip}\nClient MAC Address: {client_mac}\nClient visited the honeypot."
        send_email_notification(visit_subject, visit_body)


        if password:
            submit_subject = "Honeypot Password Submission"
            submit_body = f"Date and Time: {datetime.now()}\nClient IP Address: {client_ip}\nClient MAC Address: {client_mac}\nPassword submitted: {password}"
            send_email_notification(submit_subject, submit_body)


        http_response = """\
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<title>Example Login Form</title>
</head>
<body>
<h2>Example Login Form</h2>
<form action="/" method="post">
  <label for="password">Password:</label><br>
  <input type="password" id="password" name="password"><br><br>
  <input type="submit" value="Submit">
</form>
</body>
</html>
"""


        client_socket.sendall(http_response.encode())

    except Exception as e:
        print(f"Error handling client request from {client_address}: {e}")
    finally:

        client_socket.close()


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        server_socket.bind(('0.0.0.0', HONEYPOT_PORT))


        server_socket.listen(5)

        print(f'Honeypot listening on port {HONEYPOT_PORT}...')

        try:
            while True:

                client_socket, client_address = server_socket.accept()


                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.start()

        except KeyboardInterrupt:
            print("Shutting down the honeypot...")


if __name__ == "__main__":
    main()