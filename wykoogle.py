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
        print("[+] Pobranie surowych danych o plusujących wpis " + str(id_wpisu) + " zakończone!")
        return surowe_dane_string.text
    except:
        print("[!] Błąd pobierania surowych danych o plusujących wpis " + str(id_wpisu) + "! [funkcja 'plusujacy_wpis_surowe_dane']")
        return -1


def ekstrakcja_plusujacych_wpis(surowe_dane_string):
    try:
        tablica_plusujacych = []
        tablica_plusujacych = re.findall('ludzie\\\/(.*?)\\\/ class', surowe_dane_string)
        print("[+] Utworzenie listy plusujących wpis zakończone!")
        return tablica_plusujacych
    except:
        print("[!] Błąd utworzenia listy plusujących wpis! [funkcja 'ekstrakcja_plusujacych_wpis']")
        return -1        
    

def pobranie_plusujacych_wpis(id_wpisu):
    try:
        plusujacy_wpis = []
        surowe_dane = plusujacy_wpis_surowe_dane(id_wpisu)
        plusujacy_wpis = ekstrakcja_plusujacych_wpis(id_wpisu)
        print("[+] Pobranie plusujących wpis " + str(id_wpisu)+ " zakończone!")
        return plusujacy_wpis
    except:
        print("[!] Błąd pobierania plusujących wpis " + str(id_wpisu) +"! [funkcja 'pobranie_plusujacych_wpis']")   
        return -1

def komentujacy_wpis_surowe_dane(id_wpisu):
    try:
        url_wpisu = "https://www.wykop.pl/wpis/" + str(id_wpisu)
        surowe_dane_string = requests.get(url_wpisu)
        print("[+] Pobieranie surowych danych o komentujących wpis " + str(id_wpisu) + " zakończone!")
        return surowe_dane_string
    except:
        print("[!] Błąd pobierania surowych danych o komentujących wpis " + str(id_wpisu) + "! [funkcja 'komentujacy_wpis_surowe_dane]")
        return -1


def ekstrakcja_komentujacych_wpis(surowe_dane_string):
    komentujacy = []
    try:
        soup = bs(surowe_dane_string.text, "lxml")
        lista_komentujacych = soup.find_all('div', {'class': 'wblock lcontrast dC'}, {'data-type':'entrycomment'})
        lista_komentujacych += soup.find_all('div', {'class': 'wblock lcontrast dC deleted'}, {'data-type':'entrycomment'})
        for komentujacy_uzytkownik in lista_komentujacych:
            komentujacy.append(komentujacy_uzytkownik.find('a', {'class':'profile'}).attrs.get('href').split('/')[4]) 
        komentujacy = list(dict.fromkeys(komentujacy))
        print("[+] Utworzenie listy komentujących wpis zakończone!")
        return komentujacy
    except:
        print("[!] Błąd utworzenia listy komentujących wpis! [funkcja 'ekstrakcja_komentujacych_wpis']")
        return -1    


