import os
import time
import json
from random import random
from datetime import datetime
from sys import argv

import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Função para extrair a taxa CDI
def extrair_taxa_cdi():
    url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.4392/dados'
    try:
        response = requests.get(url=url)
        response.raise_for_status()
    except requests.HTTPError:
        print("Dado não encontrado, continuando.")
        return None
    except Exception as exc:
        print("Erro ao conectar na API.")
        raise exc
    else:
        dado = json.loads(response.text)[-1]['valor']
        return float(dado)


# Função para salvar os dados em um arquivo CSV
def salvar_dados_csv(cdi_base):
    if os.path.exists('./taxa-cdi.csv'):
        print("Arquivo 'taxa-cdi.csv' já existe. Não serão adicionados novos dados.")
        return

    for _ in range(0, 10):
        data_e_hora = datetime.now()
        data = datetime.strftime(data_e_hora, '%Y/%m/%d')
        hora = datetime.strftime(data_e_hora, '%H:%M:%S')
        cdi = cdi_base + (random() - 0.5)

        if not os.path.exists('./taxa-cdi.csv'):
            with open(file='./taxa-cdi.csv', mode='w', encoding='utf8') as fp:
                fp.write('data,hora,taxa\n')

        with open(file='./taxa-cdi.csv', mode='a', encoding='utf8') as fp:
            fp.write(f'{data},{hora},{cdi}\n')

        time.sleep(1)

    print("Dados salvos no arquivo 'taxa-cdi.csv'.")


# Função para gerar o gráfico
def gerar_grafico(nome_grafico):
    try:
        df = pd.read_csv('./taxa-cdi.csv')
    except FileNotFoundError:
        print("Erro: Arquivo 'taxa-cdi.csv' não encontrado.")
        return

    plt.figure(figsize=(10, 6))
    grafico = sns.lineplot(x='hora', y='taxa', data=df, marker="o", sort=False)
    grafico.set_xticklabels(labels=df['hora'], rotation=45, ha='right')
    grafico.set_title("Variação da Taxa CDI", fontsize=16)
    grafico.set_xlabel("Hora", fontsize=12)
    grafico.set_ylabel("Taxa CDI", fontsize=12)
    grafico.get_figure().tight_layout()
    grafico.get_figure().savefig(f"{nome_grafico}.png")
    print(f"Gráfico salvo como '{nome_grafico}.png'.")


# Main
def main():
    if len(argv) < 2:
        print("Erro: Você deve passar o nome do gráfico como argumento.")
        return

    nome_grafico = argv[1]

    if not os.path.exists('./taxa-cdi.csv'):
        print("Arquivo 'taxa-cdi.csv' não encontrado. Iniciando extração de dados...")
        cdi_base = extrair_taxa_cdi()

        if cdi_base is None:
            print("Nenhum dado de CDI encontrado. Encerrando execução.")
            return

        salvar_dados_csv(cdi_base)

    print("Gerando gráfico...")
    gerar_grafico(nome_grafico)
    print("Processo concluído com sucesso.")


if __name__ == "__main__":
    main()
