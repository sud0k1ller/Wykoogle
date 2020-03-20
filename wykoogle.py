#!/bin/python3

import re
import requests
from bs4 import BeautifulSoup as bs
import datetime
from datetime import date
from progress.bar import ShadyBar
from progress.spinner import PieSpinner

class colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    END = '\033[0m'
    BOLD = '\033[1m'


def plusujacy_wpis_surowe_dane(id_wpisu):
    try:
        surowe_dane_string  = requests.get("https://www.wykop.pl/ajax2/wpis/upvoters/" + str(id_wpisu)) 
        return surowe_dane_string.text
    except:
        print(colors.RED + "\t\t[!] Błąd pobierania surowych danych o plusujących wpis " + str(id_wpisu) + "! [funkcja 'plusujacy_wpis_surowe_dane']" + colors.END)
        return -1


def ekstrakcja_plusujacych_wpis(surowe_dane_string):
    try:
        tablica_plusujacych = []
        tablica_plusujacych = re.findall('ludzie\\\/(.*?)\\\/ class', surowe_dane_string)
        #print("\t\t[+] Utworzenie listy plusujących wpis zakończone!")
        return tablica_plusujacych
    except:
        print(colors.RED + "\t\t[!] Błąd utworzenia listy plusujących wpis! [funkcja 'ekstrakcja_plusujacych_wpis']" + colors.END)
        return -1        
    

def pobranie_plusujacych_wpis(id_wpisu):
    try:
        plusujacy_wpis = []
        surowe_dane = plusujacy_wpis_surowe_dane(id_wpisu)
        plusujacy_wpis = ekstrakcja_plusujacych_wpis(id_wpisu)
        #print("\t\t[+] Pobranie plusujących wpis " + str(id_wpisu)+ " zakończone!")
        return plusujacy_wpis
    except:
        print(colors.RED + "\t\t[!] Błąd pobierania plusujących wpis " + str(id_wpisu) +"! [funkcja 'pobranie_plusujacych_wpis']" + colors.RED)   
        return -1

def komentujacy_wpis_surowe_dane(id_wpisu):
    try:
        url_wpisu = "https://www.wykop.pl/wpis/" + str(id_wpisu)
        surowe_dane_string = requests.get(url_wpisu)
        #print("\t\t[+] Pobieranie surowych danych o komentujących wpis " + str(id_wpisu) + " zakończone!")
        return surowe_dane_string
    except:
        print(colors.RED + "\t\t[!] Błąd pobierania surowych danych o komentujących wpis " + str(id_wpisu) + "! [funkcja 'komentujacy_wpis_surowe_dane]" + colors.END)
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
        #print("\t\t[+] Utworzenie listy komentujących wpis zakończone!")
        return komentujacy
    except:
        print(colors.RED + "\t\t[!] Błąd utworzenia listy komentujących wpis! [funkcja 'ekstrakcja_komentujacych_wpis']" + colors.END)
        return -1    


