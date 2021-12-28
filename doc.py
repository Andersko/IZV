#!/usr/bin/python3.8
# coding=utf-8

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


def make_doc(df: pd.DataFrame):
    # Print data
    print("----------------------------------------")
    print("[DATA]")
    print("accidents that took one or more life: " + str(len(df[df['p9'] == 1].index)))
    print("That is % of all accidents: " + str(round(len(df[df['p9'] == 1].index) / len(df.index) * 100, 2)) + "%")
    print("Number of deaths in first 24h after accident: " + str(df['p13a'].sum()))

    # Keep only accidents that took life
    df1 = df[df["p9"] == 1]

    # Keep only p12 (accident cause) column
    df1 = df1[['p12']]

    # Group accidents cause to main reason categories
    df1[(df1["p12"] >= 201) & (df1["p12"] <= 209)] = 200
    df1[(df1["p12"] >= 301) & (df1["p12"] <= 311)] = 300
    df1[(df1["p12"] >= 401) & (df1["p12"] <= 414)] = 400
    df1[(df1["p12"] >= 501) & (df1["p12"] <= 516)] = 500
    df1[(df1["p12"] >= 601) & (df1["p12"] <= 615)] = 600

    # Count by accidents cause (p12)
    df1['cnt'] = 0
    df1 = df1.groupby(['p12']).agg({'cnt': 'count'})
    df1.sort_values(by=['cnt'], inplace=True)
    df1.reset_index(level=0, inplace=True)

    # Set ticks labels
    df1['p12'] = df1['p12'].replace({
         100: "nezaviněná řidičem",
         200: "nepřiměřená rychlost jízdy",
         300: "nesprávné předjíždění",
         400: "nedání přednosti v jízdě",
         500: "nesprávný způsob jízdy",
         600: "technická závada vozidla"
    })

    # Print plot data
    print("----------------------------------------")
    print("\tGraph values:")
    print(df1.to_string(index=False))

    # Style and save plot
    fig, ax = plt.subplots(figsize=(7, 2))
    sns.barplot(ax=ax, data=df1, x='cnt', y='p12', palette='Blues_d', orient='h')
    ax.set_title('Celkové počty nehôd, podľa ich hlavnej príčiny', fontweight='bold')
    ax.set(ylabel='', xlabel='')
    ax.set(xlim=(0, 50000))
    ax.tick_params(axis='both', width=0)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig('doc1.png')
    plt.close(fig)

    # Keep only accidents that took life
    df1 = df[df["p9"] == 1]

    # Keep only p12 (accident cause) column
    df1 = df1[['p12']]

    # Keep only 5xx accident causes (unappropriated driving style)
    df1 = df1[(df1["p12"] >= 501) & (df1["p12"] <= 516)]

    # Count by accidents cause (p12)
    df1['cnt'] = 0
    df1 = df1.groupby(['p12']).agg({'cnt': 'count'})
    df1.sort_values(by=['cnt'], inplace=True, ascending=False)
    df1.reset_index(level=0, inplace=True)

    # Replace count labels and rename columns
    df1['p12'] = df1['p12'].replace({
        501: "jízda po nesprávné straně vozovky, vjetí do protisměru",
        502: "vyhýbání bez dostatečného bočního odstupu (vůle)",
        503: "nedodržení bezpečné vzdálenosti za vozidlem",
        504: "nesprávné otáčení nebo couvání",
        505: "chyby při udání směru jízdy",
        506: "bezohledná, agresivní, neohleduplná jízda",
        507: "náhlé bezdůvodné snížení rychlosti jízdy, zabrzdění nebo zastavení",
        508: "řidič se plně nevěnoval řízení vozidla",
        509: "samovolné rozjetí nezajištěného vozidla",
        510: "vjetí na nezpevněnou komunikaci",
        511: "nezvládnutí řízení vozidla",
        512: "jízda (vjetí) jednosměrnou ulicí, silnicí (v protisměru)",
        513: "nehoda v důsledku  použití (policií) prostředků k násilnému zastavení vozidla (zastavovací pásy, "
             + "zábrana, vozidlo atp.)",
        514: "nehoda v důsledku použití služební zbraně (policií)",
        515: "nehoda při provádění služebního zákroku (pronásledování pachatele atd.)",
        516: "jiný druh nesprávného způsobu jízdy"
    })
    df1.rename(columns={"p12": "Nesprávny způsob jízdy (detailný důvod)", "cnt": "počet"}, inplace=True)

    # Print table
    print("----------------------------------------")
    print("\tTable values:")
    print(df1.to_string(index=False))


if __name__ == "__main__":
    print("creating data frame...")
    df = pd.read_pickle("accidents.pkl.gz")

    print("creating documents...")
    make_doc(df)
