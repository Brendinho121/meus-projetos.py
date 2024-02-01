from tkinter import *
from PIL import Image, ImageTk
import datetime
from tkcalendar import Calendar
import pandas as pd
from tkinter import ttk
from random import randint
from tkinter import messagebox  

# Criando a interface
janela = Tk()
janela.title('Calendário de Férias GECAP')
janela.geometry('720x700')
janela.configure(bg = 'navy blue')

# carregando e redimensionando a imagem
image = Image.open('imagem_brb.jpg')
image = image.resize((70, 50))
img_photo = ImageTk.PhotoImage(image)
image_label = Label(janela, image=img_photo)
image_label.pack(pady=5, ipadx=10, anchor=NW)

# buscando a data atual
data_atual = datetime.datetime.now().date()

# criando o calendário
cal_meses = Calendar(janela, selectmode='day', date_pattern='dd/mm/yyyy', date_var=data_atual, font='Arial 30',
                      selectbackground='green', weekendforeground='red', othermonthweforeground='red')

# Formatando os paramêtros e ajustando a exibição do calendário na janela
cal_meses.pack(pady=70, padx=50, ipadx=200, ipady=40, anchor=CENTER)

# carrengando a planilha excel
df = pd.read_excel('ferias_gecap.xlsx', sheet_name='Ausências')

# cria e configura um Treeview para exibir os dados do arquivo excel
header =  ["funcionario", "tipo_ausencia", "data_inicio", "qntd_de_dias", "data_fim", "obs"]
tree = ttk.Treeview(janela, columns=header, show='headings')
for col in header:
    tree.heading(col, text=col)
    tree.column(col)

# criando um dicionário para armazenar as cores
funcionario_cores = {}

for index, row in df.iterrows():
    funcionario, tipo_ausencia, data_inicio, qntd_de_dias, data_fim, obs = row

    # Gera uma cor única para o funcionário e armazena no dicionário
    funcionario_cores[funcionario] = '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))

    # Insira a linha no Treeview com a cor exclusiva do funcionário
    tree.insert('', 'end', values=[funcionario, tipo_ausencia, data_inicio, qntd_de_dias, data_fim, obs])
    tree.pack(pady=40, ipady=130, padx=40, anchor=CENTER)

# função para marcar férias no calendário
def marcar_ferias(cal_widget, tree_widget, funcionario_cores):
    for index, row in df.iterrows():
        funcionario, tipo_ausencia, data_inicio, qntd_de_dias, data_fim, obs = row

        if pd.notna(qntd_de_dias):
            # Converter qntd de dias em um inteiro se ele não estiver vazio
            qntd_de_dias = int(qntd_de_dias)
            for day in range(qntd_de_dias):
                date = data_inicio + datetime.timedelta(days=day)

                # Obter a cor para o funcionário do dicionário
                cores = funcionario_cores.get(funcionario)
                cal_widget.calevent_create(date, f"Férias de {funcionario}", cores)
                tree_widget.insert('', 'end', values=[funcionario, tipo_ausencia, data_inicio, qntd_de_dias, data_fim, obs])

# chamando a função para marcar férias
marcar_ferias(cal_meses, tree, funcionario_cores)

# Função para exibir informações quando um dia é selecionado
def display_info(event):
    selected_date = cal_meses.get_date()
    selected_date = pd.to_datetime(selected_date)

    # Iterar pelas linhas da planilha e encontrar entradas que correspondem à data selecionada
    matching_entries = []
    for index, row in df.iterrows():
        funcionario, tipo_ausencia, data_inicio, qntd_de_dias, data_fim, obs = row

        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        
        print(data_inicio, selected_date, data_fim)
        if data_inicio <= selected_date <= data_fim:
            matching_entries.append(f"Funcionário: {funcionario}\n"
                                    f"Tipo de Ausência: {tipo_ausencia}\n"
                                    f"Data de Início: {data_inicio}\n"
                                    f"Quantidade de Dias: {qntd_de_dias}\n"
                                    f"Data de Fim: {data_fim}\n"
                                    f"Observações: {obs}\n")

    if matching_entries:
        info_text = "\n\n".join(matching_entries)
        messagebox.showinfo("Informações do Dia", f"Detalhes das Entradas no Dia {selected_date}:\n\n{info_text}")
    else:
        messagebox.showinfo("Informações do Dia", f"Nenhuma entrada encontrada para o dia {selected_date}")

# Vincular a função display_info ao evento de seleção no calendário
cal_meses.bind('<<CalendarSelected>>', display_info)

janela.mainloop()
