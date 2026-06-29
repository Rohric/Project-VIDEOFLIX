# Auth App — Cookie & Mail

Eine Django REST API für vollständige Benutzerauthentifizierung mit HTTP-Only-Cookies und E-Mail-Bestätigung.

Das System nutzt JWT-Tokens, die ausschließlich über sichere HTTP-Only-Cookies übertragen werden — das Frontend hat keinen direkten Zugriff auf die Tokens. Neue Konten bleiben inaktiv bis zur Bestätigung per E-Mail.

Das User-Modell basiert auf `AbstractUser` und enthält zusätzliche optionale Felder (Adresse, Handynummer, Geburtstag).

---

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Installation & Integration](#installation--integration)
- [Umgebungsvariablen (.env)](#umgebungsvariablen--env)
- [Django-Konfiguration](#django-konfiguration)
- [Migrationen & Start](#migrationen--start)
- [API Dokumentation](#api-dokumentation)
- [Testing ohne Email-Versendung](#testing-ohne-email-versendung)

---

## Voraussetzungen

- Python 3.10+
- Django 4.x oder 5.x
- Ein bestehendes Django-Projekt
- pip (Python Package Manager)

---

## Installation & Integration

### **Schritt 1: App in dein Projekt kopieren**

Kopiere den Ordner `auth_Mail_and_Cookies` in das Wurzelverzeichnis deines Django-Projekts.

```
dein-projekt/
├── manage.py
├── core/
├── auth_Mail_and_Cookies/    ← Hier kopieren
└── ...
```

### **Schritt 2: Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

Die notwendigen Pakete:
- `Django>=6.0` — Web Framework
- `djangorestframework>=3.14` — REST API Framework
- `djangorestframework-simplejwt>=5.2` — JWT Token Management
- `python-dotenv>=0.20` — Environment Variable Management

### **Schritt 3: `.env`-Datei erstellen**

Kopiere die Vorlage und fülle deine Werte ein:

```bash
cp .env.example .env
```

Öffne `.env` und trage deine echten Werte ein (siehe [Umgebungsvariablen](#umgebungsvariablen--env)).

### **Schritt 4: Django-Konfiguration anpassen**

Bearbeite `core/settings.py` und `core/urls.py` (siehe [Django-Konfiguration](#django-konfiguration)).

### **Schritt 5: Migrationen durchführen**

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Öffne http://localhost:8000/admin/ — User-Modell sollte registriert sein.

---

## Umgebungsvariablen (.env)

### **`.env.example` — Vorlage (Git versioniert, keine Secrets)**

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=
FRONTEND_URL=http://localhost:3000
COOKIE_SECURE=False
```

### **`.env` — Deine lokale Konfiguration (Git-ignoriert!)**

Kopiere `.env.example` zu `.env` und fülle mit echten Werten:

| Variable | Beschreibung | Entwicklung | Production |
|---|---|---|---|
| **`SECRET_KEY`** | Django Secret Key | `django-insecure-...` | Sicherer Schlüssel (generiert) |
| **`DEBUG`** | Debug-Modus | `True` | `False` |
| **`ALLOWED_HOSTS`** | Erlaubte Hosts (kommagetrennt) | `localhost,127.0.0.1` | `example.com,www.example.com` |
| **`EMAIL_BACKEND`** | Email-Versand-Backend | `django.core.mail.backends.console.EmailBackend` | `django.core.mail.backends.smtp.EmailBackend` |
| **`EMAIL_HOST`** | SMTP-Server | `smtp.mail.me.com` (iCloud) | Dein Email-Provider |
| **`EMAIL_PORT`** | SMTP-Port | `587` | `587` oder `465` |
| **`EMAIL_HOST_USER`** | SMTP-Benutzer | `deine-email@icloud.com` | Deine Email-Adresse |
| **`EMAIL_HOST_PASSWORD`** | SMTP-Passwort | App-spezifisches Passwort | App-spezifisches Passwort |
| **`EMAIL_USE_TLS`** | TLS aktivieren | `True` | `True` |
| **`DEFAULT_FROM_EMAIL`** | Absender-Adresse | `deine-email@icloud.com` | `noreply@example.com` |
| **`FRONTEND_URL`** | Frontend-URL (für Links in Emails) | `http://localhost:3000` | `https://example.com` |
| **`COOKIE_SECURE`** | Cookies nur über HTTPS | `False` | `True` |

### **Besonderheiten für iCloud:**

1. Geh zu https://appleid.apple.com
2. Security → App-specific passwords
3. Generiere ein Passwort für "Other App"
4. Verwende **dieses Passwort**, nicht dein iCloud-Passwort!

Beispiel:
```env
EMAIL_HOST_USER=emilmarsal@icloud.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### **Besonderheiten für Gmail:**

1. Aktiviere "Less secure app access" oder nutze App Passwords
2. Verwende deine Gmail-Adresse als `EMAIL_HOST_USER`
3. `EMAIL_HOST=smtp.gmail.com`

---

## Django-Konfiguration

### **`core/settings.py` — Anpassungen**

Füge diese Imports und Konfigurationen hinzu:

```python
import os
from dotenv import load_dotenv
from datetime import timedelta

# Environment-Variablen laden
load_dotenv()

# Secrets aus .env
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# INSTALLED_APPS — füge diese vier hinzu:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',                                      # ← Neu
    'rest_framework_simplejwt',                            # ← Neu
    'rest_framework_simplejwt.token_blacklist',            # ← Neu
    'auth_Mail_and_Cookies',                               # ← Neu
]

# Custom User Model
AUTH_USER_MODEL = "auth_Mail_and_Cookies.User"

# Default Auto Field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Konfiguration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "auth_Mail_and_Cookies.authentication.CookieJWTAuthentication",
    ),
}

# JWT Konfiguration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Email Konfiguration (alle Werte aus .env)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Frontend URL (für Activation- und Password-Reset-Links in Emails)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# Cookie Security
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "False") == "True"
```

### **`core/urls.py` — API Include**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("auth_Mail_and_Cookies.api.urls")),
]
```

---

## Migrationen & Start

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Server läuft unter http://localhost:8000

Admin-Interface: http://localhost:8000/admin/

---

## API Dokumentation

### `POST /api/register/`

Registriert einen neuen Benutzer im System.

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
}
```

**Success Response (HTTP 201)**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "activation_token"
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 201 | Benutzer erfolgreich erstellt |
| 400 | Validierungsfehler (Email bereits in Nutzung, Passwörter stimmen nicht) |

**Nebeneffekt:** Automatische Versendung einer Aktivierungs-E-Mail mit Bestätigungslink.

**Hinweis:** Der Username wird automatisch aus der Email generiert (z.B. `user` aus `user@example.com`). Ein expliziter Username ist nicht nötig.

---

### `GET /api/activate/<uidb64>/<token>/`

Aktiviert das Benutzerkonto mithilfe des per E-Mail gesendeten Tokens.

**URL Parameters**

| Name | Beschreibung |
|---|---|
| `uidb64` | Base64-codierte Benutzer-ID |
| `token` | Aktivierungstoken |

**Success Response (HTTP 200)**

```json
{
  "message": "Account successfully activated."
}
```

**Error Responses**

```json
{
  "detail": "Invalid activation link."
}
```

```json
{
  "detail": "Activation token expired."
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Account erfolgreich aktiviert |
| 400 | Ungültiger oder abgelaufener Token |

---

### `POST /api/login/`

Authentifiziert den Benutzer mit Email und Passwort. Setzt JWT-Tokens als HTTP-Only-Cookies.

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success Response (HTTP 200)**

```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user"
  }
}
```

**Error Responses**

```json
{
  "detail": "Invalid email or password."
}
```

```json
{
  "detail": "Account not activated. Please check your email."
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Login erfolgreich |
| 400 | Ungültige Credentials oder Account nicht aktiviert |

**Wichtig:** Die Tokens werden als HTTP-Only-Cookies gesetzt (`access_token`, `refresh_token`). Das Frontend liest die Tokens automatisch aus den Cookies — der Response-Body ist nur zu Informationszwecken.

---

### `POST /api/logout/`

Meldet den Benutzer ab und invalidiert den Refresh-Token.

**Request Body**

```json
{}
```

**Success Response (HTTP 200)**

```json
{
  "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Logout erfolgreich |
| 401 | Nicht authentifiziert |

**Nebeneffekt:** Cookies werden gelöscht und Refresh-Token auf Blacklist gesetzt.

---

### `POST /api/token/refresh/`

Gibt einen neuen Zugangstoken aus, wenn der alte Access-Token abgelaufen ist.

**Request Body**

```json
{}
```

**Success Response (HTTP 200)**

```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Access-Token wurde erneuert |
| 400 | Refresh-Token fehlt in Cookie |
| 401 | Ungültiger oder abgelaufener Refresh-Token |

**Nebeneffekt:** Neuer `access_token`-Cookie wird gesetzt.

---

### `GET /api/auth/profile/`

Gibt das Profil des authentifizierten Benutzers zurück.

**Request Body**

Keine

**Success Response (HTTP 200)**

```json
{
  "id": 1,
  "username": "user",
  "email": "user@example.com",
  "birthdate": "1990-01-15",
  "address": "123 Main Street",
  "handynumber": "+49 123 456789"
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Profil erfolgreich abgerufen |
| 401 | Nicht authentifiziert |

---

### `POST /api/password_reset/`

Sendet einen Link zum Zurücksetzen des Passworts an die E-Mail des Benutzers.

**Request Body**

```json
{
  "email": "user@example.com"
}
```

**Success Response (HTTP 200)**

```json
{
  "detail": "An email has been sent to reset your password."
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Reset-E-Mail wurde versendet |

**Wichtig:** Der Endpoint gibt immer `200 OK` zurück, auch wenn die Email nicht existiert. Das verhindert User-Enumeration-Angriffe.

---

### `POST /api/password_confirm/<uidb64>/<token>/`

Bestätigt die Passwortänderung mit dem in der E-Mail enthaltenen Token.

**URL Parameters**

| Name | Beschreibung |
|---|---|
| `uidb64` | Base64-codierte Benutzer-ID |
| `token` | Token zur Passwort-Zurücksetzung |

**Request Body**

```json
{
  "new_password": "newsecurepassword",
  "confirm_password": "newsecurepassword"
}
```

**Success Response (HTTP 200)**

```json
{
  "detail": "Your Password has been successfully reset."
}
```

**Error Responses**

```json
{
  "detail": "Passwords do not match."
}
```

```json
{
  "detail": "Invalid reset link."
}
```

```json
{
  "detail": "Reset token expired."
}
```

**Status Codes**

| Code | Bedeutung |
|---|---|
| 200 | Passwort erfolgreich geändert |
| 400 | Validierungsfehler oder ungültiger Link |

---

## Testing ohne Email-Versendung

Während der Entwicklung musst du nicht warten, bis echte Emails ankommen. Es gibt mehrere Test-Optionen:

### **Option 1: Console Backend (Standard in Development)**

Mit `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` werden alle Emails im Terminal ausgegeben:

```bash
python manage.py runserver
```

Registriere einen User in Postman → die Email wird unten im Terminal angezeigt:

```
Content-Type: text/plain; charset="utf-8"
Subject: Activate Your Account
From: test@example.com
To: test@example.com
Date: Mon, 29 Jun 2026 15:16:52 +0000

Hello test@example.com,

Welcome to our platform! Click the link below to activate your account:

http://localhost:3000/activate/MQ/day2o4-a7369082b5f6b3f634558d15ce0a619b/
```

Kopiere den Aktivierungslink und teste direkt in Postman:

```
GET http://localhost:8000/api/activate/MQ/day2o4-a7369082b5f6b3f634558d15ce0a619b/
```

Response sollte sein:
```json
{
  "message": "Account successfully activated."
}
```

### **Option 2: File Backend (Speichert Emails als Dateien)**

In `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=./emails
```

Emails werden in `./emails/` gespeichert als `.log`-Dateien.

### **Option 3: Echtes SMTP (Production)**

Wenn du bereit bist für echte Emails:

In `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mail.me.com
EMAIL_PORT=587
EMAIL_HOST_USER=deine-email@icloud.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=deine-email@icloud.com
```

Dann registriere einen User — die Email kommt in deine echte Inbox!

---

## Zusammenfassung der Integration in einem anderen Projekt

1. **Ordner kopieren** → `auth_Mail_and_Cookies/` in dein Projekt
2. **Dependencies installieren** → `pip install -r requirements.txt`
3. **`.env` konfigurieren** → Kopiere `.env.example` → `.env` → Werte eintragen
4. **Django anpassen**:
   - `settings.py`: INSTALLED_APPS, AUTH_USER_MODEL, REST_FRAMEWORK, SIMPLE_JWT, Email-Config
   - `urls.py`: `path("api/", include("auth_Mail_and_Cookies.api.urls"))`
5. **Migrationen** → `makemigrations` → `migrate`
6. **Testen** → Console-Backend zum Testen, dann SMTP konfigurieren

Das war's! Die Auth-App ist einsatzbereit. 🚀
