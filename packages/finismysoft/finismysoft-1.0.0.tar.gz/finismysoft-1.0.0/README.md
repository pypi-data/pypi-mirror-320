# FinisMySoft

FinisMySoft, [Finis.com.tr](https://finis.com.tr) ve Hasan Çağrı Güngör tarafından geliştirilmiş bir Python kütüphanesidir. Bu kütüphane, MySoft API ile kolay bir şekilde entegrasyon yapmanızı sağlar.

## Özellikler

- Fatura gönderimi
- İrsaliye gönderimi
- Gelen faturaların sorgulanması
- Fatura durumu kontrolü
- PDF ve HTML formatında fatura taslaklarının alınması
- Token yönetimi

---

## Kurulum

FinisMySoft kütüphanesini pip ile kolayca yükleyebilirsiniz:

```bash
pip install finismysoft
```

---

## Kullanım

### 1. Kütüphaneyi İçe Aktarma ve APIService Oluşturma

```python
from finismysoft import APIService

# API kimlik bilgilerinizi girin
api_credentials = {"username": "kullanici", "password": "sifre"}

# Servis nesnesini oluşturun
service = APIService(api_credentials, isReal=True)  # Gerçek ortamda çalışmak için isReal=True
```

---

### 2. Token Alımı

```python
token = service.get_token()
print(f"Token: {token}")
```

---

### 3. Fatura Gönderimi

```python
invoice_data = {
    "docNo": "12345",
    "currencyCode": "TRY",
    "invoiceType": "SATIS",
    # Diğer gerekli alanlar...
}

try:
    response = service.send_invoice(invoice_data)
    print("Fatura başarıyla gönderildi:", response)
except Exception as e:
    print(f"Hata: {e}")
```

---

### 4. İrsaliye Gönderimi

```python
irsaliye_data = {
    "docNo": "98765",
    "currencyCode": "TRY",
    "eDespatchType": "SEVK",
    # Diğer gerekli alanlar...
}

try:
    response = service.send_irsaliye(irsaliye_data)
    print("İrsaliye başarıyla gönderildi:", response)
except Exception as e:
    print(f"Hata: {e}")
```

---

### 5. Fatura Durumunu Sorgulama

```python
invoice_ettn = "3ADEFE96-9B5E-498A-B744-3DF27D574731"
try:
    status = service.get_invoice_status(invoice_ettn)
    print("Fatura durumu:", status)
except Exception as e:
    print(f"Hata: {e}")
```

---

### 6. Gelen Faturaları Listeleme

```python
start_date = "2025-01-01"
end_date = "2025-01-02"
pk_alias = "defaultpk@ornekadres.com"

try:
    invoices, after_value = service.incoming_invoices(start_date, end_date, pk_alias)
    print("Gelen faturalar:", invoices)
except Exception as e:
    print(f"Hata: {e}")
```

---

### 7. Fatura Taslağını PDF Olarak Alma

```python
payload = {
    "docNo": "12345",
    # Diğer gerekli alanlar...
}

try:
    zip_file_name = service.invoice_preview_pdf(payload)
    print(f"PDF ZIP dosyası kaydedildi: {zip_file_name}")
except Exception as e:
    print(f"Hata: {e}")
```

---

### 8. Fatura Taslağını HTML Olarak Alma

```python
payload = {
    "docNo": "12345",
    # Diğer gerekli alanlar...
}

try:
    zip_file_name = service.invoice_preview_html(payload)
    print(f"HTML ZIP dosyası kaydedildi: {zip_file_name}")
except Exception as e:
    print(f"Hata: {e}")
```

---

## Katkıda Bulunma

Katkıda bulunmak için [GitHub üzerinden](https://github.com/finiscomtr/finismysoft) bizimle iletişime geçebilirsiniz.

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.