def pobranie_komentujacych_wpis(id_wpisu):
    try:
        komentujacy_wpis = []
        surowe_dane = komentujacy_wpis_surowe_dane(id_wpisu)
        komentujacy_wpis = ekstrakcja_komentujacych_wpis(surowe_dane)
        #print("\t\t[+] Pobieranie komentujących wpis " + str(id_wpisu) + " zakończone!")
        return komentujacy_wpis
    except:
        print(colors.RED + "\t\t[!] Błąd pobierania komentujących wpis " + str(id_wpisu) + "! [funkcja 'pobranie_komentujacych_wpis']" + colors.END)
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
            spinner_postepu = PieSpinner(colors.GREEN + '\t[#] Pobieranie id wpisów użytkownika w wybranym zakresie ' + colors.END)
            for strona in range(numer_strony, liczba_stron_do_analizy + 1):
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(strona))  
                soup = bs(surowe_dane_strony.text, "lxml")
                if soup.find("div", {"class":"mark-bg space error-block"}):
                    print(colors.RED + "\n\t\t[!] Błąd 404 dla strony: " + "https://www.wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(strona) + "\n\t\t Sprawdź poprawność URL. Zła nazwa użytkownika?" + colors.END)
                    return -1

                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                for wpis in lista_wpisow:
                    tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))    
                spinner_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return tablica_id_wpisow
        except:
            print("\t[!] Błąd pobrania id wpisów użytkownika! [funkcja 'pobranie_id_wpisow_uzytkownika']")
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = date.fromisoformat(argumenty[1])
        data_koncowa = date.fromisoformat(argumenty[2])
        flaga_data_w_zakresie = 0
        flaga_data_poza_zakresem = 0        
        try:
            spinner_postepu = PieSpinner(colors.GREEN + '\t[#] Pobieranie id wpisów użytkownika w wybranym zakresie ' + colors.END)
            while not flaga_data_poza_zakresem:
                
                spinner_postepu.next()    
                surowe_dane_strony = requests.get("https://wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(numer_strony))  
                numer_strony += 1
                soup = bs(surowe_dane_strony.text, "lxml")
                if soup.find("div", {"class":"mark-bg space error-block"}):
                    print(colors.RED + "\n\t\t[!] Błąd 404 dla strony: " + "https://www.wykop.pl/ludzie/wpisy/" + nazwa_uzytkownika + "/strona/" + str(strona) + "\n\t\t Sprawdź poprawność URL. Zła nazwa użytkownika?" + colors.END)
                    return -1

                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                if not len(lista_wpisow):
                    print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    spinner_postepu.next()    
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1
                        print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO" + colors.END)
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
        except:
            print(colors.BOLD + colors.RED + "\t[!] Błąd pobrania id wpisów użytkownika " +argumenty[0] + "! [funkcja 'pobranie_id_wpisow_uzytkownika']" + colors.END)
            return -1

    if len(argumenty) > 3:
        print(colors.BOLD + colors.RED + "\t[!] Niewłaściwa liczba argumentów [funkcja 'pobranie_id_wpisow_uzytkownika']" + colors.END)
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
            
            surowe_dane_strony = requests.get("https://www.wykop.pl/tag/wpisy/" + nazwa_tagu + '/wszystkie')
            spinner_postepu = PieSpinner(colors.GREEN + '\t[#] Pobieranie id wpisów na tagu w wybranym zakresie ' + colors.END)
            while not flaga_data_poza_zakresem:    
                soup = bs(surowe_dane_strony.text, "lxml")
                if not soup.find("li", {"class":"entry iC"}):
                    print(colors.RED + "\n\t\t[!] Błąd 404 dla strony: " + "https://www.wykop.pl/tag/wpisy/" + nazwa_tagu + "/wszystkie" + "\n\t\t Sprawdź poprawność URL. Zła nazwa tagu?" + colors.END)
                    return -1
                lista_wpisow = soup.find_all('li', {'class': 'entry iC'})
                spinner_postepu.next()
                if not len(lista_wpisow):
                    print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO" + colors.END)
                    return tablica_id_wpisow
                for wpis in lista_wpisow:
                    spinner_postepu.next()
                    data_wpisu = date.fromisoformat(wpis.find('time').attrs.get('title').split()[0])
                    if not flaga_data_w_zakresie and (data_wpisu <= data_koncowa):
                        flaga_data_w_zakresie = 1
                    if flaga_data_w_zakresie and (data_wpisu < data_poczatkowa):
                        flaga_data_w_zakresie = 0
                        flaga_data_poza_zakresem = 1 
                        print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO" + colors.END)
                        return tablica_id_wpisow
                    if flaga_data_w_zakresie:
                        tablica_id_wpisow.append(wpis.find('div').attrs.get('data-id'))
                        ostatni_wpis_na_pobranej_stronie_tagu = wpis.find('div').attrs.get('data-id')
                surowe_dane_strony = requests.get("https://www.wykop.pl/tag/wpisy/"  + nazwa_tagu + "/next/entry-" + ostatni_wpis_na_pobranej_stronie_tagu + "/")            
        except:
            print(colors.RED + "\t[!] Błąd pobrania id wpisów pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_id_wpisow_na_tagu']" + colors.END)
            return -1
    else:
        print(colors.RED + "\t[!] Niewłaściwa liczba argumentów [funkcja 'pobranie_id_wpisow_na_tagu']" + colors.END)
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
        #print("[+] Pobranie listy użytkowników i tagów zakończone!")
        return nielubiani_uz_lista, nielubiane_tagi_lista, lubiani_uz_lista, lubiane_tagi_lista   
    except:
        print(colors.RED + "[!] Błąd pobrania listy użytkowników i tagów z plików! [funkcja 'pobranie_listy_analizowanych_tagow_i_uzytkownikow']" + colors.END)
        return -1


def pobranie_komentujacych_uzytkownika(*argumenty):
    lista_id_postow_uzytkownika = []
    lista_komentujacych_uzytkownika = []
    nazwa_uzytkownika = argumenty[0]
    lista_id_postow_uzytkownika = []
    
    if len(argumenty) == 3 or len(argumenty) == 2:
        if len(argumenty) == 2:
            liczba_stron = 1
            lista_id_postow_uzytkownika = argumenty[1]
        else:
            liczba_stron = int(argumenty[1])
            lista_id_postow_uzytkownika = argumenty[2]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich komentujących wpisy użytkownika\t' + colors.END, max=len(lista_id_postow_uzytkownika), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_komentujacych_uzytkownika
        except:
            print(colors.RED + "\t[!] Błąd pobrania komentujących wszystkie wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_uzytkownika']" + colors.END)
            return -1

    if len(argumenty) == 4:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        lista_id_postow_uzytkownika = argumenty[3]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich komentujących wpisy użytkownika\t' + colors.END, max=len(lista_id_postow_uzytkownika), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_komentujacych_uzytkownika += pobranie_komentujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_komentujacych_uzytkownika
        except:
            print(colors.RED + "\t[!] Błąd pobrania komentujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_uzytkownika']" + colors.END)
            return -1


def pobranie_plusujacych_uzytkownika(*argumenty):
    lista_id_postow_uzytkownika = []
    lista_plusujacych_uzytkownika = []
    nazwa_uzytkownika = argumenty[0]
    lista_id_postow_uzytkownika = []
    if len(argumenty) == 3 or len(argumenty) == 2:
        if len(argumenty) == 2:
            liczba_stron = 1
            lista_id_postow_uzytkownika = argumenty[1]
        else:
            liczba_stron = int(argumenty[1])
            lista_id_postow_uzytkownika = argumenty[2]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich plusujących wpisy użytkownika\t\t'+ colors.END, max=len(lista_id_postow_uzytkownika), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_plusujacych_uzytkownika
        except:
            print(colors.RED + "\t[!] Błąd pobrania plusujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_uzytkownika']" + colors.END)
            return -1

    if len(argumenty) == 4:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        lista_id_postow_uzytkownika = argumenty[3]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich plusujących wpisy użytkownika\t\t'+ colors.END, max=len(lista_id_postow_uzytkownika), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_uzytkownika:
                lista_plusujacych_uzytkownika += pobranie_plusujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_plusujacych_uzytkownika
        except:
            print(colors.RED + "\t[!] Błąd pobrania plusujących wpisy użytkownika " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_uzytkownika']" + colors.END)
            return -1


def pobranie_komentujacych_tag(*argumenty):
    lista_komentujacych_tag = []
    lista_id_postow_tagu = []
    nazwa_tagu = argumenty[0]
    lista_id_postow_na_tagu = []
    if len(argumenty) == 2 or len(argumenty) == 4 :
        if len(argumenty) == 2:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
            lista_id_postow_na_tagu = argumenty[2]
        else:
            data_poczatkowa = date.fromisoformat(argumenty[1])
            data_koncowa = date.fromisoformat(argumenty[2])
            lista_id_postow_na_tagu = argumenty[3]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich komentujących wpisy pod tagiem w wybranym zakresie\t' + colors.END, max=len(lista_id_postow_na_tagu), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_na_tagu:
                lista_komentujacych_tag += pobranie_komentujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_komentujacych_tag
        except:
            print(colors.RED + "\t[!] Błąd pobrania komentujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_komentujacych_tag']" + colors.END)
            return -1
    else:
        print(colors.RED + "\t[!] Nieprawidłowa liczba argumentów! [funkcja 'pobranie_komentujacych_tag']" + colors.END)
        return -1 


def pobranie_plusujacych_tag(*argumenty):
    lista_plusujacych_tag = []
    lista_id_postow_tagu = []
    nazwa_tagu = argumenty[0]
    lista_id_postow_na_tagu = []
    if len(argumenty) == 2 or len(argumenty) == 4 :
        if len(argumenty) == 2:
            data_koncowa = datetime.date.today()
            data_poczatkowa = datetime.date.today() - datetime.timedelta(weeks=1)
            lista_id_postow_na_tagu = argumenty[2]
        else:
            data_poczatkowa = date.fromisoformat(argumenty[1])
            data_koncowa = date.fromisoformat(argumenty[2])
            lista_id_postow_na_tagu = argumenty[3]
        try:
            pasek_postepu = ShadyBar(colors.GREEN + '\t[#] Pobieranie wszystkich plusujących wpisy pod tagiem w wybranym zakresie\t' + colors.END, max=len(lista_id_postow_na_tagu), suffix='%(percent)d%%')
            for id_wpisu in lista_id_postow_na_tagu:
                lista_plusujacych_tag += pobranie_plusujacych_wpis(id_wpisu)
                pasek_postepu.next()
            print(colors.GREEN + "\n\t\t[+] ZAKOŃCZONO!" + colors.END)
            return lista_plusujacych_tag
        except:
            print(colors.RED + "\t[!] Błąd pobrania plusujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_tag']" + colors.END)
            return -1
    else:
        print(colors.RED + "\t[!] Błąd pobrania plusujących wpisy pod tagiem " + argumenty[0] + "! [funkcja 'pobranie_plusujacych_tag']" + colors.END)
        return -1


def pobranie_aktywnych_lubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    lista_wszystkich_komentujacych = []
    lista_id_wpisow_uzytkownika = []
    nazwa_uzytkownika = argumenty[0]

    print(colors.BLUE + colors.BOLD + "\nPobieranie informacji o LUBIANYM użytkowniku " + nazwa_uzytkownika + "..." + colors.END)
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_id_wpisow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron, lista_id_wpisow_uzytkownika)
            lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, liczba_stron, lista_id_wpisow_uzytkownika)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o użytkowniku " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami lubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_uz']" + colors.END)
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:
            lista_id_wpisow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa, lista_id_wpisow_uzytkownika)
            lista_wszystkich_plusujacych = pobranie_plusujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa, lista_id_wpisow_uzytkownika)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o użytkowniku " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami lubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_uz']" + colors.END)
            return -1


