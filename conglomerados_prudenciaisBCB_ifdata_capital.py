import requests
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
import os

# inicialzando a variável ano_mes_inicial
ano_mes_inicial = "201703"

# Verificar se o formato está correto (opcional)
if ano_mes_inicial and ano_mes_inicial.isdigit() and len(ano_mes_inicial) == 6:
    print("mes-ano valido")
else:
    print("Formato inválido. Certifique-se de inserir no formato AAAAMM.")

# Solicitar ao usuário o número de períodos desejados
numero_de_periodos = simpledialog.askinteger("Input", "Informe o número de períodos desejados:")

if numero_de_periodos is not None:
    # Inicializar a lista anos_meses com o mês-ano inicial
    anos_meses = [ano_mes_inicial]

    # Adicionar períodos subsequentes de três meses
    for _ in range(1, numero_de_periodos):
        ano_mes_inicial = pd.to_datetime(ano_mes_inicial, format="%Y%m") + pd.DateOffset(months=3)
        anos_meses.append(ano_mes_inicial.strftime("%Y%m"))

else:
    print("Número de períodos não fornecido. Encerrando o programa.")

# Defina a lista de anos-mês desejados
print(anos_meses)

# Inicializar o DataFrame dados_cadastrais_final
dados_cadastrais_final = pd.DataFrame()

def solicitar_ano_mes():
    root = tk.Tk()
    root.withdraw()

    # Solicitar o ano-mês por meio de um pop-up
    ano_mes = ano_mes_inicial

def obter_dados(ano_mes):
    # Montar o URL com o ano-mês fornecido
    url = f"https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)?@AnoMes={ano_mes}&@TipoInstituicao=1&@Relatorio=%275%27&$format=json&$select=CodInst,AnoMes,Conta,Saldo"

    # Realizar a solicitação HTTP
    response = requests.get(url)

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Converter os dados JSON para DataFrame pandas
        dados_json = response.json()
        df = pd.DataFrame(dados_json['value'])
        return df
    else:
        print(f"Falha na solicitação. Código de status: {response.status_code}")
        return None

def obter_dados_cadastrais(ano_mes):
    # Montar o URL com o ano-mês fornecido para dados cadastrais
    url_cadastral = f"https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes={ano_mes}&$top=1000&$filter=CodConglomeradoPrudencial%20eq%20CodInst&$format=json&$select=CodInst,NomeInstituicao,Tcb,Atividade,Uf,Sr"

    # Realizar a solicitação HTTP para dados cadastrais
    response_cadastral = requests.get(url_cadastral)

    # Verificar se a solicitação foi bem-sucedida
    if response_cadastral.status_code == 200:
        # Converter os dados JSON para DataFrame pandas
        dados_cadastrais_json = response_cadastral.json()
        df_cadastral = pd.DataFrame(dados_cadastrais_json['value'])
        return df_cadastral
    else:
        print(f"Falha na solicitação de dados cadastrais. Código de status: {response_cadastral.status_code}")
        return None

# Inicializar o DataFrame dados_indicadores_final
dados_indicadores_final = pd.DataFrame()

