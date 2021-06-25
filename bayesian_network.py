import numpy as np
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD

max_shots = 15  # maksymalna liczba celnych strzałów
max_goals = 10  # maksymalna liczba goli

def network_from_dictionary(dict):
    # lista krawędzi
    edges = [('HomeTeam', 'HST'), ('HomeTeam', 'FTAG'), ('HST', 'FTHG'), ('FTHG', 'FTR'),
             ('AwayTeam', 'AST'), ('AwayTeam', 'FTHG'), ('AST', 'FTAG'), ('FTAG', 'FTR')]

    # stworzenie modelu
    model = BayesianModel(edges)
    
    # ustalenie kardynalności zmiennych
    team_list = list(dict.keys())
    teams_card = len(team_list)
    shots_card = max_shots+1
    goals_card = max_goals+1
    
    # HomeTeam / AwayTeam CPD
    prob = np.ones((teams_card, 1))/teams_card
    cpd_home = TabularCPD('HomeTeam', teams_card, prob, state_names={'HomeTeam': team_list})
    cpd_away = TabularCPD('AwayTeam', teams_card, prob, state_names={'AwayTeam': team_list})
    
    # HST / AST CPD
    prob = np.zeros((shots_card, teams_card))
    for k in range(shots_card):
        for id in range(teams_card):
            lam = dict[team_list[id]][0]
            # rozkład Poissona
            prob[k, id] = np.e**(-lam)*lam**k/np.math.factorial(k)
    # normalizacja
    prob /= np.sum(prob, 0)
    
    cpd_hst = TabularCPD('HST', shots_card, prob, evidence=['HomeTeam'], evidence_card=[teams_card],
                         state_names={'HomeTeam': team_list, 'HST': list(np.arange(shots_card))})
    cpd_ast = TabularCPD('AST', shots_card, prob, evidence=['AwayTeam'], evidence_card=[teams_card],
                         state_names={'AwayTeam': team_list, 'AST': list(np.arange(shots_card))})
    
    # FTHG / FTAG CPD
    prob = np.zeros((goals_card, teams_card*shots_card))
    for k in range(goals_card):
        for i in range(teams_card*shots_card):
            id = i//teams_card
            n = i%teams_card
            p = dict[team_list[id]][1]
            # rozkład Bernoulliego
            prob[k, i] = np.math.comb(n, k)*p**k*(1-p)**(n-k)
    # normalizacja
    prob /= np.sum(prob, 0)
    
    cpd_fthg = TabularCPD('FTHG', goals_card, prob, evidence=['AwayTeam', 'HST'],
                          evidence_card=[teams_card, shots_card],
                          state_names={'AwayTeam': team_list, 'HST': list(np.arange(shots_card)),
                          'FTHG': list(np.arange(goals_card))})
    cpd_ftag = TabularCPD('FTAG', goals_card, prob, evidence=['HomeTeam', 'AST'],
                          evidence_card=[teams_card, shots_card],
                          state_names={'HomeTeam': team_list, 'AST': list(np.arange(shots_card)),
                          'FTAG': list(np.arange(goals_card))})
    
    # FTR CPD
    prob = np.zeros((3, goals_card*goals_card))
    for r in range(3):
        for i in range(goals_card*goals_card):
            hg = i//goals_card
            ag = i%goals_card
            if r==0 and hg>ag:
                p = 1.0
            elif r==1 and hg==ag:
                p = 1.0
            elif r==2 and hg<ag:
                p = 1.0
            else:
                p = 0.0
            prob[r, i] = p
    
    cpd_ftr = TabularCPD('FTR', 3, prob, evidence=['FTHG', 'FTAG'], evidence_card=[goals_card, goals_card],
                         state_names={'FTR': ['H', 'D', 'A'],
                         'FTHG': list(np.arange(goals_card)), 'FTAG': list(np.arange(goals_card))})
    
    # dodanie cpd i zwrócenie modelu modelu
    model.add_cpds(cpd_home, cpd_away, cpd_hst, cpd_ast, cpd_fthg, cpd_ftag, cpd_ftr)
    return model
    
