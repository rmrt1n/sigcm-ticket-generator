from PIL import Image, ImageDraw, ImageFont
import sys
import csv
import base64
import random
import time

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from email_config import *

import numpy as np
import qrcode
import psycopg2
import psycopg2.extras

BASE_URL = "https://e-ticket-pkpm.vercel.app/check-in/"
#  BASE_URL = 'localhost:3000/check-in/'
DB_NAME = ""
DB_USER = ""
DB_PASS = ""
DB_HOST = ""
GROUP_INV_1 = ""
GROUP_INV_2 = ""

VALID_CMDS = {
    "generate": lambda: make_tickets(),
    "send": lambda: send(),
    "update_db": lambda: update_db(),
}

FONT_BOLD_50 = {
    'A': 34, 'B': 28, 'C': 33, 'D': 31, 'E': 27, 'F': 25, 'G': 37, 'H': 32, 'I': 14, 'J': 21, 'K': 19, 'L': 25, 'M': 42,
    'N': 37, 'O': 38, 'P': 28, 'Q': 37, 'R': 30, 'S': 28, 'T': 26, 'U': 32, 'V': 34, 'W': 46, 'X': 36, 'Y': 31, 'Z': 32,
    'a': 29, 'b': 28, 'c': 22, 'd': 28, 'e': 25, 'f': 18, 'g': 29, 'h': 28, 'i': 14, 'j': 14, 'k': 26, 'l': 13, 'm': 41,
    'n': 28, 'o': 26, 'p': 29, 'q': 29, 'r': 20, 's': 22, 't': 19, 'u': 28, 'v': 28, 'w': 37, 'x': 28, 'y': 26, 'z': 23, ' ': 13,
}

FONT_SEMIBOLD_32 = {
    'A': 21, 'B': 18, 'C': 21, 'D': 19, 'E': 17, 'F': 16, 'G': 24, 'H': 21, 'I': 9,  'J': 13, 'K': 18, 'L': 16, 'M': 26,
    'N': 23, 'O': 24, 'P': 18, 'Q': 24, 'R': 19, 'S': 18, 'T': 17, 'U': 21, 'V': 21, 'W': 29, 'X': 22, 'Y': 19, 'Z': 20,
    'a': 18, 'b': 18, 'c': 14, 'd': 18, 'e': 16, 'f': 11, 'g': 18, 'h': 18, 'i': 8,  'j': 9,  'k': 16, 'l': 8,  'm': 26,
    'n': 18, 'o': 17, 'p': 18, 'q': 18, 'r': 13, 's': 14, 't': 12, 'u': 18, 'v': 17, 'w': 23, 'x': 17, 'y': 16, 'z': 15, ' ': 7,
}

FONT_SEMIBOLD_40 = {
    '0': 24, '1': 13, '2': 23, '3': 22, '4': 21, '5': 22, '6': 23, '7': 22, '8': 23, '9': 23,
}

PRIMARY = '#1B4575'

SUBJECT = 'Invitation: SIGCM 2022 - Facing Recession: How to Overcome The Crisis?'
BODY = '''
<html>
  <body>
    <div style="background: #eee; padding: 1rem 0;">
      <div style="max-width: 512px; margin: 0 auto; background: #fff; padding: 2rem; border: 1px solid #ccc; border-radius: 8px">
        <p>Hello Futurist! 🌐 🙌</p>
        <p>You're registered for <em><strong>SIGCM 2022 - "Facing Recession: How To Overcome The Crisis?"</strong></em> 💸🔍📈</p>

        <p>Below are the details of the event as well as the attached e-ticket, which you'll need to show on the day of the event.</p>

        <p><strong>📝 EVENT DETAILS</strong></p>
        <div style="padding-left: 1rem">
          <p style="margin: 0">🗓️ Date : December 10th, 2022</p>
          <p style="margin: 0">⏰ Time : 13:50 - END</p>
          <p style="margin: 0">📍 Place : Binus Kemanggisan Auditorium (4th Floor)</p>
        </div>

        <p>Add <a target="_blank" href="https://calendar.google.com/calendar/event?action=TEMPLATE&amp;tmeid=MzM5dDZpcmFtdWFhZ3ZjNDJvOXVlYmphYXMgb2ZmaWNpYWxzaWdjbUBt&amp;tmsrc=officialsigcm%40gmail.com">this event</a> to your calendar so you don't forget!</p>
        <p>If you have any questions or need any help, feel free to contact us!</p>
        <p><strong>📞 CONTACT PERSONS</strong> (Chat only)</p>
        <ol style="padding-left: 0; list-style-position: inside;">
          <li><em>Kevin</em>
            <div style="padding-left: 1rem; margin-bottom: .5rem">
              <p style="margin: 0">WhatsApp number: <a href="https://web.whatsapp.com/send?phone=+123456789">+123456789</a></p>
              <p style="margin: 0">LINE ID: </p>
            </div>
          </li>
          <li><em>Tiara</em>
            <div style="padding-left: 0; list-style-position: inside">
              <div style="padding-left: 1rem">
                <p style="margin: 0">WhatsApp number: <a href="https://web.whatsapp.com/send?phone=+123456789">+123456789</a></p>
                <p style="margin: 0">LINE ID: </p>
              </div>
            </div>
          </li>
        </ol>
        <small>Tip: Click on the phone numbers to directly start a chat with them</small>

        <p>Don't forget to show your e-ticket for registration on the day of the event to confirm your attendace ‼️. We look forward to seeing you soon! 👋</p>

        <p>Best Regards,</p>
        <strong style="margin: 1rem 0 0 0">Kevin Christanto</strong>
        <p style="margin: 0">Project Manager</p>
      </div>
    </div>
  </body>
</html>
'''