def pobranie_komentujacych_wpis(id_wpisu):
    try:
        komentujacy_wpis = []
        surowe_dane = komentujacy_wpis_surowe_dane(id_wpisu)
        komentujacy_wpis = ekstrakcja_komentujacych_wpis(surowe_dane)
        print("[+] Pobieranie komentujących wpis " + str(id_wpisu) + " zakończone!")
        return komentujacy_wpis
    except:
        print("[!] Błąd pobierania komentujących wpis " + str(id_wpisu) + "! [funkcja 'pobranie_komentujacych_wpis']")
        return -1

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
            print("[+] Pobranie id wpisów użytkownika zakończone")
            return tablica_id_wpisow
        except:
            print("[!] Błąd pobrania id wpisów użytkownika! [funkcja 'pobranie_id_wpisow_uzytkownika']")
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
                    print("[+] Pobranie id wpisów użytkownika " + argumenty[0] + " zakończone")
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1
                        print("[+] Pobranie id wpisów użytkownika " + argumenty[0] + " zakończone")
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))   
                    
        except:
            print("[!] Błąd pobrania id wpisów użytkownika " +argumenty[0] + "! [funkcja 'pobranie_id_wpisow_uzytkownika']")
            return -1

    if len(argumenty) > 3:
        print("[!] Niewłaściwa liczba argumentów [funkcja 'pobranie_id_wpisow_uzytkownika']")
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
                    print("[+] Pobranie id wpisów pod tagiem " + argumenty[0] + " zakończone")
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1 
                        print("[+] Pobranie id wpisów pod tagiem " + argumenty[0] + " zakończone")
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
                ostatni_wpis_na_pobranej_stronie_tagu = tablica_id_wpisow[-1] 
                surowe_dane_strony = requests.get("https://www.wykop.pl/tag/wpisy/"  + nazwa_tagu + "/next/entry-" + ostatni_wpis_na_pobranej_stronie_tagu + "/")            
        except:
            print("[!] Błąd pobrania id wpisów pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_id_wpisow_na_tagu']")
            return -1
    
    else:
        print("[!] Niewłaściwa liczba argumentów [funkcja 'pobranie_id_wpisow_na_tagu']")
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
        print("[+] Pobranie listy użytkowników i tagów zakończone!")
        return nielubiani_uz_lista, nielubiane_tagi_lista, lubiani_uz_lista, lubiane_tagi_lista   
    except:
        print("[!] Błąd pobrania listy użytkowników i tagów z plików! [funkcja 'pobranie_listy_analizowanych_tagow_i_uzytkownikow']")
        return -1


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
            print("[+] Pobranie komentujących wszystkie wpisy użytkownika " + argumenty[0] + " zakończone!")
            return lista_komentujacych_uzytkownika
        except:
            print("[!] Błąd pobrania komentujących wszystkie wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_uzytkownika']")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
            print("[+] Pobranie komentujących wszystkie wpisy użytkownika " + argumenty[0] + " zakończone!")
            return lista_komentujacych_uzytkownika
        except:
            print("[!] Błąd pobrania komentujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_uzytkownika']")
            return -1


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
                lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)
            print("[+] Pobranie plusujących wpisy użytkownika " + argumenty[0] + " zakończone!")
            return lista_plusujacych_uzytkownika
        except:
            print("[!] Błąd pobrania plusujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_uzytkownika']")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:
            lista_id_postow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)
            print("[+] Pobranie plusujących wpisy użytkownika " + argumenty[0] + " zakończone!")
            return lista_plusujacych_uzytkownika
        except:
            print("[!] Błąd pobrania plusujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_uzytkownika']")
            return -1


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
            print("[+] Pobranie komentujących wpisy pod tagiem " + argumenty[0] + " zakończone!")
            return lista_komentujacych_tag
        except:
            print("[!] Błąd pobrania komentujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_tag']")
            return -1
    else:
        print("Nieprawidłowa liczba argumentów! [funkcja 'pobranie_komentujacych_tag']")
        return -1 


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
            print("[+] Pobranie plusujących wpisy pod tagiem " + argumenty[0] + " zakończone!")
            return lista_plusujacych_tag
        except:
            print("[!] Błąd pobrania plusujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_tag']")
            return -1
    else:
        print("[!] Błąd pobrania plusujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_tag']")
        return -1


