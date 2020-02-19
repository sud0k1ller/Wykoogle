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
        #TODO
        #To pod spodem, to jakaś rzeź. Trzeba to zmienić, zanim walnie
        temp = re.findall('id="sub-(.*?)class="grid', (surowe_dane_string.text).replace('\n', ' '))
        temp_1 = re.findall('ludzie/([\w-]*?)/', str(temp))
        komentujacy = list(dict.fromkeys(temp_1))
    except:
        print("\t\t[!] Błąd ekstrakcji komentujących!")

    print("\t\t[+] ZAKOŃCZONO")
    return komentujacy   

def pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron_do_analizy):
    #TODO
    #Stworzyć mechanizm, pobierający id wpisów do określonej daty
    tablica_id_wpisow = []
    numer_strony = 1

    print("\n\tPobieranie ID wpisów użytkownika " + nazwa_uzytkownika + " z " + str(liczba_stron_do_analizy) + " pierwszych stron...")
    for strona in range(numer_strony, liczba_stron_do_analizy+1):
        surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony)) 
        #TODO
        #Tutaj też trzeba pomyśleć nad czymś sprytnieszym - xpath?
        temp = re.findall('data-id="(\d*)" data-type="entry"', (surowe_dane_strony.text).replace('\n', ' ')) 
        #Append kolejnych id z wielu stron 
        tablica_id_wpisow += list(dict.fromkeys(temp))
    print("\t\t[+] ZAKOŃCZONO")
    return tablica_id_wpisow
    


# ==== MAIN ====

tablica_analizowanych_nielubianych_uzytkownikow = ['A', 'B', 'C']
tablica_analizowanych_nielubianych_tagow = ['#X', '#Y', '#Z']
tablica_analizowanych_lubianych_uzytkownikow = ['D', 'E', 'F']
tablica_analizowanych_lubianych_tagow = ['#T', '#U', '#V']
nazwa_uzytkownika = "MikolajSobczak1985"
liczba_stron = 2

surowe_dane = plusujacy_wpis_surowe_dane(id_wpisu)
tablica_plusujacych_wpis = ekstrakcja_plusujacych_z_surowych_danych(surowe_dane)
surowe_dane = komentujacy_wpis_surowe_dane(id_wpisu)
komentujacy = ekstrakcja_komentujacych_wpis(surowe_dane)
id_wpisow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron) 

print("ID WPISÓW " + nazwa_uzytkownika + " z " + str(liczba_stron) + " stron:")
print(id_wpisow_uzytkownika)

print("PLUSUJĄCY:")
print(tablica_plusujacych_wpis)

print("KOMENTUJĄCY:")
print(komentujacy)


