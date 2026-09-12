import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

from app.core.chatbot import RAGChatbot
from app.core.quiz import QuizEngine
from app.core.settings import load_settings, update_settings
from app.data.lessons import QUIZ_BANK
from app.services.learning_service import get_lessons
from app.services.auth_service import get_user_progress, save_progress
from app.services.pdf_indexer import get_indexed_documents, index_pdf_text
from app.tools.calculator import evaluate_expression
from app.tools.chemistry_tools import ideal_gas_law, molar_mass, percent_composition
from app.tools.document_editor import char_count, summarize_notes, word_count
from app.tools.formula_sheet import get_formula_group
from app.tools.image_reader import image_summary
from app.tools.math_engine import derivative_polynomial, matrix_determinant, solve_quadratic
from app.tools.pdf_reader import read_pdf_text
from app.tools.periodic_table import get_element
from app.tools.physics_engine import MotionEquations, ProjectileMotion, ResistiveCircuit
from app.tools.physics_simulator import projectile_metrics


class MainApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.lessons = get_lessons()
        self.quiz_engine = QuizEngine(QUIZ_BANK)
        self.settings = load_settings()
        self.chatbot = RAGChatbot(self.lessons)
        self.root.title(f"Edulab - {user['full_name']}")
        self.root.geometry("1200x760")
        self.root.minsize(980, 640)
        self._apply_theme()

        self._build_ui()
        self._show_lesson(0)
        self._show_question()
        self._load_progress()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#1f4e79", padx=20, pady=18)
        header.pack(fill="x")

        title = tk.Label(header, text="Edulab", font=("Segoe UI", 28, "bold"), fg="white", bg="#1f4e79")
        title.pack(anchor="w")

        sub = tk.Label(header, text=f"Welcome, {self.user['full_name']} | Learning dashboard", font=("Segoe UI", 11), fg="#eaf4ff", bg="#1f4e79")
        sub.pack(anchor="w")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=14)

        self.home_tab = ttk.Frame(self.notebook)
        self.study_tab = ttk.Frame(self.notebook)
        self.quiz_tab = ttk.Frame(self.notebook)
        self.chat_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.study_tab, text="Study")
        self.notebook.add(self.quiz_tab, text="Quiz")
        self.notebook.add(self.chat_tab, text="AI Tutor")
        self.notebook.add(self._build_tools_tab(), text="Tools")
        self.notebook.add(self._build_settings_tab(), text="Settings")

        self._build_home_tab()
        self._build_study_tab()
        self._build_quiz_tab()
        self._build_chat_tab()

    def _build_home_tab(self):
        label = tk.Label(self.home_tab, text="Your learning path", font=("Segoe UI", 20, "bold"), anchor="w", padx=20, pady=(20, 8))
        label.pack(fill="x")

        container = tk.Frame(self.home_tab)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for index, lesson in enumerate(self.lessons):
            card = tk.Frame(container, bg="white", bd=1, relief="solid", padx=14, pady=14)
            card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")
            tk.Label(card, text=lesson["title"], font=("Segoe UI", 15, "bold"), bg="white").pack(anchor="w")
            tk.Label(card, text=lesson["subject"], font=("Segoe UI", 10), fg="#4574a8", bg="white").pack(anchor="w", pady=(2, 6))
            tk.Label(card, text=lesson["summary"], font=("Segoe UI", 10), wraplength=220, justify="left", bg="white").pack(anchor="w", fill="x")
            tk.Button(card, text="Open lesson", command=lambda value=index: self._open_lesson(value), bg="#2d7dd2", fg="white", padx=12, pady=6).pack(anchor="w", pady=(12, 0))

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)

    def _build_study_tab(self):
        left = tk.Frame(self.study_tab, bg="#eef4fb")
        left.pack(side="left", fill="y", padx=(12, 6), pady=12, ipadx=10)

        tk.Label(left, text="Lessons", font=("Segoe UI", 15, "bold"), bg="#eef4fb").pack(anchor="w", padx=10, pady=(10, 8))
        self.lesson_list = tk.Listbox(left, width=24, height=14, font=("Segoe UI", 10), activestyle="none")
        self.lesson_list.pack(fill="y", padx=10, expand=True)
        self.lesson_list.bind("<<ListboxSelect>>", self._on_lesson_select)

        for index, lesson in enumerate(self.lessons):
            self.lesson_list.insert(index, lesson["title"])

        right = tk.Frame(self.study_tab, padx=18, pady=18)
        right.pack(side="left", fill="both", expand=True, padx=(6, 12), pady=12)

        self.lesson_title = tk.Label(right, text="", font=("Segoe UI", 22, "bold"), anchor="w")
        self.lesson_title.pack(anchor="w", pady=(0, 8))
        self.lesson_subject = tk.Label(right, text="", font=("Segoe UI", 11), fg="#4777b5")
        self.lesson_subject.pack(anchor="w")
        self.lesson_summary = tk.Label(right, text="", wraplength=560, justify="left", font=("Segoe UI", 11))
        self.lesson_summary.pack(anchor="w", pady=(14, 16))

        tk.Label(right, text="Key ideas", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.lesson_facts = tk.Label(right, text="", justify="left", wraplength=600)
        self.lesson_facts.pack(anchor="w", pady=(6, 16))

        tk.Label(right, text="Suggested activities", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.lesson_activities = tk.Label(right, text="", justify="left", wraplength=600)
        self.lesson_activities.pack(anchor="w", pady=(6, 0))

    def _build_quiz_tab(self):
        self.quiz_frame = tk.Frame(self.quiz_tab, padx=20, pady=20)
        self.quiz_frame.pack(fill="both", expand=True)

        self.quiz_status = tk.Label(self.quiz_frame, text="", font=("Segoe UI", 11, "bold"), fg="#156a46", anchor="w")
        self.quiz_status.pack(anchor="w", pady=(0, 12))

        self.question_label = tk.Label(self.quiz_frame, text="", font=("Segoe UI", 18, "bold"), wraplength=900, justify="left")
        self.question_label.pack(anchor="w", fill="x", pady=(0, 14))

        self.answer_frame = tk.Frame(self.quiz_frame)
        self.answer_frame.pack(fill="both", expand=True)

        self.score_label = tk.Label(self.quiz_frame, text="Score: 0/0", font=("Segoe UI", 11, "bold"), fg="#334d66")
        self.score_label.pack(anchor="e", pady=(18, 0))

        self.restart_button = tk.Button(self.quiz_frame, text="Restart quiz", command=self.reset_quiz, bg="#edf4ff", fg="#1f4e79", font=("Segoe UI", 10, "bold"))
        self.restart_button.pack(anchor="e", pady=(8, 0))

    def _build_chat_tab(self):
        chat_panel = tk.Frame(self.chat_tab, padx=18, pady=18)
        chat_panel.pack(fill="both", expand=True)

        tk.Label(chat_panel, text="Ask your AI tutor", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 12))
        self.chat_output = scrolledtext.ScrolledText(chat_panel, wrap=tk.WORD, width=120, height=20, font=("Segoe UI", 10))
        self.chat_output.pack(fill="both", expand=True)
        self.chat_output.insert(tk.END, "Edulab tutor ready. Ask about a lesson, concept, or homework question.\n\n")
        self.chat_output.configure(state="disabled")

        input_frame = tk.Frame(chat_panel)
        input_frame.pack(fill="x", pady=(12, 0))

        self.chat_input = tk.Entry(input_frame, font=("Segoe UI", 11))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", self._ask_chatbot)

        tk.Button(input_frame, text="Send", command=self._ask_chatbot, bg="#2d7dd2", fg="white", font=("Segoe UI", 10, "bold"), padx=16, pady=8).pack(side="right")

    def _build_settings_tab(self):
        settings_tab = ttk.Frame(self.notebook)
        panel = tk.Frame(settings_tab, padx=24, pady=18)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Settings", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 18))

        self.settings = load_settings()
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        self.accent_var = tk.StringVar(value=self.settings.get("accent", "#2d7dd2"))
        self.web_search_var = tk.BooleanVar(value=self.settings.get("web_search", True))
        self.rag_var = tk.BooleanVar(value=self.settings.get("rag_enabled", True))
        self.pdf_index_var = tk.BooleanVar(value=self.settings.get("pdf_indexing", True))

        tk.Label(panel, text="Theme:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Combobox(panel, textvariable=self.theme_var, values=["light", "dark", "blue"], state="readonly", width=20).pack(anchor="w", pady=(0, 12))

        tk.Label(panel, text="Accent color:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Entry(panel, textvariable=self.accent_var, width=20, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 12))

        tk.Checkbutton(panel, text="Enable web search", variable=self.web_search_var, onvalue=True, offvalue=False).pack(anchor="w")
        tk.Checkbutton(panel, text="Enable local RAG context", variable=self.rag_var, onvalue=True, offvalue=False).pack(anchor="w")
        tk.Checkbutton(panel, text="Enable PDF indexing", variable=self.pdf_index_var, onvalue=True, offvalue=False).pack(anchor="w")

        tk.Button(panel, text="Save settings", command=self._save_settings, bg="#2d7dd2", fg="white", font=("Segoe UI", 10, "bold"), padx=18, pady=8).pack(anchor="w", pady=(18, 0))
        return settings_tab

    def _build_tools_tab(self):
        tools_tab = ttk.Frame(self.notebook)

        main = tk.Frame(tools_tab, padx=18, pady=18)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="Academic tools", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 12))

        tools = [
            ("Calculator", self._show_calculator_tool),
            ("Periodic Table", self._show_periodic_table_tool),
            ("Physics Simulator", self._show_physics_tool),
            ("Formula Sheet", self._show_formula_sheet),
            ("Circuit Helper", self._show_circuit_helper),
            ("Motion Helper", self._show_motion_helper),
            ("Chemistry Helper", self._show_chemistry_helper),
            ("Math Engine", self._show_equation_helper),
            ("Matrix Tool", self._show_math_matrix_helper),
            ("Document Editor", self._show_document_tool),
            ("PDF Reader", self._show_pdf_tool),
            ("Image Reader", self._show_image_tool),
        ]

        for index, (name, action) in enumerate(tools):
            column = index % 3
            row = index // 3
            button = tk.Button(main, text=name, width=22, height=2, command=action, bg="#dfeaf7", font=("Segoe UI", 10, "bold"))
            button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=1)

        return tools_tab

    def _apply_theme(self):
        theme = self.settings.get("theme", "light")
        accent = self.settings.get("accent", "#2d7dd2")
        if theme == "dark":
            self.root.configure(bg="#101820")
        elif theme == "blue":
            self.root.configure(bg="#dfeaf7")
        else:
            self.root.configure(bg="#f3f7fb")
        self.accent_color = accent

    def _save_settings(self):
        settings = update_settings({
            "theme": self.theme_var.get(),
            "accent": self.accent_var.get(),
            "web_search": self.web_search_var.get(),
            "rag_enabled": self.rag_var.get(),
            "pdf_indexing": self.pdf_index_var.get(),
        })
        self.settings = settings
        self._apply_theme()
        messagebox.showinfo("Settings saved", f"Settings saved successfully.\nTheme: {settings['theme']}")

    def _show_calculator_tool(self):
        expression = simpledialog.askstring("Calculator", "Enter an expression (e.g. sin(pi/2) + 10)")
        if not expression:
            return
        try:
            result = evaluate_expression(expression)
            messagebox.showinfo("Calculator result", f"Result: {result}")
        except ValueError as exc:
            messagebox.showerror("Calculator error", str(exc))

    def _show_periodic_table_tool(self):
        symbol = simpledialog.askstring("Periodic Table", "Enter element symbol (e.g. H, Fe, O)")
        if not symbol:
            return
        element = get_element(symbol)
        if not element:
            messagebox.showerror("Element not found", "Element not found in the basic table.")
            return
        details = f"Symbol: {symbol.upper()}\nAtomic Number: {element['number']}\nAtomic Mass: {element['mass']}\nGroup: {element['group']}"
        messagebox.showinfo("Element info", details)

    def _show_physics_tool(self):
        velocity = simpledialog.askfloat("Physics simulator", "Initial velocity (m/s)")
        angle = simpledialog.askfloat("Physics simulator", "Angle (degrees)")
        if velocity is None or angle is None:
            return
        result = projectile_metrics(velocity, angle)
        messagebox.showinfo("Projectile results", "\n".join(f"{key}: {value}" for key, value in result.items()))

    def _show_document_tool(self):
        text = simpledialog.askstring("Document editor", "Paste text to analyze")
        if text is None:
            return
        summary = summarize_notes(text)
        stats = f"Words: {word_count(text)}\nCharacters: {char_count(text)}\n\nSummary:\n{summary}"
        messagebox.showinfo("Document analysis", stats)

    def _show_pdf_tool(self):
        path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        try:
            text = read_pdf_text(path)
            if load_settings().get("pdf_indexing", True):
                index_pdf_text(path, text)
            messagebox.showinfo("PDF reader", text)
        except Exception as exc:
            messagebox.showerror("PDF error", str(exc))

    def _show_image_tool(self):
        path = filedialog.askopenfilename(title="Select image file", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp")])
        if not path:
            return
        try:
            info = image_summary(path)
            messagebox.showinfo("Image info", "\n".join(f"{key}: {value}" for key, value in info.items()))
        except Exception as exc:
            messagebox.showerror("Image error", str(exc))

    def _show_formula_sheet(self):
        group = simpledialog.askstring("Formula sheet", "Enter group: physics / chemistry / math")
        if not group:
            return
        formulas = get_formula_group(group)
        if not formulas:
            messagebox.showerror("Formula group not found", "Use physics, chemistry, or math.")
            return
        messagebox.showinfo("Formula sheet", "\n".join(f"{name}: {value}" for name, value in formulas.items()))

    def _show_equation_helper(self):
        a = simpledialog.askfloat("Quadratic equation", "a value")
        b = simpledialog.askfloat("Quadratic equation", "b value")
        c = simpledialog.askfloat("Quadratic equation", "c value")
        if a is None or b is None or c is None:
            return
        result = solve_quadratic(a, b, c)
        if result is None:
            messagebox.showinfo("Quadratic formula", "No real roots found for this equation.")
            return
        messagebox.showinfo("Quadratic formula", f"Roots: {result}")

    def _show_chemistry_helper(self):
        formula = simpledialog.askstring("Chemistry helper", "Enter molecular formula, e.g. H2O")
        if not formula:
            return
        try:
            molar = molar_mass(formula)
            messagebox.showinfo("Chemistry helper", f"Molar mass of {formula}: {molar} g/mol")
        except Exception as exc:
            messagebox.showerror("Chemistry helper", str(exc))

    def _show_circuit_helper(self):
        values = simpledialog.askstring("Resistance simulator", "Enter resistor values separated by commas, e.g. 10,20,30")
        if not values:
            return
        try:
            resistors = [float(v.strip()) for v in values.split(",") if v.strip()]
            circuit = ResistiveCircuit(resistors)
            response = (
                f"Series: {circuit.series_resistance()}\n"
                f"Parallel: {circuit.parallel_resistance()}"
            )
            messagebox.showinfo("Circuit results", response)
        except Exception as exc:
            messagebox.showerror("Circuit helper", str(exc))

    def _show_motion_helper(self):
        velocity = simpledialog.askfloat("Motion helper", "Initial velocity (m/s)")
        angle = simpledialog.askfloat("Motion helper", "Launch angle (degrees)")
        if velocity is None or angle is None:
            return
        motion = ProjectileMotion(velocity, angle)
        messagebox.showinfo("Motion results", f"Time: {motion.time_of_flight()}\nRange: {motion.range()}\nMax height: {motion.max_height()}")

    def _show_math_matrix_helper(self):
        try:
            a = simpledialog.askstring("Matrix determinant", "Enter 2x2 matrix as a,b;c,d")
            if not a:
                return
            parts = [item.strip() for item in a.split(";")]
            matrix = [[float(cell) for cell in row.split(",")] for row in parts]
            messagebox.showinfo("Determinant", f"Determinant: {matrix_determinant(matrix)}")
        except Exception as exc:
            messagebox.showerror("Matrix error", str(exc))

    def _open_lesson(self, index):
        self.notebook.select(self.study_tab)
        self._show_lesson(index)

    def _on_lesson_select(self, event):
        selection = self.lesson_list.curselection()
        if selection:
            self._show_lesson(selection[0])

    def _show_lesson(self, lesson_index):
        lesson = self.lessons[lesson_index]
        self.lesson_title.config(text=lesson["title"])
        self.lesson_subject.config(text=f"Subject: {lesson['subject']}")
        self.lesson_summary.config(text=lesson["summary"])
        self.lesson_facts.config(text="\n• ".join(lesson["facts"]))
        self.lesson_activities.config(text="\n• ".join(lesson["activities"]))
        self.lesson_list.selection_clear(0, self.lesson_list.size() - 1)
        self.lesson_list.select_set(lesson_index)

    def _show_question(self):
        question = self.quiz_engine.current_question()
        self.quiz_status.config(text="")

        if question is None:
            self.question_label.config(text=f"Quiz complete! You scored {self.quiz_engine.score} out of {len(QUIZ_BANK)}.")
            self._clear_answer_buttons()
            self.score_label.config(text=f"Score: {self.quiz_engine.score}/{len(QUIZ_BANK)}")
            self._save_quiz_result()
            return

        self.question_label.config(text=f"Q{self.quiz_engine.current_index + 1}: {question['question']}")
        self.score_label.config(text=f"Score: {self.quiz_engine.score}/{len(QUIZ_BANK)}")
        self._clear_answer_buttons()

        for option in question["options"]:
            tk.Button(
                self.answer_frame,
                text=option,
                command=lambda value=option: self._handle_answer(value),
                width=35,
                pady=8,
                bg="#dfeaf7",
                activebackground="#cfe0f5",
                font=("Segoe UI", 10),
                bd=1,
            ).pack(anchor="w", pady=5)

    def _clear_answer_buttons(self):
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

    def _handle_answer(self, selected_answer):
        if self.quiz_engine.completed():
            return

        is_correct = self.quiz_engine.submit_answer(selected_answer)
        if is_correct:
            self.quiz_status.config(text="Correct! Nice work.", fg="#156a46")
        else:
            correct = self.quiz_engine.questions[self.quiz_engine.current_index - 1]["answer"]
            self.quiz_status.config(text=f"Incorrect. The correct answer is: {correct}", fg="#9d3d2d")
        self._show_question()

    def reset_quiz(self):
        self.quiz_engine.reset()
        self.quiz_status.config(text="Quiz restarted.", fg="#1f4e79")
        self._show_question()

    def _save_quiz_result(self):
        subject = "General Learning"
        save_progress(self.user["id"], subject, self.quiz_engine.score, len(QUIZ_BANK), ["quiz"])

    def _load_progress(self):
        progress = get_user_progress(self.user["id"])
        if progress:
            summary = "\n".join(f"{item['subject']}: {item['score']}/{item['total']}" for item in progress)
            messagebox.showinfo("Progress", f"Your saved learning progress:\n\n{summary}")

    def _ask_chatbot(self, event=None):
        query = self.chat_input.get().strip()
        if not query:
            return

        self.chat_input.delete(0, tk.END)
        self.chat_output.configure(state="normal")
        self.chat_output.insert(tk.END, f"You: {query}\n\n")
        self.chat_output.see(tk.END)

        response = self.chatbot.generate_response(query)
        self.chat_output.insert(tk.END, f"Tutor: {response}\n\n")
        self.chat_output.configure(state="disabled")
        self.chat_output.see(tk.END)