def pobranie_aktywnych_lubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    lista_wszystkich_komentujacych = []
    nazwa_uzytkownika = argumenty[0]

    print("Pobieranie informacji o LUBIANYM użytkowniku " + nazwa_uzytkownika + "...")
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
            print("[+] Pobranie aktywnych (plusujących i komentujących) pod wpisami użytkownika " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami lubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_uz']")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:    
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print("[+] Pobranie aktywnych (plusujących i komentujących) pod wpisami użytkownika " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami lubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_uz']")
            return -1


def pobranie_aktywnych_nielubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    nazwa_uzytkownika = argumenty[0]

    print("Pobieranie informacji o NIELUBIANYM użytkowniku " + nazwa_uzytkownika + "...")
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print("[+] Pobranie aktywnych (komentujących) pod wpisami użytkownika " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (komentujących) pod wpisami nielubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_uz']")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:    
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print("[+] Pobranie aktywnych (komentujących) pod wpisami użytkownika " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (komentujących) pod wpisami nielubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_uz']")
            return -1

   
def zbior_wspolny_lubianych_uz(tablica_lubianych_uzytkownikow):
    flaga_zbior_wspolny_pusty_na_poczatku = 1
    zbior_wspolny = []
    temp_tablica = []

    try:
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
                 print("[!] Brak użytkownika, udzielającego się pod wpisami wybranych LUBIANYCH użytkowników w określonych okresach")
                 return []
    except:
        print("[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami LUBIANYCH użytkowników! funkcja ['zbior_wspolny_lubianych_uz']")
        return -1
    
    print("[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami LUBIANYCH użytkowników!")
    return zbior_wspolny    


def zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, zbior_wspolny):
    temp_tablica = []

    try:
        for uzytkownik in tablica_nielubianych_uzytkownikow:
            if len(uzytkownik.split()) == 1:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0])
            if len(uzytkownik.split()) == 2:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1])
            if len(uzytkownik.split()) == 3:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1], uzytkownik.split()[2])
            if zbior_wspolny:
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if not zbior_wspolny:
                print("[!] Brak użytkownika, udzielającego się pod wpisami wybranych NIELUBIANYCH użytkowników w określonych okresach")
                return []
    except:
        print("[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami NIELUBIANYCH użytkowników! funkcja ['zbior_wspolny_nielubianych_uz']")
        return -1
         
    print("[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami NIELUBIANYCH użytkowników!")
    return zbior_wspolny    


def pobranie_aktywnych_lubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    lista_wszystkich_plusujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    
    print("Pobieranie informacji o LUBIANYM tagu " + nazwa_tagu + "...")
    if len(argumenty) == 1 or len(argumenty) == 3:
        try:       
            if len(argumenty) == 3:
                data_poczatkowa = argumenty[1]
                data_koncowa = argumenty[2]
            else:
                data_koncowa = str(datetime.date.today())
                data_poczatkowa = str(datetime.date.today() - datetime.timedelta(weeks=1))
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)    
            lista_wszystkich_plusujacych = pobranie_plusujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            print("[+] Pobranie aktywnych (plusujących i komentujących) pod wpisami pod LUBIANYM tagiem " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami pod LUBIANYM tagiem " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_tag']")
            return -1
    else:
        print("[!] Nieprawidłowa liczba argumentów! [funkcja 'pobranie_aktywnych_lubianych_tag']")
        return -1


