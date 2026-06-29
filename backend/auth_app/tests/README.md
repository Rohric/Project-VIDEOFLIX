# Auth App Tests

Pytest Test Suite für die Auth App API Endpoints.

## Test-Struktur

Für jeden API-Endpoint gibt es eine dedizierte Test-Datei:

- `test_POST_API_Register.py` - Registrierung
- `test_POST_API_Login.py` - Login
- `test_POST_API_Logout.py` - Logout
- `test_POST_API_TokenRefresh.py` - Token Refresh
- `test_GET_API_Activate.py` - Email Aktivierung
- `test_POST_API_PasswordReset.py` - Passwort Reset anfordern
- `test_POST_API_PasswordConfirm.py` - Passwort zurücksetzen

## Test-Abdeckung

Jede Datei enthält:
- ✅ **Happy Path Test** - Erfolgreicher Request
- ❌ **Unhappy Path Tests** - Verschiedene Error-Szenarien

## Fixtures

Die `conftest.py` definiert folgende Fixtures:

- `api_client` - Django REST Framework Test Client
- `test_user` - Aktiver Test-User (is_active=True)
- `inactive_test_user` - Inaktiver Test-User (is_active=False, nicht verifiziert)

## Tests ausführen

```bash
# Alle Tests
pytest

# Nur ein Test-File
pytest auth_app/tests/test_POST_API_Register.py

# Mit Verbose Output
pytest -v

# Mit Coverage Report
pytest --cov=auth_app

# Nur Happy Path
pytest -k "happy_path"

# Nur Unhappy Path
pytest -k "not happy_path"
```

## Dependencies

```bash
pip install pytest
pip install pytest-django
pip install djangorestframework-simplejwt
```

## Konfiguration

`pytest.ini` ist konfiguriert für Django und findet alle Tests in `auth_app/tests/`.
