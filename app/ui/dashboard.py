import tkinter as tk
from tkinter import ttk

from app.core.quiz import QuizEngine
from app.services.learning_service import get_lessons, get_quiz_bank


class EdulabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Edulab")
        self.root.geometry("1000x660")
        self.root.minsize(860, 560)

        self.lessons = get_lessons()
        self.quiz_bank = get_quiz_bank()
        self.quiz_engine = QuizEngine(self.quiz_bank)
        self.selected_lesson = 0

        self._build_ui()
        self._show_lesson(self.selected_lesson)
        self._show_question()

    def _build_ui(self):
        self.root.configure(bg="#f4f7fb")

        header = tk.Frame(self.root, bg="#1f4e79", padx=20, pady=18)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Edulab",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#1f4e79",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Learn, practice, and grow every day.",
            font=("Segoe UI", 11),
            fg="#eaf4ff",
            bg="#1f4e79",
        )
        subtitle.pack(anchor="w")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=14)

        self.home_tab = ttk.Frame(self.notebook)
        self.study_tab = ttk.Frame(self.notebook)
        self.quiz_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.study_tab, text="Study")
        self.notebook.add(self.quiz_tab, text="Quiz")

        self._build_home_tab()
        self._build_study_tab()
        self._build_quiz_tab()

    def _build_home_tab(self):
        intro = tk.Label(
            self.home_tab,
            text="Welcome back to your learning space",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
            justify="left",
            padx=20,
            pady=(18, 8),
        )
        intro.pack(fill="x")

        description = tk.Label(
            self.home_tab,
            text="Explore short lessons, gain confidence, and test your understanding with quick quizzes.",
            font=("Segoe UI", 11),
            wraplength=760,
            justify="left",
            padx=20,
            pady=(0, 18),
        )
        description.pack(fill="x")

        self.card_frame = tk.Frame(self.home_tab, bg="#f4f7fb")
        self.card_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for index, lesson in enumerate(self.lessons):
            card = tk.Frame(self.card_frame, bg="white", bd=1, relief="solid", padx=16, pady=14)
            card.grid(row=index // 3, column=index % 3, padx=12, pady=12, sticky="nsew")

            title = tk.Label(card, text=lesson["title"], font=("Segoe UI", 14, "bold"), bg="white")
            title.pack(anchor="w")

            subject = tk.Label(card, text=lesson["subject"], font=("Segoe UI", 10), fg="#4472a6", bg="white")
            subject.pack(anchor="w", pady=(2, 8))

            summary = tk.Label(
                card,
                text=lesson["summary"],
                font=("Segoe UI", 10),
                wraplength=220,
                justify="left",
                bg="white",
            )
            summary.pack(anchor="w", fill="x")

            button = tk.Button(
                card,
                text="Explore",
                command=lambda value=index: self._jump_to_study(value),
                bg="#2d7dd2",
                fg="white",
                activebackground="#2367b5",
                bd=0,
                padx=12,
                pady=6,
            )
            button.pack(anchor="w", pady=(14, 0))

            self.card_frame.grid_columnconfigure(0, weight=1)
            self.card_frame.grid_columnconfigure(1, weight=1)
            self.card_frame.grid_columnconfigure(2, weight=1)

    def _build_study_tab(self):
        left_panel = tk.Frame(self.study_tab, bg="#eef4fb")
        left_panel.pack(side="left", fill="y", padx=(12, 6), pady=12, ipadx=10)

        tk.Label(left_panel, text="Lessons", font=("Segoe UI", 14, "bold"), bg="#eef4fb").pack(anchor="w", padx=10, pady=(10, 8))

        self.lesson_list = tk.Listbox(left_panel, height=12, width=22, font=("Segoe UI", 10), activestyle="none")
        self.lesson_list.pack(fill="y", padx=10, pady=(0, 10), expand=True)
        self.lesson_list.bind("<<ListboxSelect>>", self._on_lesson_select)

        right_panel = tk.Frame(self.study_tab, padx=18, pady=18)
        right_panel.pack(side="left", fill="both", expand=True, padx=(6, 12), pady=12)

        self.lesson_title = tk.Label(right_panel, text="", font=("Segoe UI", 22, "bold"), anchor="w")
        self.lesson_title.pack(anchor="w", pady=(0, 8))

        self.lesson_subject = tk.Label(right_panel, text="", font=("Segoe UI", 11), fg="#4472a6")
        self.lesson_subject.pack(anchor="w")

        self.lesson_summary = tk.Label(
            right_panel,
            text="",
            font=("Segoe UI", 11),
            justify="left",
            wraplength=560,
        )
        self.lesson_summary.pack(anchor="w", pady=(12, 16))

        tk.Label(right_panel, text="Key ideas", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.lesson_facts = tk.Label(right_panel, text="", justify="left", wraplength=560)
        self.lesson_facts.pack(anchor="w", pady=(6, 16))

        tk.Label(right_panel, text="Activities", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.lesson_activities = tk.Label(right_panel, text="", justify="left", wraplength=560)
        self.lesson_activities.pack(anchor="w", pady=(6, 0))

        for index, lesson in enumerate(self.lessons):
            self.lesson_list.insert(index, lesson["title"])

    def _build_quiz_tab(self):
        self.quiz_frame = tk.Frame(self.quiz_tab, padx=24, pady=22)
        self.quiz_frame.pack(fill="both", expand=True)

        self.quiz_status = tk.Label(
            self.quiz_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            fg="#1a5e30",
            anchor="w",
        )
        self.quiz_status.pack(anchor="w", pady=(0, 10))

        self.question_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Segoe UI", 18, "bold"),
            wraplength=820,
            justify="left",
        )
        self.question_label.pack(anchor="w", fill="x", pady=(0, 16))

        self.answer_frame = tk.Frame(self.quiz_frame)
        self.answer_frame.pack(fill="both", expand=True)

        self.score_label = tk.Label(
            self.quiz_frame,
            text="Score: 0/0",
            font=("Segoe UI", 11, "bold"),
            fg="#2c3e50",
        )
        self.score_label.pack(anchor="e", pady=(20, 0))

    def _on_lesson_select(self, _event):
        selection = self.lesson_list.curselection()
        if selection:
            self._show_lesson(selection[0])

    def _show_lesson(self, lesson_index):
        lesson = self.lessons[lesson_index]
        self.selected_lesson = lesson_index
        self.lesson_title.config(text=lesson["title"])
        self.lesson_subject.config(text=f"Subject: {lesson['subject']}")
        self.lesson_summary.config(text=lesson["summary"])

        facts = "\n• ".join(lesson["facts"])
        activities = "\n• ".join(lesson["activities"])
        self.lesson_facts.config(text=f"• {facts}")
        self.lesson_activities.config(text=f"• {activities}")

        if self.lesson_list.size() > 0:
            self.lesson_list.selection_clear(0, self.lesson_list.size() - 1)
            self.lesson_list.select_set(lesson_index)

    def _jump_to_study(self, lesson_index):
        self.notebook.select(self.study_tab)
        self._show_lesson(lesson_index)

    def _show_question(self):
        question = self.quiz_engine.current_question()
        self.quiz_status.config(text="")

        if question is None:
            final_score = self.quiz_engine.score
            total = len(self.quiz_bank)
            self.question_label.config(text=f"Quiz complete! You scored {final_score} out of {total}.")
            self._clear_answer_buttons()
            self.score_label.config(text=f"Score: {final_score}/{total}")
            return

        self.question_label.config(text=f"Q{self.quiz_engine.current_index + 1}: {question['question']}")
        self.score_label.config(text=f"Score: {self.quiz_engine.score}/{len(self.quiz_bank)}")
        self._clear_answer_buttons()

        for option in question["options"]:
            button = tk.Button(
                self.answer_frame,
                text=option,
                command=lambda value=option: self._handle_answer(value),
                width=28,
                pady=8,
                font=("Segoe UI", 10),
                bg="#dfeaf7",
                activebackground="#cfe0f5",
                bd=1,
            )
            button.pack(anchor="w", pady=6)

    def _clear_answer_buttons(self):
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

    def _handle_answer(self, selected_answer):
        if self.quiz_engine.completed():
            return

        is_correct = self.quiz_engine.submit_answer(selected_answer)

        if is_correct:
            self.quiz_status.config(text="Correct! Nice work.", fg="#1a5e30")
        else:
            correct_answer = self.quiz_engine.questions[self.quiz_engine.current_index - 1]["answer"]
            self.quiz_status.config(text=f"Not quite — the correct answer is: {correct_answer}", fg="#9c3d2d")

        self._show_question()

    def reset_quiz(self):
        self.quiz_engine.reset()
        self.quiz_status.config(text="New quiz started.", fg="#1f4e79")
        self._show_question()


if __name__ == "__main__":
    root = tk.Tk()
    EdulabApp(root)
    root.mainloop()
