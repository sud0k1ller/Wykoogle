#!/bin/python3

import re
import requests
from lxml import html

id_wpisu = 46855743

#def wyswietl_naglowek():
#   
#   wyswielt informacje o skrypcie i jego przeznaczeniu
#   wyswietl informacje o wybranych do analizy tagach i uzytkownikach
#   zakoncz
#    
   

def plusujacy_wpis_surowe_dane(id_spisu):
       
    print("WPIS: " + str(id_wpisu))
    print("\tPobieranie danych o plusujących wpis...")
    try:
        url_json_plusujacy_wpis = "https://www.wykop.pl/ajax2/wpis/upvoters/" + str(id_wpisu)    
        surowe_dane_string  = requests.get(url_json_plusujacy_wpis)
    except:
        print("\t\t[!] Błąd pobierania danych!")
    
    print("\t\t[+] ZAKOŃCZONO")
    return surowe_dane_string.text

def ekstrakcja_plusujacych_z_surowych_danych(surowe_dane_string):
    
    print("\tEkstrakcja plusujących...")
    try:
        tablica_plusujacych = []
        tablica_plusujacych = re.findall('ludzie\\\/(.*?)\\\/ class', surowe_dane_string)
    except:
        print("\t\t[!\ Błąd ekstrakcji plusujących!")
    
    print("\t\t[+] ZAKOŃCZONO")
    return tablica_plusujacych

def komentujacy_wpis_surowe_dane(id_wpisu):
    
    print("\tPobieranie danych o komentujących wpis...")
    try:
        url_wpisu = "https://www.wykop.pl/wpis/" + str(id_wpisu)
        surowe_dane_string = requests.get(url_wpisu)
    except:
        print("\t\t[!] Błąd pobierania danych!")

    print("\t\t[+] ZAKOŃCZONO")
    return surowe_dane_string

def ekstrakcja_komentujacych_wpis(surowe_dane_string):
   
    print("\tEkstrakcja komentujących...") 
    try:
        #To pod spodem, to jakaś rzeź. Trzeba to zmienić, zanim walnie
        temp = re.findall('id="sub-(.*?)class="grid', (surowe_dane_string.text).replace('\n', ' '))
        temp_1 = re.findall('ludzie/([\w-]*?)/', str(temp))
        komentujacy = list(dict.fromkeys(temp_1))
    except:
        print("\t\t[!] Błąd ekstrakcji komentujących!")

    print("\t\t[+] ZAKOŃCZONO")
    return komentujacy   

def pobierz_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron_do_analizy):
    
    tablicy_id_wpisow = []
    print("\tPobieranie ID wpisów użytkownika " + nazwa_uzytkownika + " z " + liczba_stron_do_analizy + " pierwszysch stron...")

    print("\\tt[+] ZAKOŃCZONO")
    


# ==== MAIN ====

tablica_analizowanych_uzytkownikow = ['A', 'B', 'C']
tablica_analizowanych_tagow = ['#X', '#Y', '#Z']

surowe_dane = plusujacy_wpis_surowe_dane(id_wpisu)
tablica_plusujacych_wpis = ekstrakcja_plusujacych_z_surowych_danych(surowe_dane)
surowe_dane = komentujacy_wpis_surowe_dane(id_wpisu)
komentujacy = ekstrakcja_komentujacych_wpis(surowe_dane)

print("PLUSUJĄCY:")
print(tablica_plusujacych_wpis)

print("KOMENTUJĄCY:")
print(komentujacy)

