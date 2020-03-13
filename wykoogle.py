#!/bin/python3

import re
import requests
from lxml import html
from bs4 import BeautifulSoup as bs
import datetime
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
    komentujacy = []
    try:
        soup = bs(surowe_dane_string.text, "lxml")
        lista_komentujacych = soup.find_all('div', {'class': 'wblock lcontrast dC'}, {'data-type':'entrycomment'})
        lista_komentujacych += soup.find_all('div', {'class': 'wblock lcontrast dC deleted'}, {'data-type':'entrycomment'})
        for komentujacy_uzytkownik in lista_komentujacych:
            komentujacy.append(komentujacy_uzytkownik.find('a', {'class':'profile'}).attrs.get('href').split('/')[4]) 
        komentujacy = list(dict.fromkeys(komentujacy))
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

    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron_do_analizy = 1
        else:
            liczba_stron_do_analizy = int(argumenty[1])
        
        try:
            for strona in range(numer_strony, liczba_stron_do_analizy + 1):
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(strona))  
                soup = bs(surowe_dane_strony.text, "lxml")
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                for wpis in lista_wpisow:
                    tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
        except:
            print("\t\t[!] Błąd pobrania id wpisów użytkownika!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = date.fromisoformat(argumenty[1])
        data_koncowa = date.fromisoformat(argumenty[2])
        flaga_data_w_zakresie = 0
        flaga_data_poza_zakresem = 0        
        try:
            while not flaga_data_poza_zakresem:
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony))  
                numer_strony += 1
                soup = bs(surowe_dane_strony.text, "lxml")
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                if not len(lista_wpisow):
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1 
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))   
                    
        except:
            print("\t\t[!] Błąd pobrania id wpisów użytkownika!")
            return -1

    if len(argumenty) > 3:
        print("Niewłaściwa liczba argumentów funkcji 'pobranie_id_wpisow_uzytkownika'")
        return -1

 
def pobranie_id_wpisow_na_tagu(*argumenty):
    tablica_id_wpisow = []
    nazwa_tagu = argumenty[0]
    flaga_data_w_zakresie = 0
    flaga_data_poza_zakresem = 0

    if len(argumenty) == 1 or len(argumenty) == 3:
        try:
            if len(argumenty) == 1:
                data_koncowa = datetime.date.today()
                data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
            else:
                data_poczatkowa = date.fromisoformat(argumenty[1])
                data_koncowa = date.fromisoformat(argumenty[2])
 
            surowe_dane_strony = requests.get("https://www.wykop.pl/tag/wpisy/" + nazwa_tagu)
            while not flaga_data_poza_zakresem:    
                soup = bs(surowe_dane_strony.text, "lxml")
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                if not len(lista_wpisow):
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1  
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
                
                ostatni_wpis_na_pobranej_stronie_tagu = tablica_id_wpisow[-1] 
                surowe_dane_strony = requests.get("https://www.wykop.pl/tag/wpisy/"  + nazwa_tagu + "/next/entry-" + ostatni_wpis_na_pobranej_stronie_tagu + "/")            
        except:
            print("\t\t[!] Błąd pobrania id wpisów pod tagiem!")
            return -1
    
    else:
        print("Niewłaściwa liczba argumentów funkcji 'pobranie_id_wpisow_na_tagu'")
        return -1

 
def pobranie_listy_analizowanych_tagow_i_uzytkownikow():
    nielubiani_uz_lista = []
    nielubiane_tagi_lista = []
    lubiani_uz_lista = []
    lubiane_tagi_lista = []

    try:
        for nielubiany_uz in open('nielubiani_uzytkownicy', 'r'):
            nielubiani_uz_lista.append(nielubiany_uz.strip())
        for nielubiany_tag in open('nielubiane_tagi', 'r'):
            nielubiane_tagi_lista.append(nielubiany_tag.strip())
        for lubiany_uz in open('lubiani_uzytkownicy', 'r'):
            lubiani_uz_lista.append(lubiany_uz.strip())
        for lubiany_tag in open('lubiane_tagi', 'r'):
            lubiane_tagi_lista.append(lubiany_tag.strip())
    except:
        print("\t\t[!] Błąd pobrania listy analizowanych użytkowników i tagów z plików!")
        return -1

    return nielubiani_uz_lista, nielubiane_tagi_lista, lubiani_uz_lista, lubiane_tagi_lista   