def pobranie_aktywnych_nielubiany_uz(*argumenty):
    lista_wszystkich_plusujacych = []
    nazwa_uzytkownika = argumenty[0]
    lista_id_wpisow_uzytkownika = []

    print(colors.BLUE + colors.BOLD + "\nPobieranie informacji o NIELUBIANYM użytkowniku " + nazwa_uzytkownika + "..." + colors.END)
    if len(argumenty) == 2 or len(argumenty) == 1:
        if len(argumenty) == 1:
            liczba_stron = 1
        else:
            liczba_stron = int(argumenty[1])
        try:
            lista_id_wpisow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, liczba_stron)
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, liczba_stron, lista_id_wpisow_uzytkownika)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o użytkowniku " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (komentujących) pod wpisami nielubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_uz']" + colors.END)
            return -1

    if len(argumenty) == 3:
        data_poczatkowa = argumenty[1]
        data_koncowa = argumenty[2]
        try:    
            lista_id_wpisow_uzytkownika = pobranie_id_wpisow_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa)
            lista_wszystkich_komentujacych = pobranie_komentujacych_uzytkownika(nazwa_uzytkownika, data_poczatkowa, data_koncowa, lista_id_wpisow_uzytkownika)
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            wszyscy_aktywni.remove(nazwa_uzytkownika)
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o użytkowniku " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (komentujących) pod wpisami nielubianego użytkownika " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_uz']" + colors.END)
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
            
            if temp_tablica != -1 and zbior_wspolny: 
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if temp_tablica != -1 and not zbior_wspolny:
                zbior_wspolny = temp_tablica
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and not zbior_wspolny: 
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY UŻYTKOWNIKA" + colors.END)
                zbior_wspolny = []
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and zbior_wspolny:
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY UŻYTKOWNIKA" + colors.END)
    except:
        print(colors.RED + "\t[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami LUBIANYCH użytkowników! funkcja ['zbior_wspolny_lubianych_uz']" + colors.END)
        return -1
    
    if temp_tablica != -1 and not zbior_wspolny:
            return []
    if temp_tablica == -1 and not zbior_wspolny:
            return -1

    print(colors.GREEN + "\t[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami LUBIANYCH użytkowników!" + colors.END)
    return zbior_wspolny    


def zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, dotychczasowy_zbior_wspolny):
    temp_tablica = []
    zbior_wspolny = []
    flaga_zbior_wspolny_pusty_na_poczatku = 1    

    try:
        for uzytkownik in tablica_nielubianych_uzytkownikow:
            if len(uzytkownik.split()) == 1:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0])
            if len(uzytkownik.split()) == 2:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1])
            if len(uzytkownik.split()) == 3:
                temp_tablica = pobranie_aktywnych_nielubiany_uz(uzytkownik.split()[0], uzytkownik.split()[1], uzytkownik.split()[2])

            if temp_tablica != -1 and zbior_wspolny: 
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if temp_tablica != -1 and not zbior_wspolny:
                zbior_wspolny = temp_tablica
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and not zbior_wspolny: 
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY UŻYTKOWNIKA" + colors.END)
                zbior_wspolny = []
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and zbior_wspolny:
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY UŻYTKOWNIKA" + colors.END)
    except:
        print(colors.RED + "\t[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami NIELUBIANYCH użytkowników! funkcja ['zbior_wspolny_nielubianych_uz']" + colors.END)
        return -1
    
    if temp_tablica != -1 and not zbior_wspolny:
            return []
    if temp_tablica == -1 and not zbior_wspolny:
            return -1

    print(colors.GREEN + "\t[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami NIELUBIANYCH użytkowników!" + colors.END)
    return set(zbior_wspolny).intersection(dotychczasowy_zbior_wspolny)

