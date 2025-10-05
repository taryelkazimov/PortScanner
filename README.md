# Network Port Scanner & Alert Script

**Qısa təsvir:**  
Bu repo lokal / icazəli şəbəkə aralığında port skanı aparır və əgər müəyyən "riskli" portlar aşkar edilərsə, e-poçt bildirişi göndərir.

---

## Əhəmiyyətli: Fork edəndə dəyişdirilməli olan yerlər

> **Heç vaxt** həssas məlumatları (SMTP parolu, client secret və s.) birbaşa koda yazmayın. Aşağıdakı parametrləri əvvəlcə özünüzə uyğunlaşdırın.

### Fayldakı parametrlər (skript daxilində)

1. **IP range & şəbəkə prefiksi**  
   - Faylda axtarın: `ip_range = [f"X.X.X.{i}" for i in range(1, 254)]`  
   - **Dəyişdirin**: `X.X.X.` → sizin prefiks (məsələn `192.168.1.`), və ya istifadə edin `ipaddress` modulu ilə CIDR (`"192.168.1.0/24"`).

2. **İstisna ediləcək IP-lər (exclude list)**  
   - Faylda: `exclude_ips = ["X.X.X.X"]`  
   - **Dəyişdirin**: burada idarəçi cihazları/servisləri, skana məruz qalmamalı ünvanları göstərin.

3. **Skan ediləcək portlar**  
   - Faylda: `ports_to_check = [3389, 21, 22, 23, 445]`  
   - **Dəyişdirin**: sizin təhlükə modelinə görə (RDP, FTP, SSH, Telnet, SMB və s.).

4. **SMTP konfiqurasiyası** (`send_email` funksiyası daxilində)  
   - `smtp_server = "YOUR SMTP SERVER"` → **Dəyişdirin**: `smtp.mail.example.com`  
   - `from_email = "FROM EMAIL ADDRESS"` → **Dəyişdirin**: `alerts@yourdomain.com`  
   - `to_email = "TO EMAIL ADDRESS"` → **Dəyişdirin**: `secops@yourdomain.com` (və ya siyahı)

> **Tövsiyə:** SMTP istifadəçi adı və şifrəsini mütləq environment dəyişəni olaraq saxlayın (məs.: `SMTP_USER`, `SMTP_PASS`). `.env` faylından oxumaq üçün `python-dotenv` istifadə edə bilərsiniz (amma `.env` faylını `.gitignore`-ə əlavə edin).

---

## Tövsiyə edilən təhlükəsizlik & deploy praktikaları

- **Secrets:** SMTP parolları və digər həssas məlumatlar üçün `ENV` və ya secrets manager istifadə edin (Azure Key Vault, AWS Secrets Manager və s.).
- **STARTTLS:** SMTP ilə əlaqə üçün `STARTTLS` (port 587) və `server.login()` istifadə edin.
- **IP range:** `ipaddress` modulundan istifadə etmək daha etibarlıdır.
- **Skan etmədən öncə icazə alın.** Xarici şəbəkələri skan edərkən hüquqi məsuliyyətə görə mütləq sahibdən yazılı icazə alın.

---