def strlen(text, font):
    return sum([font[i] for i in text])

def format_name(name, max_len, font):
    tokens = name.split(' ')
    res = tokens[0]
    new_line = res
    for i in tokens[1:]:
        res += ('\n' if strlen(new_line + i, font) > max_len else ' ') + i
        new_line = res.split('\n')[-1]
    if res.count('\n') > 1:
        cut = [i for i, j in enumerate(res) if j == '\n'][1]
        res = res[:cut]
    return res

def ticket_filename(participant, fileonly=False):
    file = '{}-{}-{}.jpg'.format(participant['id'], '-'.join(participant['nama'].split(' ')[:2]), participant['nim'])
    return file if fileonly else './tickets/' + file

def add_qr(participant, ticket):
    draw = ImageDraw.Draw(ticket)
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(
        BASE_URL
        + base64.b64encode(
            str.encode(
                '{{"id":{},"nim":{}}}'.format(participant['id'], participant['nim'])
            )
        ).decode()
    )
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=PRIMARY, back_color="#f7ecde")
    ticket.paste(qr_img, (1538 + (397 - 246) // 2, 218))

def add_text(participant, ticket):
    draw = ImageDraw.Draw(ticket)

    # ['Thin', 'ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']
    font_bold_50 = ImageFont.truetype('./fonts/static/LeagueSpartan-Bold.ttf', 50)
    font_semibold_32 = ImageFont.truetype('./fonts/static/LeagueSpartan-SemiBold.ttf', 32)
    font_semibold_40 = ImageFont.truetype('./fonts/static/LeagueSpartan-SemiBold.ttf', 40)

    # no peserta
    no_peserta = str(participant['id']).zfill(3)
    draw.multiline_text(
        (1538 + (397 - strlen(no_peserta, FONT_SEMIBOLD_40)) // 2, 156),
        no_peserta,
        font=font_semibold_40,
        fill=PRIMARY,
        align='center',
    )

    # nama peserta qr
    nama = format_name(participant['nama'], 228, FONT_SEMIBOLD_32)
    draw.multiline_text(
        ((1538 + (397 - strlen(max(nama.split('\n'), key=len), FONT_SEMIBOLD_32)) // 2), 466 + 18),
        nama,
        font=font_semibold_32,
        fill=PRIMARY,
        align='center',
    )

    # nama peserta left
    nama = format_name(participant['nama'], 296, FONT_BOLD_50)
    draw.multiline_text(
        (135 + (328 - strlen(max(nama.split('\n'), key=len), FONT_BOLD_50)) // 2, 385 + (67 if len(nama.split('\n')) == 1 else 44)),
        nama,
        font=font_bold_50,
        fill=PRIMARY,
        align='center',
    )

def generate(participant):
    ticket = Image.open('./template.jpg')
    add_qr(participant, ticket)
    add_text(participant, ticket)
    #  ticket.show()
    ticket.save(ticket_filename(participant))


def make_tickets():
    filename = sys.argv[2]
    participants = list(csv.DictReader(open(filename)))
    for participant in participants:
        print('{}. generating ticket for {} ({})'.format(participant['id'], participant['nama'], participant['nim']))
        generate(participant)

def generate_email(participant):
    msg = MIMEMultipart()
    msg['From'] = Header(EMAIL)
    msg['To'] = Header(participant['email'])
    msg['Subject'] = Header(SUBJECT)
    msg.attach(MIMEText(BODY, 'html'))

    with open(ticket_filename(participant), 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename={}'.format(ticket_filename(participant, fileonly=True)))
    msg.attach(part)

    return msg

def send_email(participant):
    msg = generate_email(participant)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(HOST, PORT, context=context) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, participant['email'], msg.as_string())

def send():
    filename = sys.argv[2]
    participants = list(csv.DictReader(open(filename)))
    for i, participant in enumerate(participants):
        if i % 10 == 0:
            time.sleep(random.randint(0, 5))
        print('sending message to {} ({})'.format(participant['nama'], participant['nim']))
        send_email(participant)

def update_db():
    filename = sys.argv[2]
    participants = list(csv.DictReader(open(filename)))
    print('uploading data to db...')
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
    )
    cur = conn.cursor()
    data = [
        (i['id'], i['nama'].title(), i['nim'], i['no_hp'], i['email'], 30)
        for i in participants
    ]
    psycopg2.extras.execute_values(
        cur,
        'insert into "Participant" (id, name, nim, phone, email, "groupId") values %s',
        data,
    )
    conn.commit()
    conn.close()
    print('\nupload finished')

def print_help():
    n = len(sys.argv)
    if n > 1 and n != 3:
        print("Error: invalid number of arguments\n")

    print(
        """Usage: {} <command> file\n
Available commands:
  generate      generate tickets
  send          send bulk email
  update_db     update database
          """.format(
            sys.argv[0]
        )
    )

def main():
    if len(sys.argv) != 3:
        print_help()
        return
    cmd = sys.argv[1]
    if cmd not in VALID_CMDS.keys():
        print('Error: invalid command\n')
        print_help()
        return
    VALID_CMDS[cmd]()

if __name__ == '__main__':
    main()