def pobranie_aktywnych_lubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    lista_wszystkich_plusujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    lista_id_wpisow_na_tagu = []

    print(colors.BOLD + colors.BLUE + "\nPobieranie informacji o LUBIANYM tagu " + nazwa_tagu + "..." + colors.END)
    if len(argumenty) == 1 or len(argumenty) == 3:
        try:       
            if len(argumenty) == 3:
                data_poczatkowa = argumenty[1]
                data_koncowa = argumenty[2]
            else:
                data_koncowa = str(datetime.date.today())
                data_poczatkowa = str(datetime.date.today() - datetime.timedelta(weeks=1))

            lista_id_wpisow_na_tagu = pobranie_id_wpisow_na_tagu(nazwa_tagu, data_poczatkowa, data_koncowa)
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa, lista_id_wpisow_na_tagu)    
            lista_wszystkich_plusujacych = pobranie_plusujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa, lista_id_wpisow_na_tagu)   
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_plusujacych + lista_wszystkich_komentujacych))
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o tagu " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami pod LUBIANYM tagiem " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_lubiany_tag']" + colors.END)
            return -1
    else:
        print(colors.RED + "\t[!] Nieprawidłowa liczba argumentów! [funkcja 'pobranie_aktywnych_lubianych_tag']" + colors.END)
        return -1


