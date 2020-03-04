#!/bin/python3

import re
import requests
from lxml import html
from bs4 import BeautifulSoup as bs
from datetime import date

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


def pobranie_id_wpisow_uzytkownika(*argumenty):
    
    nazwa_uzytkownika = argumenty[0]
    tablica_id_wpisow = []
    numer_strony = 1 

    if len(argumenty) == 2:
        liczba_stron_do_analizy = argumenty[1]

        try:
            for strona in range(numer_strony, liczba_stron_do_analizy+1):
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony))  
                soup = bs(surowe_dane_strony.text, "lxml")
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                for wpis in lista_wpisow:
                    tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
        except:
            print("\t\t[!] Błąd pobrania id wpisów użytkownika!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = date.fromisoformat(argumenty[2])
        data_koncowa = date.fromisoformat(argumenty[1])
        flaga_data_w_zakresie = 0
        flaga_data_poza_zakresem = 0        

        try:
            while not flaga_data_poza_zakresem:
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony))  
                numer_strony += 1
                soup = bs(surowe_dane_strony.text, "lxml")
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                for wpis in lista_wpisow:
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    print(data_wpisu)
                    if not flaga_data_w_zakresie and data_wpisu >= data_poczatkowa:
                        flaga_data_w_zakresie = 1
                        print("W ZAKRESIE")
                    if flaga_data_w_zakresie and data_wpisu < data_koncowa:
                        flaga_data_poza_zakresem = 1 
                        print("POZA ZAKRESEM")
                        break 
                    if flaga_data_w_zakresie:
                        print("DODAJĘ ID")
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))   
        except:
            print("\t\t[!] Błąd pobrania id wpisów użytkownika!")
            return -1

    if len(argumenty) > 3 or len(argumenty) < 2:
        print("Niewłaściwa liczba argumentów funkcji 'pobranie_id_wpisow_uzytkownika'")
        return -1
 
    print(tablica_id_wpisow) 
    return tablica_id_wpisow

 
def pobranie_id_wpisow_na_tagu(nazwa_tagu, liczba_stron_do_analizy):
    tablica_id_wpisow = []
    numer_strony = 1

    try:
        for strona in range(numer_strony, liczba_stron_do_analizy+1):
            surowe_dane_strony = requests.get("https://wykop.pl/tag/" + nazwa_uzytkownika + "/strona/" + str(numer_strony)) 
            temp = re.findall('data-id="(\d*)" data-type="entry"', (surowe_dane_strony.text).replace('\n', ' ')) 
            tablica_id_wpisow += list(dict.fromkeys(temp))
    except:
        print("\t\t[!] Błąd pobranie id wpisow na tagu!")
        return -1

    return tablica_id_wpisow

 
def pobranie_listy_analizowanych_tagow_i_uzytkownikow():
    
    try:
        return [nielubiany_uz.rstrip('\n') for nielubiany_uz in  open('nielubiani_uzytkownicy', 'r')], [nielubiany_tag.rstrip('\n') for nielubiany_tag in  open('nielubiane_tagi', 'r')], [lubiany_uz.rstrip('\n') for lubiany_uz in  open('lubiani_uzytkownicy', 'r')], [lubiany_tag.rstrip('\n') for lubiany_tag in  open('lubiane_tagi', 'r')]   
    except:
        print("\t\t[!] Błąd pobrania listy analizowanych użytkowników i tagów z plików!")
        return -1

def pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron):
    lista_id_postow_uzytkownika = []
    lista_komentujacych_uzytkownika = []

    try:
        lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
        for id_wpisu in lista_id_postow_uzytkownika:
            lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
    except:
        print("\t\t[!] Błąd pobrania komentujących wpisy użytkownika!")
        return -1

    return lista_komentujacych_uzytkownika


def pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron):
    lista_id_postow_uzytkownika = []
    lista_plusujacych_uzytkownika = []
    
    try:
        lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
        for id_wpisu in lista_id_postow_uzytkownika:
            lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)
    except:
        print("\t\t[!] Błąd pobrania plusujących wpisy użytkownika!")
        return -1
    
    return lista_plusujacych_uzytkownika


def pobranie_aktywnych_lubiany_uz(nazwa_uzytkownika, liczba_stron):
    lista_wszystkich_plusujacych = []
    lista_wszystkich_komentujacych = []

    print("Pobieranie informacji o lubianym użytkowniku " + nazwa_uzytkownika + "...\t\t", end=' ')
    try:
        lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)
        lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)   
        wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
        wszyscy_aktywni.remove(nazwa_uzytkownika)
    except:
        print("\t\t[!] Błąd pobrania aktywnych pod wpisami użytkownika (plusujących i komentujących)!")
        return -1

    print("[+] ZAKOŃCZONO")
    return wszyscy_aktywni

def wyswietl_informacje_o_pobranych_danych(tablica_lubianych_uzytkownikow, tablica_lubianych_tagow, tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow):
   
    if len(tablica_lubianych_uzytkownikow):
        print("\nWybrano " + str(len(tablica_lubianych_uzytkownikow)) + " lubianych użytkowników:")
        for uzytkownik in tablica_lubianych_uzytkownikow:
            print("\t" + uzytkownik)
    else:
        print("\nNie wybrano lubianych użytkowników")

    if len(tablica_lubianych_tagow):
        print("Wybrano " + str(len(tablica_lubianych_tagow)) + " lubianych tagów:")
        for tag in tablica_lubianych_tagow:
            print("\t" + tag)
    else:
        print("\nNie wybrano lubianych tagów")

    if len(tablica_nielubianych_uzytkownikow):
        print("Wybrano " + str(len(tablica_nielubianych_uzytkownikow)) + " nielubianych użytkowników:")
        for uzytkownik in tablica_lubianych_uzytkownikow:
            print("\t" + uzytkownik)
    else:
        print("\nNie wybrano nielubianych użytkowników")

    if len(tablica_nielubianych_tagow):
        print("Wybrano " + str(len(tablica_nielubianych_tagow)) + " nielubianych tagów:")
        for uzytkownik in tablica_lubianych_uzytkownikow:
            print("\t" + uzytkownik)
    else:
        print("\nNie wybrano nielubianych tagów\n")


#===== MAIN =====
liczba_stron = 2
tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow = pobranie_listy_analizowanych_tagow_i_uzytkownikow()

wyswietl_informacje_o_pobranych_danych(tablica_lubianych_uzytkownikow, tablica_lubianych_tagow, tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow)

#pobranie_id_wpisow_uzytkownika("MikolajSobczak1985", 1)
pobranie_id_wpisow_uzytkownika("MikolajSobczak1985", "2020-03-01", "2020-03-02")

# === TO DZIAŁA - TEST ====

#zbior_wspolny = []
#
#for uzytkownik in tablica_lubianych_uzytkownikow:
#    temp_tablica = pobranie_aktywnych_lubiany_uz(uzytkownik, liczba_stron)
#    if zbior_wspolny:
#        zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
#    else:
#        zbior_wspolny = temp_tablica
#
#print("\nLista użytkowników udzielająca się pod wszystkimi wskazanymi tagami/wpisami użytkowników:")
#
#index = 1
#for uzytkownik in zbior_wspolny:
#    print("\t" + str(index) + ") " + uzytkownik)
#    index += 1