def pobranie_komentujacych_uzytkownika(*argumenty):
    lista_id_postow_uzytkownika = []
    lista_komentujacych_uzytkownika = []
    nazwa_uzytkownika = argumenty[0]
    
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])   
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania komentujących wpisy użytkownika!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania komentujących wpisy użytkownika!")
            return -1
    
    return lista_komentujacych_uzytkownika


def pobranie_plusujacych_uzytkownika(*argumenty):
    lista_id_postow_uzytkownika = []
    lista_plusujacych_uzytkownika = []
    nazwa_uzytkownika = argumenty[0]
   
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_plusujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania komentujących wpisy użytkownika!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_plusujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania komentujących wpisy użytkownika!")
            return -1
    return lista_plusujacych_uzytkownika


def pobranie_komentujacych_tag(*argumenty):
    lista_komentujacych_tag = []
    lista_id_postow_tagu = []
    nazwa_tagu = argumenty[0]
    
    if len(argumenty) == 1 or len(argumenty) == 3 :
        if len(argumenty) == 1:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
        else:
            data_poczatkowa = date.fromisoformat(argumenty[1])
            data_koncowa = date.fromisoformat(argumenty[2])
        try:
            lista_id_postow_tagu = pobranie_id_wpisow_na_tagu(nazwa_tagu, str(data_poczatkowa), str(data_koncowa))
            for id_wpisu in lista_id_postow_tagu:
                lista_komentujacych_tag += pobranie_komentujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania komentujących wpisy pod tagiem!")
            return -1
    else:
        print("\t\t[!] Błąd pobrania komentujących wpisy pod tagiem!")
        return -1
        
    return lista_komentujacych_tag


def pobranie_plusujacych_tag(*argumenty):
    lista_plusujacych_tag = []
    lista_id_postow_tagu = []
    nazwa_tagu = argumenty[0]
    if len(argumenty) == 1 or len(argumenty) == 3 :
        if len(argumenty) == 1:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
        else:
            data_poczatkowa = date.fromisoformat(argumenty[1])
            data_koncowa = date.fromisoformat(argumenty[2])
        try:
            lista_id_postow_tagu = pobranie_id_wpisow_na_tagu(nazwa_tagu, str(data_poczatkowa), str(data_koncowa))
            for id_wpisu in lista_id_postow_tagu:
                lista_plusujacych_tag += pobranie_plusujacych_wpis(id_wpisu)
        except:
            print("\t\t[!] Błąd pobrania plusujących wpisy pod tagiem!")
            return -1
    else:
        print("\t\t[!] Błąd pobrania plusujących wpisy pod tagiem!")
        return -1
    
    return lista_plusujacych_tag


def pobranie_aktywnych_lubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    lista_wszystkich_komentujacych = []
    nazwa_uzytkownika = argumenty[0]

    print("\nPobieranie informacji o lubianym użytkowniku " + nazwa_uzytkownika + "...\t\t", end=' ')
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)
            lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami lubianego użytkownika (plusujących i komentujących)!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:    
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami lubianego użytkownika (plusujących i komentujących)!")
            return -1

    print("[+] ZAKOŃCZONO")
    return wszyscy_aktywni


def pobranie_aktywnych_nielubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    nazwa_uzytkownika = argumenty[0]

    print("\nPobieranie informacji o nielubianym użytkowniku " + nazwa_uzytkownika + "...\t\t", end=' ')
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami nielubianego użytkownika (komentujących)!")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:    
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami nielubianego użytkownika (komentujących)!")
            return -1

    print("[+] ZAKOŃCZONO")
    return wszyscy_aktywni

   