def pobranie_aktywnych_nielubiany_tag(*argumenty):
    lista_wszystkich_komentujacych = []
    wszyscy_aktywni = []
    nazwa_tagu = argumenty[0]
    lista_id_wpisow_na_tagu = []

    print(colors.BOLD + colors.BLUE + "\nPobieranie informacji o NIELUBIANYM tagu " + nazwa_tagu + "..." + colors.END)
    if len(argumenty) == 1 or len(argumenty) == 3:
        try:       
            if len(argumenty) == 3:
                data_poczatkowa = argumenty[1]
                data_koncowa = argumenty[2]
            else:
                data_koncowa = str(datetime.date.today())
                data_poczatkowa = str(datetime.date.today() - datetime.timedelta(weeks=1))

            lista_id_wpisow_na_tagu = pobranie_id_wpisow_na_tagu(nazwa_tagu, data_poczatkowa, data_koncowa)    
            lista_wszystkich_komentujacych = pobranie_komentujacych_tag(nazwa_tagu, data_poczatkowa, data_koncowa, lista_id_wpisow_na_tagu)    
            wszyscy_aktywni = list(dict.fromkeys(lista_wszystkich_komentujacych))
            print(colors.GREEN + "\n\t[+] Zakończono pobieranie informacji o tagu " + argumenty[0] + "!" + colors.END)
            return wszyscy_aktywni
        except:
            print(colors.RED + "\t[!] Błąd pobrania aktywnych (plusujących i komentujących) pod wpisami pod NIELUBIANYM tagiem " + argumenty[0] + "! [funkcja 'pobranie_aktywnych_nielubiany_tag']" + colors.END)
            return -1
    else:
        print(colors.RED + "\t[!] Nieprawidłowa liczba argumentów! [funkcja 'pobranie_aktywnych_nielubianych_tag']" + colors.END)
        return -1

def zbior_wspolny_lubianych_tagow(tablica_lubianych_tagow, dotychczasowy_zbior_wspolny):
    temp_tablica = []
    zbior_wspolny = []
    flaga_zbior_wspolny_pusty_na_poczatku = 1

    try:
        for tag in tablica_lubianych_tagow:
            if len(tag.split()) == 1:
                temp_tablica = pobranie_aktywnych_lubiany_tag(tag.split()[0])
            if len(tag.split()) == 3:
                temp_tablica = pobranie_aktywnych_lubiany_tag(tag.split()[0], tag.split()[1], tag.split()[2])

            if temp_tablica != -1 and zbior_wspolny: 
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if temp_tablica != -1 and not zbior_wspolny:
                zbior_wspolny = temp_tablica
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and not zbior_wspolny: 
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY NA TAGU" + colors.END)
                zbior_wspolny = []
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and zbior_wspolny:
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY NA TAGU" + colors.END)
    except:
        print(colors.RED + "\t[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami LUBIANYCH użytkowników! funkcja ['zbior_wspolny_lubianych_tago']" + colors.END)
        return -1
    
    if temp_tablica != -1 and not zbior_wspolny:
            return []
    if temp_tablica == -1 and not zbior_wspolny:
            return -1

    print(colors.GREEN + "\t[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami LUBIANYCH tagów!" + colors.END)
    return set(zbior_wspolny).intersection(dotychczasowy_zbior_wspolny)