if __name__ == "__main__":
    # Solicitar ano-mês
    for ano_mes in anos_meses:
        # Obter dados usando o ano-mês fornecido para indicadores
        dados_indicadores_df = obter_dados(ano_mes)



        # Obter dados usando o ano-mês fornecido para dados cadastrais
        dados_cadastrais_df = obter_dados_cadastrais(ano_mes)

        # Adicionar coluna "Periodo" com o valor do ano-mês
        dados_cadastrais_df["Periodo"] = ano_mes

        # Exibir DataFrames
        if dados_indicadores_df is not None:
            print("Dados de Indicadores obtidos com sucesso:")
            print(dados_indicadores_df)

            # Converter a coluna "Saldo" para número decimal
            dados_indicadores_df["Saldo"] = pd.to_numeric(dados_indicadores_df["Saldo"], errors="coerce")


            contas_para_filtrar = ["79664", "79659", "79660", "79650", "79645", "79646", "79647", "79648", "79649", "79652",
                       "79653", "79654", "79655", "79651", "79656", "79665", "79658", "92999", "79661", "79662"]

            contas_para_preencher = ["IB", "ICP", "NI", "RWAcpad", "Capital_principal", "Capital_complementar", "PR_I", "NII",
                                    "PR", "RWAcam", "RWAcom", "RWAjur", "RWAacs", "RWAmpad", "RWAopad", "RWA", "Exposicao_total",
                                    "ACP", "RA", "IMOB"]

            # Lista de colunas a serem convertidas para números decimais
            colunas_para_converter = ["RWAcpad", "Capital_principal", "Capital_complementar", "PR_I", "NII",
                                    "PR", "RWAcam", "RWAcom", "RWAjur", "RWAacs", "RWAmpad", "RWAopad", "RWA", "Exposicao_total"]

            colunas_para_converter = [col for col in colunas_para_converter if col in dados_cadastrais_df.columns]

            # Converter colunas para números decimais
            dados_cadastrais_df[colunas_para_converter] = dados_cadastrais_df[colunas_para_converter].apply(pd.to_numeric, errors='coerce')

            # Verificar se as colunas existem no DataFrame antes de converter para porcentagem
            colunas_para_converter_porcentagem = ["IB", "ICP", "NI", "RA", "IMOB"]

            colunas_para_converter_porcentagem = [col for col in colunas_para_converter_porcentagem if col in dados_cadastrais_df.columns]

            

            # Filtrar dados_indicadores_df e realizar as junções
            for conta in contas_para_filtrar:
                dados_filtrados = dados_indicadores_df[dados_indicadores_df["Conta"] == conta]
                coluna_destino = contas_para_preencher[contas_para_filtrar.index(conta)]  # Usar o nome da coluna de destino
                dados_cadastrais_df = pd.merge(dados_cadastrais_df, dados_filtrados[['CodInst', 'Saldo']], on='CodInst', how='left')
                dados_cadastrais_df.rename(columns={'Saldo': coluna_destino}, inplace=True)

            # Verificar se as colunas existem no DataFrame antes de preencher
            colunas_para_preencher = contas_para_preencher

            # Filtrar as colunas existentes
            colunas_existentes = [col for col in colunas_para_preencher if col in dados_cadastrais_df.columns]

            # Preencher colunas com valores de exemplo
            dados_cadastrais_df[colunas_existentes].fillna("", inplace=True)

            # Substituir ponto por vírgula nas colunas IB, ICP e NI
            #dados_cadastrais_df["IB"] = dados_cadastrais_df["IB"].astype(str).str.replace('.', ',')
            #dados_cadastrais_df["ICP"] = dados_cadastrais_df["ICP"].astype(str).str.replace('.', ',')
            #dados_cadastrais_df["NI"] = dados_cadastrais_df["NI"].astype(str).str.replace('.', ',')

            # Exibir DataFrames
            if dados_indicadores_df is not None:
                print("Dados de Indicadores obtidos com sucesso:")
                print(dados_indicadores_df)

                # Adicionar os dados ao DataFrame final de indicadores
                dados_indicadores_final = pd.concat([dados_indicadores_final, dados_indicadores_df], ignore_index=True)

            else:
                print("Falha ao obter dados de Indicadores.")

            if dados_cadastrais_df is not None:
                print("\nDados Cadastrais obtidos com sucesso:")
                print(dados_cadastrais_df)

                # Adicionar os dados ao DataFrame final
                dados_cadastrais_final = pd.concat([dados_cadastrais_final, dados_cadastrais_df], ignore_index=True)

            else:
                print("Falha ao obter dados Cadastrais.")

            # Converter a coluna "Periodo" para o formato de data desejado
            dados_cadastrais_final['Periodo'] = dados_cadastrais_final['Periodo'].apply(lambda x: f"{x[:4]}/{x[4:]}" if pd.notnull(x) else '')

            # Remover barras duplicadas, se houver
            dados_cadastrais_final['Periodo'] = dados_cadastrais_final['Periodo'].str.replace('//', '/', regex=False)

            # Exibir o DataFrame final
            print(dados_cadastrais_final)

            # Salvar o DataFrame
            user_directory = os.path.expanduser("Z:\IF_DATA")  # Obter o diretório do usuário
            output_directory = os.path.join(user_directory, "DadosBCB")

            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            excel_file_path = os.path.join(output_directory, f"dados_cadastrais_todos_periodos.xlsx")
            dados_cadastrais_final.to_excel(excel_file_path, index=False, header=True)

            #excel_file_path_indicadores = os.path.join(output_directory, f"dados_indicadores_todos_periodos.xlsx")
            #dados_indicadores_final.to_excel(excel_file_path_indicadores, index=False, header=True)

            print(f"\nDataFrame final salvo como arquivo Excel em {excel_file_path}")