def zbior_wspolny_lubianych_uz(tablica_lubianych_uzytkownikow):
    flaga_zbior_wspolny_pusty_na_poczatku = 1
    zbior_wspolny = []
    temp_tablica = []

    for uzytkownik in tablica_lubianych_uzytkownikow:
        if len(uzytkownik.split()) == 1:
            temp_tablica = pobranie_aktywnych_lubiany_uz(uzytkownik.split()[0])
        if len(uzytkownik.split()) == 2:
            temp_tablica = pobranie_aktywnych_lubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1])
        if len(uzytkownik.split()) == 3:
            temp_tablica = pobranie_aktywnych_lubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1], uzytkownik.split()[2])
        if zbior_wspolny:
            zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
        if not zbior_wspolny and flaga_zbior_wspolny_pusty_na_poczatku:
            zbior_wspolny = temp_tablica
            flaga_zbior_wspolny_pusty_na_poczatku = 0
        if not zbior_wspolny and not flaga_zbior_wspolny_pusty_na_poczatku:
            print("\n\tBrak użytkownika, udzielającego się pod wpisami wybranych LUBIANYCH użytkowników w określonych okresach")
            return -1
    
    return zbior_wspolny    


def zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, zbior_wspolny):
    temp_tablica = []

    for uzytkownik in tablica_nielubianych_uzytkownikow:
        if len(uzytkownik.split()) == 1:
            temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0])
        if len(uzytkownik.split()) == 2:
            temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1])
        if len(uzytkownik.split()) == 3:
            temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1], uzytkownik.split()[2])
        if zbior_wspolny:
            zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
        if not zbior_wspolny :
            print("\n\tBrak użytkownika, udzielającego się pod wpisami wybranych NIELUBIANYCH użytkowników w określonych okresach")
            return -1
    
    return zbior_wspolny    

#TODO -=====================================================================================================================================================================================================

def pobranie_aktywnych_lubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    lista_wszystkich_plusujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    
    print("\nPobieranie informacji o lubianym tagu " + nazwa_tagu + "...\t\t", end='')
    if len(argumenty) == 1 or len(argumenty) == 3:
        if len(argumenty) == 3:
            data_poczatkowa = argumenty[1]
            data_koncowa = argumenty[2]
        else:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
        try: 
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)
            lista_wszystkich_plusujacych = pobranie_plusujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami pod lubianym tagiem (plusujących i komentujących)!")
            return -1
    else:
        print("\t\t[!] Błąd pobrania aktywnych pod wpisami pod lubianym tagiem (plusujących i komentujących) - zła liczba argumentów!")
        return -1

    print("[+] ZAKOŃCZONO")
    return wszyscy_aktywni


def pobranie_aktywnych_nielubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    
    print("\nPobieranie informacji o nielubianym tagu " + nazwa_tagu + "...\t\t", end='')
    if len(argumenty) == 1 or len(argumenty) == 3:
        if len(argumenty) == 3:
            data_poczatkowa = argumenty[1]
            data_koncowa = argumenty[2]
        else:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
        try:    
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
        except:
            print("\t\t[!] Błąd pobrania aktywnych pod wpisami pod nielubianym tagiem (komentujących)!")
            return -1
    else:
        print("\t\t[!] Błąd pobrania aktywnych pod wpisami pod nielubianym tagiem (komentujących)! - zła liczba argumentów")
        return -1

    print("[+] ZAKOŃCZONO")
    return wszyscy_aktywni


def zbior_wspolny_lubianych_tagow(tablica_lubianych_tagow, zbior_wspolny):
    pass

def zbior_wspolny_nielubianych_tagow(tablica_nielubianych_tagow, zbior_wspolny):
    pass


#TODO ======================================================================================================================================================================================================