def zbior_wspolny_nielubianych_tagow(tablica_nielubianych_tagow, dotychczasowy_zbior_wspolny):
    temp_tablica = []
    zbior_wspolny = []
    flaga_zbior_wspolny_pusty_na_poczatku = 1

    try:
        for tag in tablica_nielubianych_tagow:
            if len(tag.split()) == 1:
                temp_tablica = pobranie_aktywnych_nielubiany_tag(tag.split()[0])
            if len(tag.split()) == 3:
                temp_tablica = pobranie_aktywnych_nielubiany_tag(tag.split()[0], tag.split()[1], tag.split()[2])

            if temp_tablica != -1 and zbior_wspolny: 
                zbior_wspolny = set(zbior_wspolny).intersection(temp_tablica)
            if temp_tablica != -1 and not zbior_wspolny:
                zbior_wspolny = temp_tablica
                flaga_zbior_wspolny_pusty_na_poczatku = 0
            if temp_tablica == -1 and not flaga_zbior_wspolny_pusty_na_poczatku:
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY NA TAGU" + colors.END)
            if temp_tablica == -1 and flaga_zbior_wspolny_pusty_na_poczatku: 
                print(colors.YELLOW + colors.BOLD + "\nBŁĄD UZUPEŁNIENIA ZBIORU WSPÓLNEGO - IGNORUJĘ WPISY NA TAGU" + colors.END)
                zbior_wspolny = []
                flaga_zbior_wspolny_pusty_na_poczatku = 0

    except:
        print(colors.RED + "\t[!] Błąd tworzenia zbioru wspólnego udzielających się pod wpisami NIELUBIANYCH tagów! funkcja ['zbior_wspolny_nielubianych_tagow']" + colors.END)
        return -1
    
    if temp_tablica != -1 and not zbior_wspolny:
            return []
    if temp_tablica == -1 and not zbior_wspolny:
            return -1

    print(colors.GREEN + "\t[+] Utworzono zbiór wspólny użytkowników udzielających się pod wpisami NIELUBIANYCH tagów!" + colors.END)
    return set(zbior_wspolny).intersection(dotychczasowy_zbior_wspolny)


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

    if zbior_wspolny and zbior_wspolny != -1:
        if len(zbior_wspolny) > 20:
            print(colors.GREEN + "\nWytypowano ponad 20 osób [" + str(len(zbior_wspolny)) + "] czy chcesz wyświetlić wszystkie?: [t/N]" + colors.END)
            odpowiedz = input()
            if odpowiedz == 't':
                print(colors.GREEN + colors.BOLD + "\nPodczas analizy wybranych użytkowników i tagów wytypowano następujące osoby [" + str(len(zbior_wspolny)) + "]:" + colors.END)
                indeks = 1
                for uzytkownik in zbior_wspolny:
                    print(colors.BLUE + colors.BOLD + "\t\t" + str(indeks) + ") " + uzytkownik + colors.END)
                    indeks += 1
            else:
                print(colors.YELLOW + "Zmień kryteria, aby zmniejszyć liczbę wytypowanych użytkowników i uruchom program ponownie")
                return 0
        else:
            print(colors.GREEN + colors.BOLD + "\nPodczas analizy wybranych użytkowników i tagów wytypowano następujące osoby [" + str(len(zbior_wspolny)) + "]:" + colors.END)
            indeks = 1
            for uzytkownik in zbior_wspolny:
                print(colors.BLUE + colors.BOLD + "\t\t" + str(indeks) + ") " + uzytkownik + colors.END)
                indeks += 1
            return 0
    else:
        print(colors.YELLOW + colors.BOLD + "\nPodczas analizy nie udało się znaleźć osób pasujących do wybranych kryteriów. Spróbuj poszerzyć zakres dat lub zmienić analizowane tagi i użytkowników\n" + colors.END)
        return -1

