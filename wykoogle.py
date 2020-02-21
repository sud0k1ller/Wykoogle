#!/bin/python3

import re
import requests
from lxml import html

def plusujacy_wpis_surowe_dane(id_wpisu):
    try:
        url_json_plusujacy_wpis = "https://www.wykop.pl/ajax2/wpis/upvoters/" + str(id_wpisu)    
        surowe_dane_string  = requests.get(url_json_plusujacy_wpis)
    except:
        print("\t\t[!] Błąd pobierania danych!")
        return -1

    return surowe_dane_string.text


def ekstrakcja_plusujacych_wpis(surowe_dane_string):
    try:
        tablica_plusujacych = []
        tablica_plusujacych = re.findall('ludzie\\\/(.*?)\\\/ class', surowe_dane_string)
    except:
        print("\t\t[!] Błąd ekstrakcji plusujących!")
        return -1        
    
    return tablica_plusujacych


def pobranie_plusujacych_wpis(id_wpisu):
    surowe_dane = plusujacy_wpis_surowe_dane(id_wpisu)
    return ekstrakcja_plusujacych_wpis(surowe_dane)


def komentujacy_wpis_surowe_dane(id_wpisu):
    try:
        url_wpisu = "https://www.wykop.pl/wpis/" + str(id_wpisu)
        surowe_dane_string = requests.get(url_wpisu)
    except:
        print("\t\t[!] Błąd pobierania danych!")

    return surowe_dane_string


def ekstrakcja_komentujacych_wpis(surowe_dane_string):
    try:
        temp = re.findall('id="sub-(.*?)class="grid', (surowe_dane_string.text).replace('\n', ' '))
        temp_1 = re.findall('ludzie/([\w-]*?)/', str(temp))
        komentujacy = list(dict.fromkeys(temp_1))
    except:
        print("\t\t[!] Błąd ekstrakcji komentujących!")
        return -1    

    return komentujacy   


def pobranie_komentujacych_wpis(id_wpisu):
    surowe_dane = komentujacy_wpis_surowe_dane(id_wpisu)
    return ekstrakcja_komentujacych_wpis(surowe_dane) 


def pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron_do_analizy):
    tablica_id_wpisow = []
    numer_strony = 1

    for strona in range(numer_strony, liczba_stron_do_analizy+1):
        surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony)) 
        temp = re.findall('data-id="(\d*)" data-type="entry"', (surowe_dane_strony.text).replace('\n', ' ')) 
        tablica_id_wpisow += list(dict.fromkeys(temp))

    return tablica_id_wpisow

 
def pobranie_id_wpisow_na_tagu(nazwa_tagu, liczba_stron_do_analizy):
    tablica_id_wpisow = []
    numer_strony = 1

    for strona in range(numer_strony, liczba_stron_do_analizy+1):
        surowe_dane_strony = requests.get("https://wykop.pl/tag/" + nazwa_uzytkownika + "/strona/" + str(numer_strony)) 
        temp = re.findall('data-id="(\d*)" data-type="entry"', (surowe_dane_strony.text).replace('\n', ' ')) 
        tablica_id_wpisow += list(dict.fromkeys(temp))

    return tablica_id_wpisow

 
def pobranie_listy_analizowanych_tagow_i_uzytkownikow():
    return [nielubiany_uz.rstrip('\n') for nielubiany_uz in  open('nielubiani_uzytkownicy', 'r')], [nielubiany_tag.rstrip('\n') for nielubiany_tag in  open('nielubiane_tagi', 'r')], [lubiany_uz.rstrip('\n') for lubiany_uz in  open('lubiani_uzytkownicy', 'r')], [lubiany_tag.rstrip('\n') for lubiany_tag in  open('lubiane_tagi', 'r')]   


def pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron):
    lista_id_postow_uzytkownika = []
    lista_komentujacych_uzytkownika = []
    lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
    for id_wpisu in lista_id_postow_uzytkownika:
        lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)

    return lista_komentujacych_uzytkownika


def pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron):
    lista_id_postow_uzytkownika = []
    lista_plusujacych_uzytkownika = []
    
    lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
    for id_wpisu in lista_id_postow_uzytkownika:
        lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)

    return lista_plusujacych_uzytkownika


def pobranie_aktywnych_lubiany_uz(nazwa_uzytkownika, liczba_stron):
    lista_wszystkich_plusujacych = []
    lista_wszystkich_komentujacych = []

    lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)
    lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)   
    wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
    wszyscy_aktywni.remove(nazwa_uzytkownika)
    return wszyscy_aktywni


#===== MAIN =====
liczba_stron = 2
tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow = pobranie_listy_analizowanych_tagow_i_uzytkownikow()

print(pobranie_aktywnych_lubiany_uz(tablica_lubianych_uzytkownikow[0], 1))



