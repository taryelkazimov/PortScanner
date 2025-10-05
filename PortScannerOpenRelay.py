import socket
import concurrent.futures
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        if s.connect_ex((ip, port)) == 0:
            return ip, port
    return None

def scan_network(network, ports, exclude_ips):
    open_ports = []
    
    ip_range = [f"X.X.X.{i}" for i in range(1, 254)]
    ip_range = [ip for ip in ip_range if ip not in exclude_ips]  # Exclude IPs
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_scan = {executor.submit(check_port, ip, port): (ip, port) for ip in ip_range for port in ports}
        
        for future in concurrent.futures.as_completed(future_to_scan):
            print(future)
            result = future.result()
            if result:
                open_ports.append(result)
    
    return open_ports

def send_email(open_ports):
    if not open_ports:
        return
    
    smtp_server = "YOUR SMTP SERVER"
    from_email = "FROM EMAIL ADDRESS"
    to_email = "TO EMAIL ADDRESS"
    subject = "DIQQET: Askar edilen aciq portlar var!!!"
    
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    
    body = """
    <html>
    <body>
    <p><b><font color="red">Diqqet asagidaki ip unvanlarinda risk yarada bilecek aciq portlar askar edilmisdir:</font></b></p>
    <table border="1" style="border-collapse: collapse;">
        <tr>
            <th style="background-color: blue; color: white; padding: 5px;">IP Unvan</th>
            <th style="background-color: blue; color: white; padding: 5px;">Port</th>
        </tr>
    """
    
    for ip, port in open_ports:
        body += f"<tr><td style='padding: 5px;'>{ip}</td><td style='padding: 5px;'>{port}</td></tr>"
    
    body += "</table></body></html>"
    message.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP(smtp_server) as server:
        server.sendmail(from_email, to_email, message.as_string())

if __name__ == "__main__":
    ports_to_check = [3389, 21, 22, 23, 445]
    exclude_ips = ["X.X.X.X"]
    open_ports = scan_network("X.X.X.0/24", ports_to_check, exclude_ips)
    send_email(open_ports)