def wygeneruj_zbior_wspolny(zbior_wspolny):

    temp_zbior_wspolny = []

    if not tablica_lubianych_uzytkownikow and not tablica_lubianych_tagow and not tablica_nielubianych_uzytkownikow and not tablica_nielubianych_tagow: 
        print(colors.RED + colors.BOLD + "README byś chociaż przeczytał.\n\n" + colors.END)
        return -1

    if tablica_lubianych_uzytkownikow:
        temp_zbior_wspolny = zbior_wspolny_lubianych_uz(tablica_lubianych_uzytkownikow)
        if temp_zbior_wspolny == -1:
            print(colors.RED + colors.BOLD + "\nZbiór wspólny niewygenerowany z powodu błędów - ignoruję wpisy LUBIANYCH użytkowników" + colors.END)
        if not temp_zbior_wspolny:
            print(colors.RED + colors.BOLD + "\nBrak użytkowników odpowiadających kryteriom - ZBIÓR WSPÓLNY JEST PUSTY" + colors.END)
            return -1    
        if temp_zbior_wspolny != -1:
            zbior_wspolny = temp_zbior_wspolny
            print(colors.GREEN + colors.BOLD + "\nZbiór wspólny zawiera " + str(len(zbior_wspolny)) + " użytkowników" + colors.END)   
    else:
        print(colors.YELLOW + "\nNie wybrano żadnych lubianych użytkowników - POMIJAM" + colors.END)

    if tablica_nielubianych_uzytkownikow:
        temp_zbior_wspolny = zbior_wspolny_nielubianych_uz(tablica_nielubianych_uzytkownikow, zbior_wspolny)
        if temp_zbior_wspolny == -1:
            print(colors.RED + colors.BOLD + "\nZbiór wspólny niewygenerowany z powodu błędów - ignoruję wpisy NIELUBIANYCH użytkowników" + colors.END)
        if not temp_zbior_wspolny: 
            print(colors.RED + colors.BOLD + "\nBrak użytkowników odpowiadających kryteriom - ZBIÓR WSPÓLNY JEST PUSTY" + colors.END)
            return -1    
        if temp_zbior_wspolny != -1:
            zbior_wspolny = temp_zbior_wspolny
            print(colors.GREEN + colors.BOLD + "\nZbiór wspólny zawiera " + str(len(zbior_wspolny)) + " użytkowników" + colors.END)   
    else:
        print(colors.YELLOW + "\nNie wybrano żadnych nielubianych użytkowników - POMIJAM" + colors.END)
    
    if tablica_lubianych_tagow:
        temp_zbior_wspolny = zbior_wspolny_lubianych_tagow(tablica_lubianych_tagow, zbior_wspolny)
        if temp_zbior_wspolny == -1:
            print(colors.RED + colors.BOLD + "\nZbiór wspólny niewygenerowany z powodu błędów - ignoruję wpisy LUBIANYCH tagów" + colors.END)
        if not zbior_wspolny:
            print(colors.RED + colors.BOLD + "\nBrak użytkowników odpowiadających kryteriom. - ZBIÓR WSPÓLNY JEST PUSTY" + colors.END)
            return -1    
        if temp_zbior_wspolny != -1:
            zbior_wspolny = temp_zbior_wspolny
            print(colors.GREEN + colors.BOLD + "\nZbiór wspólny zawiera " + str(len(zbior_wspolny)) + " użytkowników" + colors.END)   
    else:
        print(colors.YELLOW + "\nNie wybrano żadnych lubianych tagów - POMIJAM" + colors.END)
        
    if tablica_nielubianych_tagow:
        temp_zbior_wspolny = zbior_wspolny_nielubianych_tagow(tablica_nielubianych_tagow, zbior_wspolny)
        if temp_zbior_wspolny == -1:
            print(colors.RED + colors.BOLD + "\nZbiór wspólny niewygenerowany z powodu błędów - ignoruję wpisy NIELUBIANYCH tagów" + colors.END)
        if not zbior_wspolny:
            print(colors.RED + colors.BOLD + "\nBrak użytkowników odpowiadających kryteriom. - ZBIÓR WSPÓLNY JEST PUSTY" + colors.END)
            return -1    
        if temp_zbior_wspolny != -1:
            zbior_wspolny = temp_zbior_wspolny
            print(colors.GREEN + colors.BOLD + "\nZbiór wspólny zawiera " + str(len(zbior_wspolny)) + " użytkowników" + colors.END)   
    else:
        print(colors.YELLOW + "\nNie wybrano żadnych nielubianych tagów - POMIJAM" + colors.END)
    
    return zbior_wspolny

#===== MAIN =====
zbior_wspolny = []

tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow = pobranie_listy_analizowanych_tagow_i_uzytkownikow()
wyswietl_informacje_o_pobranych_danych(tablica_nielubianych_uzytkownikow, tablica_nielubianych_tagow, tablica_lubianych_uzytkownikow, tablica_lubianych_tagow)
zbior_wspolny = wygeneruj_zbior_wspolny(zbior_wspolny)
if zbior_wspolny != -1:
    wyswietl_informacje_koncowe(zbior_wspolny)