def wyswietl_informacje_o_pobranych_danych(tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow):
 
    if len(tablica_lubianych_uzytkownikow):
        print("\nWybrano " + str(len(tablica_lubianych_uzytkownikow)) + " lubianych użytkowników:")
        for uzytkownik in tablica_lubianych_uzytkownikow:
            if len(uzytkownik.split()) == 1:
                print("\t" + uzytkownik.split()[0] + "\tNie wybrano zakresu dat lub liczby stron do analizy. Domyślnie sprawdzane są wpisy z ostatniej strony")
            if len(uzytkownik.split()) == 2:
                print("\t" + uzytkownik.split()[0] + "\tSprawdzane posty z " + uzytkownik.split()[1] + " ostatnich stron wpisów użytkownika")
            if len(uzytkownik.split()) == 3:
                print("\t" + uzytkownik.split()[0] + "\tSprawdzane posty od " + uzytkownik.split()[1] + " do " + uzytkownik.split()[2]) 
    else:
        print("\nNie wybrano lubianych użytkowników")

    if len(tablica_lubianych_tagow):
        print("\nWybrano " + str(len(tablica_lubianych_tagow)) + " lubianych tagów:")
        for tag in tablica_lubianych_tagow:
            if len(tag.split()) == 1:
                print("\t" + tag.split()[0] + "\tNie wybrano zakresu dat do analizy. Domyślnie sprawdzane są wpisy z ostatniego tygodnia")
            if len(tag.split()) == 2:
                print("\t" + tag.split()[0] + "\tZakres dat źle określony. Zostanie zbadany domyślny okres ostatniego tygodnia")
            if len(tag.split()) == 3:
                print("\t" + tag.split()[0] + "\tSprawdzane posty od " + tag.split()[1] + " do " + tag.split()[2]) 
    else:
        print("\nNie wybrano lubianych tagów")

    if len(tablica_nielubianych_uzytkownikow):
        print("\nWybrano " + str(len(tablica_nielubianych_uzytkownikow)) + " nielubianych użytkowników:")
        for uzytkownik in tablica_nielubianych_uzytkownikow:
            if len(uzytkownik.split()) == 1:
                print("\t" + uzytkownik.split()[0] + "\tNie wybrano zakresu dat lub liczby stron do analizy. Domyślnie sprawdzane są wpisy z ostatniej strony")
            if len(uzytkownik.split()) == 2:
                print("\t" + uzytkownik.split()[0] + "\tSprawdzane posty z " + uzytkownik.split()[1] + " ostatnich stron wpisów użytkownika")
            if len(uzytkownik.split()) == 3:
                print("\t" + uzytkownik.split()[0] + "\tSprawdzane posty od " + uzytkownik.split()[1] + " do " + uzytkownik.split()[2]) 
    else:
        print("\nNie wybrano nielubianych użytkowników")

    if len(tablica_nielubianych_tagow):
        print("\nWybrano " + str(len(tablica_nielubianych_tagow)) + " nielubianych tagów:")
        for tag in tablica_nielubianych_tagow:
            if len(tag.split()) == 1:
                print("\t" + tag.split()[0] + "\tNie wybrano zakresu dat do analizy. Domyślnie sprawdzane są wpisy z ostatniego tygodnia")
            if len(tag.split()) == 2:
                print("\t" + tag.split()[0] + "\tZakres dat źle określony. Zostanie zbadany domyślny okres ostatniego tygodnia")
            if len(tag.split()) == 3:
                print("\t" + tag.split()[0] + "\tSprawdzane posty od " + tag.split()[1] + " do " + tag.split()[2]) 
    else:
        print("\nNie wybrano nielubianych tagów\n")


#===== MAIN =====

# Pobierz informacje z plików
tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow = pobranie_listy_analizowanych_tagow_i_uzytkownikow()

# Wyświetl pobrane informacje oraz wskaż błędy
wyswietl_informacje_o_pobranych_danych(tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow)

# Wybierz zbiór wspólny dla lubianych użytkowników
#zbior_wspolny = zbior_wspolny_lubianych_uz(tablica_lubianych_uzytkownikow)

# Zmodyfikuj zbiór wspólny uwzględniając nielubianych użytkowników
#zbior_wspolny = zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, zbior_wspolny)

##
#print(pobranie_id_wpisow_na_tagu("kolanowirus"))
#print(pobranie_id_wpisow_na_tagu("kolanowirus", "2020-02-01", "2020-03-13"))
#print(pobranie_komentujacych_tag("kolanowirus"))
#print(pobranie_komentujacych_tag("kolanowirus", "2020-03-06", "2020-03-13"))
#print(pobranie_plusujacych_tag("kolanowirus"))
#print(pobranie_plusujacych_tag("kolanowirus", "2020-03-06", "2020-03-13"))
print(pobranie_aktywnych_lubiany_tag("kolanowirus", "2020-03-06", "2020-03-13"))
print(pobranie_aktywnych_nielubiany_tag("kolanowirus", "2020-03-06", "2020-03-13"))
##

# Zmodyfikuj zbiór wspólny uwzględniając lubiane tagi
# TODO

# Zmodyfikuj zbiór wspólny uwzględniając nielubianye tagów
# TODO

# Wyświetl informacje o otrzymanym zbiorze wspólnym
# TODO

