import socket
import concurrent.futures
import requests
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =======================
# Azure AD App məlumatları
# =======================
tenant_id = "YOU ENTRA TENANT ID"
client_id = "YOU ENTRA ID APP CLIENT SECRET ID"
client_secret = "YOU ENTRA ID APP CLIENT SECRET KEY"
sender_email = "FROM EMAIL ADDRESS"
recipient_emails = ["TO ADDRESS 1", "TO ADDRESS 2"]

# =======================
# Port scanner funksiyaları
# =======================
def check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        if s.connect_ex((ip, port)) == 0:
            return ip, port
    return None

def scan_network(network, ports, exclude_ips):
    open_ports = []
    
    ip_range = [f"X.X.X.{i}" for i in range(1, 254)] # Birinci 3 okteti dolduraraq subneti scan edə bilərsiniz
    ip_range = [ip for ip in ip_range if ip not in exclude_ips]  # Exclude IPs
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_scan = {executor.submit(check_port, ip, port): (ip, port) for ip in ip_range for port in ports}
        
        for future in concurrent.futures.as_completed(future_to_scan):
            result = future.result()
            if result:
                open_ports.append(result)
    
    return open_ports

# =======================
# Microsoft Graph API ilə mail göndərmə
# =======================
def get_access_token():
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    token_r = requests.post(token_url, data=token_data)
    token_r.raise_for_status()
    return token_r.json().get("access_token")

def send_email(open_ports):
    if not open_ports:
        return
    
    access_token = get_access_token()
    graph_url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
    
    # Mailin HTML bədəni
    body = """
    <html>
    <body>
    <p><b><font color="red">Diqqet: asagidaki ip unvanlarinda risk yarada bilecek aciq portlar askar edilmisdir:</font></b></p>
    <table border="1" style="border-collapse: collapse;">
        <tr>
            <th style="background-color: blue; color: white; padding: 5px;">IP Unvan</th>
            <th style="background-color: blue; color: white; padding: 5px;">Port</th>
        </tr>
    """
    for ip, port in open_ports:
        body += f"<tr><td style='padding: 5px;'>{ip}</td><td style='padding: 5px;'>{port}</td></tr>"
    body += "</table></body></html>"
    
    mail_data = {
        "message": {
            "subject": "DIQQET: Askar edilen aciq portlar var!!!",
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [{"emailAddress": {"address": email}} for email in recipient_emails]
        },
        "saveToSentItems": "true"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(graph_url, headers=headers, data=json.dumps(mail_data))
    if response.status_code == 202:
        print("Mail uğurla göndərildi!")
    else:
        print(f"Xəta baş verdi: {response.status_code} - {response.text}")

# =======================
# Main
# =======================
if __name__ == "__main__":
    ports_to_check = [3389, 21, 22, 23, 445]
    exclude_ips = ["X.X.X.254"]
    open_ports = scan_network("X.X.X.0/24", ports_to_check, exclude_ips)
    send_email(open_ports)
