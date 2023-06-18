<h1>Aplikacja internetowa bazy danych policyjnych</h1>

Aplikacja internetowa bazy danych policyjnych to aplikacja oparta na Flask, która umożliwia upoważnionym użytkownikom zarządzanie i wyszukiwanie informacji dotyczących osób i zdarzeń w bazie danych policyjnych.
Wymagania

Aby uruchomić aplikację, potrzebujesz następujących elementów:

    Python w wersji 3.x
    Flask
    Flask-Session
    MySQL Connector

<h1>Konfiguracja</h1>

Instalacja sktptów venv:

    py -3 -m venv .venv

Przed uruchomieniem aplikacji, upewnij się, że skonfigurowałeś szczegóły połączenia z bazą danych. Zmodyfikuj następujące linie w kodzie:

    cnx = mysql.connector.connect(user='funkcjonariusz', password='password123',
                              host='127.0.0.1',
                              database='policedb')

Zaktualizuj wartości user, password, host i database zgodnie z konfiguracją Twojego serwera MySQL.
<h1>Użycie</h1>

Aby uruchomić aplikację, uruchom skrypt Pythona oraz aktywuj skrypt venv flaska w terminalu:

    .venv\Scripts\activate

    flask --app app.py run

Po uruchomieniu aplikacji, możesz uzyskać do niej dostęp w przeglądarce internetowej pod adresem http://localhost:5000/.
<h1>Trasy (Routes)</h1>

Aplikacja udostępnia następujące trasy (routes):

    / - Strona główna wyświetlająca ogólne informacje o aplikacji.
    /osoby - Umożliwia upoważnionym użytkownikom wyszukiwanie osób w bazie danych.
    /osoba_info - Wyświetla szczegółowe informacje o konkretnej osobie.
    /osoby_add - Umożliwia upoważnionym użytkownikom dodawanie nowych osób do bazy danych.
    /wydarzenia - Umożliwia upoważnionym użytkownikom wyszukiwanie zdarzeń w bazie danych.
    /wydarzenie_info - Wyświetla szczegółowe informacje o konkretnym zdarzeniu.
    /wydarzenia_add - Umożliwia upoważnionym użytkownikom dodawanie nowych zdarzeń do bazy danych.
    /radiowozy - Umożliwia upoważnionym użytkownikom przeglądanie i zarządzanie informacjami dotyczącymi pojazdów policyjnych.

<h1>Autoryzacja i Uprawnienia</h1>

Aplikacja wykorzystuje prosty system uwierzytelniania. Użytkownicy muszą się zalogować, aby uzyskać dostęp do funkcji wymagających autoryzacji. Istnieją trzy poziomy uprawnień: Poziom 1, Poziom 2 i Poziom 3. Każdy poziom ma inne prawa dostępu.

    Poziom 1: Podstawowy poziom dostępu, może uzyskać dostęp do wszystkich publicznych tras.
    Poziom 2: Może uzyskać dostęp do tras dotyczących osób i zdarzeń, w tym wyszukiwania i przeglądania szczegółów.
    Poziom 3: Najwyższy poziom dostępu, może dodawać nowe osoby, zdarzenia oraz zarządzać pojazdami policyjnymi.

Aby zalogować się, aplikacja obecnie używa metody zastępczej w pliku helpers.py. Należy zmodyfikować tę metodę zgodnie z wybranym mechanizmem uwierzytelniania.
<h1>Szablony (Templates)</h1>

Aplikacja wykorzystuje szablony HTML znajdujące się w katalogu templates. Każda trasa ma swój odpowiadający mu plik szablonu HTML.
<h1>Pliki statyczne (Static Files)</h1>

Katalog static zawiera pliki statyczne, takie jak arkusze stylów CSS i obrazy używane w szablonach HTML aplikacji.
<h1>Helpers</h1>

Plik helpers.py zawiera funkcje pomocnicze używane w aplikacji, w tym sprawdzanie autoryzacji i uprawnień.
<h1>Obsługa Błędów</h1>

Aplikacja dostarcza niestandardowe obsługiwacze błędów dla błędów HTTP 404 (nie znaleziono) i HTTP 500 (wewnętrzny błąd serwera). Odpowiednie szablony HTML dla tych błędów znajdują się w katalogu templates.
<h1>Kontrola Cache</h1>

Aplikacja ustawia odpowiednie nagłówki kontroli pamięci podręcznej (cache control) w celu zapewnienia, że odpowiedzi nie są buforowane w pamięci podręcznej.
<h1>Obsługa Po Zapytaniu (After Request Handler)</h1>

Aplikacja wykorzystuje obsługę po zapytaniu (after_request handler) w celu zapewnienia, że odpowiedzi nie są buforowane w pamięci podręcznej poprzez ustawienie odpowiednich nagłówków.