def pobranie_aktywnych_nielubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    
    print("\nPobieranie informacji o NIELUBIANYM tagu " + nazwa_tagu + "...\t\t", end='')
    if len(argumenty) == 1 or len(argumenty) == 3:
        try:        
            if len(argumenty) == 3:
                data_poczatkowa = argumenty[1]
                data_koncowa = argumenty[2]
            else:
                data_koncowa = str(datetime.date.today())
                data_poczatkowa = str(datetime.date.today() - datetime.timedelta(weeks=1))
            
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            print("[+] Pobranie aktywnych (komentujących) pod wpisami pod NIELUBIANYM tagiem " + argumenty[0] + " zakończone!")
            return wszyscy_aktywni
        except:
            print("[!] Błąd pobrania aktywnych (komentujących) pod wpisami pod NIELUBIANYM tagiem " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_tag']")
            return -1
    else:
        print("[!] Nieprawidłowa liczba argumentów! [funkcja 'pobranie_aktywnych_nielubianych_tag']")
        return -1


def zbior_wspolny_lubianych_tagow(tablica_lubianych_tagow, zbior_wspolny):
    temp_tablica = []

    try:
        for tag in tablica_lubianych_tagow:
            if len(tag.split()) == 1:
                temp_tablica = pobranie_aktywnych_lubiany_tag(tag.split()[0])
            if len(tag.split()) == 3:
                temp_tablica = pobranie_aktywnych_lubiany_tag(tag.split()[0], tag.split()[1], tag.split()[2])
            if zbior_wspolny:
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if not zbior_wspolny :
                print("[!] Brak użytkownika, udzielającego się pod wpisami wybranych LUBIANYCH tagów w określonych okresach")
                return []
    except:
        print("[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami pod LUBIANYMI tagami! funkcja ['zbior_wspolny_lubianych_tagow']")
        return -1

    print("[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami pod LUBIANYMI tagami!")
    return zbior_wspolny


def zbior_wspolny_nielubianych_tagow(tablica_nielubianych_tagow, zbior_wspolny):
    temp_tablica = []

    try:
        for tag in tablica_nielubianych_tagow:
            if len(tag.split()) == 1:
                temp_tablica = pobranie_aktywnych_nielubiany_tag(tag.split()[0])
            if len(tag.split()) == 3:
                temp_tablica = pobranie_aktywnych_nielubiany_tag(tag.split()[0], tag.split()[1], tag.split()[2])
            if zbior_wspolny:
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if not zbior_wspolny :
                print("[!] Brak użytkownika, udzielającego się pod wpisami wybranych NIELUBIANYCH tagów w określonych okresach")
                return []
    except:
        print("[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami pod NIELUBIANYMI tagami! funkcja ['zbior_wspolny_nielubianych_tagow']")
        return -1

    print("[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami NIELUBIANYCH użytkowników!")
    return zbior_wspolny 


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

def wyswietl_informacje_koncowe(zbior_wspolny):
    
    if zbior_wspolny:
        print("Podczas analizy wybranych użytkowników i tagów wytypowano następujące osoby:")
        for uzytkownik, indeks in zbior_wspolny, range(len(zbior_wspolny)):
            print("\t\t" + str(indeks) + ") " + uzytkownik)
        return 0
    else:
        print("Podczas analizy nie udało się znaleźć osób pasujących do wybranych kryteriów. Spróbuj poszerzyć zakres dat lub zmienić analizowane tagi i użytkowników")
        return -1


#===== MAIN =====
zbior_wspolny = []
# Pobierz informacje z plików
tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow = pobranie_listy_analizowanych_tagow_i_uzytkownikow()

# Wyświetl pobrane informacje oraz wskaż błędy
wyswietl_informacje_o_pobranych_danych(tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow)

# Wybierz zbiór wspólny dla lubianych użytkowników
zbior_wspolny = zbior_wspolny_lubianych_uz(tablica_lubianych_uzytkownikow)
if not zbior_wspolny:
    print("Brak użytkowników odpowiadających kryteriom.")
    
# Zmodyfikuj zbiór wspólny uwzględniając nielubianych użytkowników
zbior_wspolny = zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, zbior_wspolny)
if not zbior_wspolny:
    print("Brak użytkowników odpowiadających kryteriom.")

# Zmodyfikuj zbiór wspólny uwzględniając lubiane tagi
zbior_wspolny = zbior_wspolny_lubianych_tagow(tablica_lubianych_tagow, zbior_wspolny)
if not zbior_wspolny:
    print("Brak użytkowników odpowiadających kryteriom.")

# Zmodyfikuj zbiór wspólny uwzględniając nielubianye tagów
zbior_wspolny = zbior_wspolny_nielubianych_tagow(tablica_nielubianych_tagow, zbior_wspolny)
if not zbior_wspolny:
    print("Brak użytkowników odpowiadających kryteriom.")

# Wyświetl informacje o otrzymanym zbiorze wspólnym
wyswietl_informacje_koncowe(zbior_wspolny)

