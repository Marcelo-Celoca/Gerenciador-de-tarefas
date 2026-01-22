import customtkinter as ctk
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerenciador de Tarefas")
        self.geometry("500x650")
        self.filename = "tarefas.json"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Painel de Status
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Tarefas: 0 | Concluídas: 0 (0%)", font=("Roboto", 14))
        self.stats_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.stats_frame, width=400)
        self.progress_bar.set(0)  # Começa vazia
        self.progress_bar.pack(pady=5)

        self.label = ctk.CTkLabel(self, text="Minhas Tarefas", font=("Roboto", 24, "bold"))
        self.label.grid(row=1, column=0, padx=20, pady=10)

        # ENTRADA DE DADOS
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.entry_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="O que precisa ser feito?")
        self.task_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Atalho: Carregar 'Enter' também adiciona a tarefa
        self.task_entry.bind("<Return>", lambda event: self.add_task_button_clicked())

        self.add_button = ctk.CTkButton(self.entry_frame, text="Adicionar", command=self.add_task_button_clicked)
        self.add_button.grid(row=0, column=1)

        # LISTA DE TAREFAS (Scrollable Frame)
        self.tasks_list = ctk.CTkScrollableFrame(self, label_text="Lista de Afazeres")
        self.tasks_list.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # LISTA PARA ARMAZENAR AS REFERÊNCIAS DOS COMPONENTES (checkboxes)
        self.tasks_data_widgets = []

        # Botão Limpar Concluídas
        self.clear_button = ctk.CTkButton(
            self,
            text="Limpar todas as concluídas",
            fg_color="transparent",
            border_width=2,
            hover_color="#ff4d4d",
            command=self.clear_completed
        )
        self.clear_button.grid(row=4, column=0, padx=20, pady=20)

        # Carregar dados ao iniciar
        self.load_tasks()

    def update_stats(self):
        """Calcula o progresso e atualiza a barra e o texto."""
        total = len(self.tasks_data_widgets)
        concluidas = sum(1 for t in self.tasks_data_widgets if t["variable"].get())
        percentual = (concluidas / total) if total > 0 else 0

        # Atualiza o texto
        self.stats_label.configure(
            text=f"Tarefas: {total} | Concluídas: {concluidas} ({int(percentual * 100)}%)"
        )
        # Atualiza a barra (recebe valor de 0.0 a 1.0)
        self.progress_bar.set(percentual)

    def add_task_button_clicked(self):
        text = self.task_entry.get()
        if text.strip() != "":
            self.create_task_row(text, completed=False)
            self.task_entry.delete(0, 'end')
            self.save_tasks()
            self.update_stats()  # Atualiza após adicionar

    def create_task_row(self, text, completed):
        task_frame = ctk.CTkFrame(self.tasks_list)
        task_frame.pack(fill="x", pady=5, padx=5)

        check_var = ctk.BooleanVar(value=completed)
        check = ctk.CTkCheckBox(
            task_frame,
            text=text,
            variable=check_var,
            command=self.on_check_clicked  # Função para salvar e atualizar stats
        )
        check.pack(side="left", padx=10, pady=5)

        # Botão de remover
        delete_btn = ctk.CTkButton(
            task_frame,
            text="X",
            width=30,
            fg_color="#ff4d4d",
            hover_color="#cc0000",
            command=lambda tf=task_frame: self.remove_task(tf)
        )
        delete_btn.pack(side="right", padx=10)

        self.tasks_data_widgets.append({"frame": task_frame, "text": text, "variable": check_var})

    def on_check_clicked(self):
        """Chamado sempre que um checkbox é marcado/desmarcado."""
        self.save_tasks()
        self.update_stats()

    def remove_task(self, task_frame):
        # Remove da lista de widgets
        self.tasks_data_widgets = [t for t in self.tasks_data_widgets if t["frame"] != task_frame]
        task_frame.destroy()
        self.save_tasks()
        self.update_stats()

    def clear_completed(self):
        """Remove todas as tarefas que estão marcadas como concluídas"""
        for item in self.tasks_data_widgets[:]:
            if item["variable"].get():
                item["frame"].destroy()
                self.tasks_data_widgets.remove(item)
        self.save_tasks()
        self.update_stats()

    def save_tasks(self):
        data_to_save = [{"text": i["text"], "completed": i["variable"].get()} for i in self.tasks_data_widgets]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def load_tasks(self):
        """Lê o ficheiro JSON e reconstrói a lista de tarefas."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    tasks = json.load(f)
                    for task in tasks:
                        self.create_task_row(task["text"], task["completed"])
                self.update_stats()
            except Exception as e:
                print(f"Erro ao carregar tarefas: {e}")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
