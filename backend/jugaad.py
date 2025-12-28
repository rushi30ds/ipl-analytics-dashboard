# import pandas as pd
# import numpy as np
# import json
#
# class NpEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.integer):
#             return int(obj)
#         if isinstance(obj, np.floating):
#             # replace NaN with None
#             if np.isnan(obj):
#                 return None
#             return float(obj)
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return super(NpEncoder, self).default(obj)
#
# # ---------------- DATA LOADING ----------------
# ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
# matches = pd.read_csv(ipl_matches)
#
# ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
# balls = pd.read_csv(ipl_ball)
#
# ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
# ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
# ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(lambda x: x.values[0].replace(x.values[1], ''), axis=1)
# batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]
#
# # ---------------- TEAM STATS ----------------
# def team1vsteam2(team, team2):
#     df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) |
#                  ((matches['Team2'] == team) & (matches['Team1'] == team2))].copy()
#
#     mp = df.shape[0]
#     won = df[df.WinningTeam == team].shape[0]
#     nr = df[df.WinningTeam.isnull()].shape[0]
#     loss = mp - won - nr
#
#     return {
#         'matchesplayed': mp,
#         'won': won,
#         'loss': loss,
#         'noResult': nr
#     }
#
#
# def allRecord(team):
#     df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
#
#     mp = df.shape[0]
#     won = df[df.WinningTeam == team].shape[0]
#     nr = df[df.WinningTeam.isnull()].shape[0]
#     loss = mp - won - nr
#     titles = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
#
#     return {
#         'matchesplayed': mp,
#         'won': won,
#         'loss': loss,
#         'noResult': nr,
#         'title': titles
#     }
#
#
# def teamAPI(team, matches=matches):
#     self_record = allRecord(team)
#     TEAMS = matches.Team1.unique()
#
#     against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
#
#     data = {team: {
#         'overall': self_record,
#         'against': against
#     }}
#
#     return json.dumps(data, cls=NpEncoder)
#
# # ---------------- BATTING STATS ----------------
# def batsmanRecord(batsman, df):
#     if df.empty:
#         return {}
#
#     out = df[df.player_out == batsman].shape[0]
#     df = df[df['batter'] == batsman]
#
#     inngs = df.ID.unique().shape[0]
#     runs = df.batsman_run.sum()
#     fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
#     sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
#
#     # JSON-safe average
#     avg = runs / out if out else None
#
#     nballs = df[~(df.extra_type == 'wides')].shape[0]
#     strike_rate = runs / nballs * 100 if nballs else None
#
#     gb = df.groupby('ID').sum()
#     fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
#     hundreds = gb[gb.batsman_run >= 100].shape[0]
#
#     try:
#         highest_score = int(gb.batsman_run.max())
#     except:
#         highest_score = None
#
#     not_out = inngs - out
#     mom = df[df.Player_of_Match == batsman].drop_duplicates('ID').shape[0]
#
#     return {
#         'innings': inngs,
#         'runs': runs,
#         'fours': fours,
#         'sixes': sixes,
#         'avg': avg,
#         'strikeRate': strike_rate,
#         'fifties': fifties,
#         'hundreds': hundreds,
#         'highestScore': highest_score,
#         'notOut': not_out,
#         'mom': mom
#     }
#
#
# def batsmanVsTeam(batsman, team, df):
#     df = df[df.BowlingTeam == team].copy()
#     return batsmanRecord(batsman, df)
#
#
# def batsmanAPI(batsman, balls=batter_data):
#     df = balls[balls.innings.isin([1, 2])]  # Exclude Super Over
#
#     self_record = batsmanRecord(batsman, df)
#     TEAMS = matches.Team1.unique()
#
#     against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
#
#     data = {
#         batsman: {
#             'all': self_record,
#             'against': against
#         }
#     }
#
#     return json.dumps(data, cls=NpEncoder)
#
# # ---------------- BOWLING STATS ----------------
# bowler_data = batter_data.copy()
#
# def bowlerRun(x):
#     if x[0] in ['penalty', 'legbyes', 'byes']:
#         return 0
#     return x[1]
#
# bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowlerRun, axis=1)
#
#
# def bowlerWicket(x):
#     return x[1] if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket'] else 0
#
# bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowlerWicket, axis=1)
#
#
# def bowlerRecord(bowler, df):
#     df = df[df['bowler'] == bowler]
#
#     inngs = df.ID.unique().shape[0]
#     nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
#     runs = df['bowler_run'].sum()
#
#     eco = runs / nballs * 6 if nballs else None
#     wicket = df.isBowlerWicket.sum()
#
#     avg = runs / wicket if wicket else None
#     strike_rate = nballs / wicket if wicket else None
#
#     gb = df.groupby('ID').sum()
#     w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]
#
#     try:
#         best = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True]).head(1).values[0]
#         best_figure = f"{int(best[0])}/{int(best[1])}"
#     except:
#         best_figure = None
#
#     mom = df[df.Player_of_Match == bowler].drop_duplicates('ID').shape[0]
#
#     return {
#         'innings': inngs,
#         'wicket': wicket,
#         'economy': eco,
#         'average': avg,
#         'strikeRate': strike_rate,
#         'fours': df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0],
#         'sixes': df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0],
#         'best_figure': best_figure,
#         '3+W': w3,
#         'mom': mom
#     }
#
#
# def bowlerVsTeam(bowler, team, df):
#     df = df[df.BattingTeam == team].copy()
#     return bowlerRecord(bowler, df)
#
#
# def bowlerAPI(bowler, balls=bowler_data):
#     df = balls[balls.innings.isin([1, 2])]
#     self_record = bowlerRecord(bowler, df)
#
#     TEAMS = matches.Team1.unique()
#     against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
#
#     data = {
#         bowler: {
#             'all': self_record,
#             'against': against
#         }
#     }
#
#     return json.dumps(data, cls=NpEncoder)
import pandas as pd
import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            if np.isnan(obj):
                return None
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# ---------------- DATA LOADING ----------------
ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)

ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
    lambda x: x.iloc[0].replace(x.iloc[1], ''), axis=1
)

batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]

# ---------------- TEAM STATS ----------------
def team1vsteam2(team, team2):
    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) |
                 ((matches['Team2'] == team) & (matches['Team1'] == team2))].copy()

    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr

    return {
        'matchesplayed': mp,
        'won': won,
        'loss': loss,
        'noResult': nr
    }


def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()

    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    titles = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]

    return {
        'matchesplayed': mp,
        'won': won,
        'loss': loss,
        'noResult': nr,
        'title': titles
    }


def teamAPI(team, matches=matches):
    self_record = allRecord(team)
    TEAMS = matches.Team1.unique()

    against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}

    data = {team: {
        'overall': self_record,
        'against': against
    }}

    return json.dumps(data, cls=NpEncoder)

# ---------------- BATTING STATS ----------------
def batsmanRecord(batsman, df):
    if df.empty:
        return {}

    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]

    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    avg = runs / out if out else None

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    strike_rate = runs / nballs * 100 if nballs else None

    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]

    try:
        highest_score = int(gb.batsman_run.max())
    except:
        highest_score = None

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID').shape[0]

    return {
        'innings': inngs,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strikeRate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highestScore': highest_score,
        'notOut': not_out,
        'mom': mom
    }


def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsmanRecord(batsman, df)


def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]

    self_record = batsmanRecord(batsman, df)
    TEAMS = matches.Team1.unique()

    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}

    data = {
        batsman: {
            'all': self_record,
            'against': against
        }
    }

    return json.dumps(data, cls=NpEncoder)

# ---------------- BOWLING STATS ----------------
bowler_data = batter_data.copy()

def bowlerRun(x):
    if x['extra_type'] in ['penalty', 'legbyes', 'byes']:
        return 0
    return x['total_run']

bowler_data['bowler_run'] = bowler_data.apply(bowlerRun, axis=1)


def bowlerWicket(x):
    return x['isWicketDelivery'] if x['kind'] in [
        'caught', 'caught and bowled', 'bowled',
        'stumped', 'lbw', 'hit wicket'
    ] else 0

bowler_data['isBowlerWicket'] = bowler_data.apply(bowlerWicket, axis=1)


def bowlerRecord(bowler, df):
    df = df[df['bowler'] == bowler]

    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()

    eco = runs / nballs * 6 if nballs else None
    wicket = df.isBowlerWicket.sum()

    avg = runs / wicket if wicket else None
    strike_rate = nballs / wicket if wicket else None

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    try:
        best = gb.sort_values(
            ['isBowlerWicket', 'bowler_run'],
            ascending=[False, True]
        ).head(1).iloc[0]
        best_figure = f"{int(best['isBowlerWicket'])}/{int(best['bowler_run'])}"
    except:
        best_figure = None

    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID').shape[0]

    return {
        'innings': inngs,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'strikeRate': strike_rate,
        'fours': df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0],
        'sixes': df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0],
        'best_figure': best_figure,
        '3+W': w3,
        'mom': mom
    }


def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]
    self_record = bowlerRecord(bowler, df)

    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}

    data = {
        bowler: {
            'all': self_record,
            'against': against
        }
    }

    return json.dumps(data, cls=NpEncoder)
