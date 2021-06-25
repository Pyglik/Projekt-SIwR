#!/usr/bin/python3

import csv
import datetime
import numpy as np
import bayesian_network as bn
from pgmpy.inference import VariableElimination

if __name__ == '__main__':
    # wczytanie danych z wejścia
    Date = input()
    HomeTeam = input()
    AwayTeam = input()
    
    # wczytanie daty do obiektu datetime
    date_in = datetime.datetime.strptime(Date, '%d/%m/%Y')
    
    # słownik zawierający dane o drużynach jako tablica:
    # [suma celnych strzałów, liczba meczy, suma goli przeciwko, suma celnych strzałów przeciwko]
    teams = {}
    
    # wczytanie danych z pliku csv
    with open('data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # pominięcie pierwszego wiersza
            if row[0] == 'Date':
                continue
            
            # pominięcie przyszłych meczów
            date = datetime.datetime.strptime(row[0], '%d/%m/%Y')
            if date >= date_in:
                continue
            
            # HomeTeam
            if row[1] not in teams.keys():
                teams[row[1]] = [0, 0, 0, 0]
            teams[row[1]][0] += int(row[11])
            teams[row[1]][1] += 1
            teams[row[1]][2] += int(row[4])
            teams[row[1]][3] += int(row[12])
            
            # AwayTeam
            if row[2] not in teams.keys():
                teams[row[2]] = [0, 0, 0, 0]
            teams[row[2]][0] += int(row[12])
            teams[row[2]][1] += 1
            teams[row[2]][2] += int(row[3])
            teams[row[2]][3] += int(row[11])
    
    # sprawdzenie, czy podane drużyny znajdują się w bazie
    if HomeTeam not in teams.keys() or AwayTeam not in teams.keys():
        exit(1)
    
    # zmiana danych o drużynach na tablicę:
    # [lambda (średnia liczba celnych strzałów), p (prawdopodobieństwo wpuszczenia strzału do bramki)]
    for t in teams.keys():
        st, n, ga, sta = teams[t]
        teams[t] = [st/n, ga/sta]
    
    # utworzenie sieci Bayesowskiej i wykonanie inferencji
    model = bn.network_from_dictionary(teams)
    infer = VariableElimination(model)
    q = infer.query(['FTR'], evidence={'HomeTeam': HomeTeam, 'AwayTeam': AwayTeam})
    
    # znalezienie i wypisanie najbardziej prawdopodobnego wyniku
    res = np.argmax(q.values)
    print(q.state_names['FTR'][res])
    
