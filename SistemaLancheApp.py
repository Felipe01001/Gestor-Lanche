import datetime
from SistemaLanche import McFastBurguer
import tkinter as tk
from tkinter import Toplevel, ttk, messagebox, simpledialog, PhotoImage

class McFastBurguerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("McFast Burguer - Sistema de Pedidos")
        self.root.bind("<Configure>", self.ajustar_responsividade)
        self.root.geometry("800x600")  # Define um tamanho inicial mediano para a janela
        self.mc_fast_burguer = McFastBurguer()
        self.pedido_atual = []  # Lista para manter todos os itens do pedido atual

        # Tema escuro
        self.root.configure(bg="#333333")
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure("Treeview", 
            background="#999999", 
            foreground="white", 
            fieldbackground="#333333",
            font=("Helvetica", 12)
        )
        estilo.map('Treeview', background=[('selected', '#555555')])

        # Carregar imagens
        self.icone_aumentar = PhotoImage(file="img/botao-de-upload.png")
        self.icone_apagar = PhotoImage(file="img/excluir.png")

        # Configuração de frames
        self.frame_cardapio = tk.Frame(root, bg="#222222")
        self.frame_cardapio.grid(row=0, column=0, sticky="nsew")

        self.frame_pedido = tk.Frame(root, bg="#222222")
        self.frame_pedido.grid(row=0, column=1, sticky="nsew")


        # Ajustar proporções das colunas
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Inicialização das interfaces
        self._criar_cardapio()
        self._criar_pedido()
    def ajustar_responsividade(self, event=None):
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()

        # Limitar os tamanhos máximos e mínimos da fonte
        tamanho_fonte = max(12, min(14, largura // 80))
        nova_fonte = ("Helvetica", tamanho_fonte)
        estilo = ttk.Style()
        estilo.configure("Treeview", font=nova_fonte)

        # Limitar tamanhos das colunas para evitar cortes
        largura_coluna_cardapio = max(200, min(300, largura // 2 - 50))
        self.lista_cardapio.column("#0", width=largura_coluna_cardapio // 2)
        self.lista_cardapio.column("Preço", width=largura_coluna_cardapio // 4)

        largura_coluna_pedido = max(200, min(300, largura // 2 - 50))
        self.lista_pedido.column("Item", width=largura_coluna_pedido // 2)
        self.lista_pedido.column("Quantidade", width=largura_coluna_pedido // 4)
        self.lista_pedido.column("Preço", width=largura_coluna_pedido // 4)


    def abrir_menu_lateral(self):
        """Abre o menu lateral (navbar)."""
        self.frame_menu_lateral = tk.Frame(self.root, bg="#222222")
        self.frame_menu_lateral.place(x=0, y=0, relwidth=0.2, relheight=1)

        btn_relatorio = tk.Button(self.frame_menu_lateral, text="Gerar Relatório", command=self.gerar_relatorio)
        btn_relatorio.pack(pady=10)

        btn_controle = tk.Button(self.frame_menu_lateral, text="Abrir Controle de Pedidos", command=self.abrir_janela_controle)
        btn_controle.pack(pady=10)

        btn_fechar_menu = tk.Button(self.frame_menu_lateral, text="Fechar Menu", command=self.fechar_menu_lateral)
        btn_fechar_menu.pack(pady=10)

    def fechar_menu_lateral(self):
        """Fecha o menu lateral."""
        self.frame_menu_lateral.destroy()

    def abrir_janela_controle(self):
        """Abre uma nova janela para controle dos pedidos."""
        if hasattr(self, "janela_controle") and self.janela_controle.winfo_exists():
            self.janela_controle.lift()
            return

        self.janela_controle = Toplevel(self.root)
        self.janela_controle.title("Controle de Pedidos")

        # Tabela de pedidos (adicionando coluna Data/Hora)
        self.lista_controle = ttk.Treeview(
                self.janela_controle,
                columns=("Pedido","Item", "Quantidade", "Preço", "Status", "Data/Hora"),
                show="headings",
                height=20
            )              
        self.lista_controle.pack(fill=tk.BOTH, expand=True)  # Exibe a tabela
        self.lista_controle.heading("Pedido", text="Pedido")  # Cabeçalho da coluna
        self.lista_controle.column("Pedido", width=80, anchor=tk.CENTER)  # Largura e alinhamento
        self.lista_controle.heading("Item", text="Item")
        self.lista_controle.heading("Quantidade", text="Quantidade")
        self.lista_controle.heading("Preço", text="Preço")
        self.lista_controle.heading("Status", text="Status")
        self.lista_controle.heading("Data/Hora", text="Data/Hora")
        self.lista_controle.column("Item", width=200, anchor=tk.W)
        self.lista_controle.column("Quantidade", width=100, anchor=tk.CENTER)
        self.lista_controle.column("Preço", width=100, anchor=tk.CENTER)
        self.lista_controle.column("Status", width=100, anchor=tk.CENTER)
        self.lista_controle.column("Data/Hora", width=150, anchor=tk.CENTER)

        btn_concluir = tk.Button(
            self.janela_controle,
            text="Marcar como Concluído",
            command=self.marcar_como_concluido
        )
        btn_concluir.pack(pady=5)

        self._atualizar_janela_controle()

    def _atualizar_janela_controle(self):
        """Atualiza os dados na janela de controle."""
        self.lista_controle.delete(*self.lista_controle.get_children())

        for idx, pedido in enumerate(self.mc_fast_burguer.pedidos, start=1):
            data_hora_formatada = pedido["data_hora"].strftime('%d/%m/%Y %H:%M:%S')
            valores_pedido = [idx, "", "", "", pedido["status"], data_hora_formatada]  

            pedido_id = self.lista_controle.insert(
                "", tk.END, text=f"Pedido #{idx}", values=valores_pedido
            )

            total_pedido = 0
            for item, preco, quantidade in pedido["itens"]:
                subtotal = preco * quantidade
                total_pedido += subtotal

                valores_item = [idx, item, quantidade, f"{subtotal:.2f}", "", ""]  

                self.lista_controle.insert(
                    pedido_id, tk.END, values=valores_item
                )

            valores_total = [idx, "", "", f"Total: R$ {total_pedido:.2f}", "", ""]
            self.lista_controle.insert(
                pedido_id, tk.END, values=valores_total
            )

            if pedido["status"] == "concluído":
                self.lista_controle.item(pedido_id, tags=("concluido",))

            self.lista_controle.tag_configure("concluido", background="lightgreen")

    def marcar_como_concluido(self):
        """Marca o pedido selecionado como concluído."""
        item_selecionado = self.lista_controle.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um pedido.")
            return

        valores = self.lista_controle.item(item_selecionado)["values"]
        if not valores or valores[4] == "":
            messagebox.showwarning("Aviso", "Selecione o título de um pedido para concluir.")
            return

        pedido_idx = int(self.lista_controle.item(item_selecionado)["text"].split("#")[1]) - 1
        self.mc_fast_burguer.pedidos[pedido_idx]["status"] = "concluído"

        self._atualizar_janela_controle()

    def _criar_cardapio(self):
        """Cria a interface do cardápio."""
        label_cardapio = tk.Label(self.frame_cardapio, text="Cardápio", font=("Helvetica", 20, "bold"), bg="#222222", fg="white")
        label_cardapio.grid(row=0, column=0, pady=10)
        self.frame_cardapio.grid_columnconfigure(0, weight=1)
        self.frame_cardapio.grid_rowconfigure(1, weight=1)


        self.lista_cardapio = ttk.Treeview(self.frame_cardapio, columns=("Preço"), show="tree headings", height=20)
        self.lista_cardapio.heading("#0", text="Categoria / Item")
        self.lista_cardapio.heading("Preço", text="Preço (R$)")
        self.lista_cardapio.column("#0", width=200, anchor=tk.W)
        self.lista_cardapio.column("Preço", width=100, anchor=tk.CENTER)
        self.lista_cardapio.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        for categoria, itens in self.mc_fast_burguer.cardapio.items():
            cat_id = self.lista_cardapio.insert("", tk.END, text=categoria, open=True)
            for item, preco in itens.items():
                self.lista_cardapio.insert(cat_id, tk.END, text=item, values=(f"{preco:.2f}"))

        self.lista_cardapio.bind("<Double-Button-1>", self.adicionar_item_direto)
        self.lista_cardapio.bind("<Return>", self.adicionar_item_direto)

        btn_adicionar = tk.Button(self.frame_cardapio, text="Adicionar ao Pedido", command=self._adicionar_ao_pedido)
        btn_adicionar.grid(row=2, column=0, pady=10)

    def adicionar_item_direto(self, event=None):
        """Adiciona o item selecionado ao pedido com quantidade 1."""
        item_selecionado = self.lista_cardapio.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item do cardápio.")
            return

        dados_item = self.lista_cardapio.item(item_selecionado)
        item_nome = dados_item.get("text", "")

        if not item_nome:
            messagebox.showwarning("Aviso", "Por favor, selecione um item válido.")
            return

        preco = None
        for _, nome, preco_item, _ in self.mc_fast_burguer.itens_numerados:
            if nome == item_nome:
                preco = preco_item
                break

        if preco is None:
            messagebox.showerror("Erro", "Item não encontrado no sistema.")
            return

        self.pedido_atual.append((item_nome, preco, 1))
        self._atualizar_pedido()

    def _adicionar_ao_pedido(self):
        """Adiciona um item ao pedido com quantidade especificada pelo usuário."""
        item_selecionado = self.lista_cardapio.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item do cardápio.")
            return

        dados_item = self.lista_cardapio.item(item_selecionado)
        item_nome = dados_item.get("text", "")

        if not item_nome:
            messagebox.showwarning("Aviso", "Por favor, selecione um item válido.")
            return

        quantidade = simpledialog.askinteger("Quantidade", f"Digite a quantidade para {item_nome}:")
        if not quantidade or quantidade <= 0:
            messagebox.showwarning("Aviso", "Quantidade inválida.")
            return

        preco = None
        for _, nome, preco_item, _ in self.mc_fast_burguer.itens_numerados:
            if nome == item_nome:
                preco = preco_item
                break

        if preco is None:
            messagebox.showerror("Erro", "Item não encontrado no sistema.")
            return

        self.pedido_atual.append((item_nome, preco, quantidade))
        self._atualizar_pedido()

    def _criar_pedido(self):
        """Cria a interface do pedido."""
        label_pedido = tk.Label(self.frame_pedido, text="Pedido Atual", font=("Helvetica", 20, "bold"), bg="#222222", fg="white")
        label_pedido.grid(row=0, column=0, pady=10, columnspan=3)

        self.lista_pedido = ttk.Treeview(
            self.frame_pedido, 
            columns=("Item", "Quantidade", "Preço"), 
            show="headings", 
            height=20
        )

        self.frame_pedido.grid_columnconfigure(0, weight=1)
        self.frame_pedido.grid_columnconfigure(1, weight=1)
        self.frame_pedido.grid_columnconfigure(2, weight=1)
        self.frame_pedido.grid_rowconfigure(1, weight=1)

        
        self.lista_pedido.heading("Item", text="Item")
        self.lista_pedido.heading("Quantidade", text="Quantidade")
        self.lista_pedido.heading("Preço", text="Preço (R$)")
        self.lista_pedido.column("Item", width=200, anchor=tk.W)
        self.lista_pedido.column("Quantidade", width=100, anchor=tk.CENTER)
        self.lista_pedido.column("Preço", width=100, anchor=tk.CENTER)
        self.lista_pedido.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.lista_pedido.bind("<<TreeviewSelect>>", self.mostrar_botoes_item)

        # Configurar botão "Finalizar Pedido" ao centro e os outros ao lado
        self.btn_apagar_item = tk.Button(self.frame_pedido, image=self.icone_apagar, command=self.remover_item)
        self.btn_apagar_item.grid(row=2, column=0, pady=10)
        self.btn_apagar_item.grid_remove()

        btn_finalizar = tk.Button(self.frame_pedido, text="Finalizar Pedido", command=self.finalizar_pedido)
        btn_finalizar.grid(row=2, column=1, pady=10)

        self.btn_aumentar_quantidade = tk.Button(self.frame_pedido, image=self.icone_aumentar, command=self.aumentar_quantidade)
        self.btn_aumentar_quantidade.grid(row=2, column=2, pady=10)
        self.btn_aumentar_quantidade.grid_remove()

        # Configurar espaçamento automático entre os elementos
        self.frame_pedido.grid_columnconfigure(0, weight=1)
        self.frame_pedido.grid_columnconfigure(1, weight=1)
        self.frame_pedido.grid_columnconfigure(2, weight=1)

        # Ajustar botão de menu para alinhar com o título
        self.btn_menu = tk.Button(self.root, text="☰ Menu", command=self.abrir_menu_lateral, bg="#555555", fg="white", font=("Helvetica", 12))
        self.btn_menu.grid(row=0, column=0, sticky="nw", padx=5, pady=20)

    def mostrar_botoes_item(self, event=None):
        """Mostra os botões de apagar e aumentar quantidade quando um item é selecionado."""
        if self.lista_pedido.focus():
            self.btn_apagar_item.grid()
            self.btn_aumentar_quantidade.grid()
        else:
            self.btn_apagar_item.grid_remove()
            self.btn_aumentar_quantidade.grid_remove()



    def remover_item(self):
        """Remove o item selecionado do pedido."""
        item_selecionado = self.lista_pedido.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return

        indice = self.lista_pedido.index(item_selecionado)
        del self.pedido_atual[indice]
        self._atualizar_pedido()

    def aumentar_quantidade(self):
        """Aumenta a quantidade do item selecionado."""
        item_selecionado = self.lista_pedido.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para aumentar a quantidade.")
            return

        indice = self.lista_pedido.index(item_selecionado)
        item, preco, quantidade = self.pedido_atual[indice]
        self.pedido_atual[indice] = (item, preco, quantidade + 1)
        self._atualizar_pedido()

    def _atualizar_pedido(self):
        """Atualiza a visualização do pedido atual."""
        self.lista_pedido.delete(*self.lista_pedido.get_children())
        for item, preco, quantidade in self.pedido_atual:
            subtotal = preco * quantidade
            self.lista_pedido.insert("", tk.END, values=(item, quantidade, f"{subtotal:.2f}"))

    def finalizar_pedido(self):
        """Finaliza o pedido atual."""
        if not self.pedido_atual:
            messagebox.showwarning("Aviso", "Nenhum pedido registrado.")
            return

        data_hora = datetime.datetime.now()

        self.mc_fast_burguer.pedidos.append({"itens": self.pedido_atual[:], "status": "pendente", "data_hora": data_hora})

        total = sum(preco * quantidade for _, preco, quantidade in self.pedido_atual)
        self.pedido_atual.clear()
        self._atualizar_pedido()
        messagebox.showinfo("Pedido Finalizado", f"Total do pedido: R$ {total:.2f}")
    def gerar_relatorio(self):
            """Exibe o relatório de vendas e permite copiar o texto."""
            if not self.mc_fast_burguer.pedidos:
                messagebox.showinfo("Relatório", "Nenhum pedido foi registrado.")
                return

            # Gera o relatório com base nos pedidos
            relatorio = self.mc_fast_burguer.gerar_relatorio()

            # Cria uma nova janela para exibir o relatório
            relatorio_window = Toplevel(self.root)
            relatorio_window.title("Relatório de Vendas")

            # Campo de texto para exibir o relatório
            text_area = tk.Text(relatorio_window, wrap=tk.WORD, width=80, height=25)
            text_area.insert("1.0", relatorio)
            text_area.config(state=tk.DISABLED)  # Apenas leitura
            text_area.pack(padx=10, pady=10)

            # Função para copiar o texto do relatório
            def copiar_para_area_transferencia():
                self.root.clipboard_clear()
                self.root.clipboard_append(relatorio)
                self.root.update()  # Atualiza a área de transferência
                messagebox.showinfo("Copiado", "Relatório copiado para a área de transferência!")

            # Botão para copiar o relatório
            btn_copiar = tk.Button(relatorio_window, text="Copiar Relatório", command=copiar_para_area_transferencia)
            btn_copiar.pack(pady=5)

            # Botão para fechar a janela
            btn_fechar = tk.Button(relatorio_window, text="Fechar", command=relatorio_window.destroy)
            btn_fechar.pack(pady=5)



root = tk.Tk()
app = McFastBurguerApp(root)
root.mainloop()