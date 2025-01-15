# Konvo Python SDK

Konvotech API için resmi Python SDK.

## Kurulum

```bash
pip install konvo
```

## Kullanım

### Temel Kurulum

```python
from konvo import KonvoClient

# API anahtarınızla istemciyi başlatın
client = KonvoClient(api_key="api_anahtarınız_buraya")

# API sağlık durumunu kontrol edin
health_status = client.system.check_health()
print(health_status)  # {"status": "healthy"}
```

### Yapılandırma Seçenekleri

`KonvoClient` çeşitli yapılandırma seçeneklerini destekler:

```python
client = KonvoClient(
    api_key="api_anahtarınız_buraya",
    max_retries=3,          # Başarısız istekler için yeniden deneme sayısı
    log_level="WARNING",    # Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    timeout=30              # İstek zaman aşımı (saniye)
)
```

## Hata Yönetimi

SDK özel istisnalar fırlatır:

- `KonvoError`: Tüm Konvotech API hataları için temel istisna
- `APIError`: API istekleri başarısız olduğunda fırlatılır, status_code içerir

```python
try:
    client.system.check_health()
except APIError as e:
    print(f"API isteği başarısız oldu. Durum kodu: {e.status_code}: {str(e)}")
```
