import smtplib
import sys
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


# Open file and read all lines
location = sys.path[0]
with open(f"{location}/test_creds.txt", 'r') as f:
    lines = f.readlines()

args = []
img_paths = []
i = 0

# Iterate over each line read from the file and retrieve the args
for line in lines:
    line = line.strip()
    if i < 8:
        args.append(line)
    else:
        img_paths.append(line)
    i += 1

# Establish connection with gmail http service
server = smtplib.SMTP(args[0], int(args[1]))
server.ehlo()
server.starttls()
server.ehlo()

# Implement the args
sender_email = args[2]
sender_pwd = args[3]
sender_name = args[4]
target = args[5]
subject = args[6]

# Login to mailing service
server.login(sender_email, sender_pwd)

# Create message
msg = MIMEMultipart()
msg['From'] = sender_name
msg['To'] = target
msg['Subject'] = subject

# Read text data
with open(f"{location}/{args[7]}", 'r') as f:
    message = f.read()

# Attach the message to the email, and search for file attachments
# TO-DO (Maybe?) Add a method to send the same image multiple times.
msg.attach(MIMEText(message, 'plain'))
for j in range(len(img_paths)):
    filename = img_paths[j]
    attachment = open(f"{location}/{filename}", 'rb')

    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())

    encoders.encode_base64(p)
    p.add_header('Content-Disposition', f'attachment; filename={filename.split("/")[-1]}')
    msg.attach(p)

# Convert data to a valid email
text = msg.as_string()

# Send the email to the target
server.sendmail(sender_email, target, text)