import socket
import concurrent.futures
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check_port(ip, port):
    """Verilmiş IP-də portun açıq olub-olmadığını yoxlayır."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        if s.connect_ex((ip, port)) == 0:
            return ip, port
    return None

def scan_network(network, ports, exclude_ips):
    """IP aralığında port scan aparır."""
    open_ports = []
    ip_range = [f"X.X.X.{i}" for i in range(1, 254)]
    ip_range = [ip for ip in ip_range if ip not in exclude_ips]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_scan = {executor.submit(check_port, ip, port): (ip, port) for ip in ip_range for port in ports}
        
        for future in concurrent.futures.as_completed(future_to_scan):
            result = future.result()
            if result:
                open_ports.append(result)
    
    return open_ports

def send_email(open_ports, disable_tls=False):
    """
    Açıq portlar barədə HTML formatında mail göndərir.
    disable_tls = True  -> starttls() çağırılmır (plain SMTP)
    disable_tls = False -> starttls() istifadə olunur (təhlükəsiz)
    """
    if not open_ports:
        print("✅ Açıq port tapılmadı, mail göndərilmir.")
        return
    
    smtp_server = "smtp.contoso.com" # <-- sizin smtp serverin ünvanı
    smtp_port = 587  # TLS üçün 587, plain üçün lazım olsa 25 istifadə oluna bilər
    smtp_user = "FROM ADDRESS"     # From və login
    smtp_password = "PASSWORD OF FROM ADDRESS"  # <-- buraya real şifrəni yaz

    to_email = "taryel@taryel.online" # <-- mailin çatdırılacağı ünvan
    subject = "⚠️ DIQQƏT: Aşkarlanan açıq portlar mövcuddur!"

    # HTML email bədəni
    body = """
    <html>
    <body>
    <p><b><font color="red">Diqqət!</font> Aşağıdakı IP ünvanlarında açıq portlar aşkarlanmışdır:</b></p>
    <table border="1" style="border-collapse: collapse;">
        <tr>
            <th style="background-color: blue; color: white; padding: 5px;">IP Ünvan</th>
            <th style="background-color: blue; color: white; padding: 5px;">Port</th>
        </tr>
    """

    for ip, port in open_ports:
        body += f"<tr><td style='padding: 5px;'>{ip}</td><td style='padding: 5px;'>{port}</td></tr>"

    body += "</table></body></html>"

    # Email obyektini formalaşdır
    message = MIMEMultipart()
    message['From'] = smtp_user
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            if not disable_tls:
                # Təhlükəsiz: starttls + sertifikat yoxlanışı
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
                print("🔐 TLS aktivləşdirildi və sertifikat yoxlanışı aparıldı.")
            else:
                # TLS söndürülmüş: starttls çağırılmır
                print("⚠️ TLS söndürülüb — bağlantı plain SMTP olacaq. Yalnız test/lab üçün istifadə et!")
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, message.as_string())
            print("📨 Mail uğurla göndərildi.")
    except Exception as e:
        print(f"❌ Mail göndərilmədi: {e}")

if __name__ == "__main__":
    ports_to_check = [3389, 21, 22, 23, 445]
    exclude_ips = ["X.X.X.X"]
    open_ports = scan_network("X.X.X.0/24", ports_to_check, exclude_ips)

    # Burada TLS-i söndürmək istəsən True qoy:
    disable_tls = True  # <-- True edərək TLS-i söndürə bilərsən (təhlükəsiz deyil)
    send_email(open_ports, disable_tls=disable_tls)
