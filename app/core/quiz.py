class QuizEngine:
    def __init__(self, questions):
        self.questions = questions
        self.current_index = 0
        self.score = 0

    def current_question(self):
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def submit_answer(self, selected_answer):
        question = self.current_question()
        if question is None:
            return False

        is_correct = selected_answer == question["answer"]
        if is_correct:
            self.score += 1

        self.current_index += 1
        return is_correct

    def completed(self):
        return self.current_index >= len(self.questions)

    def reset(self):
        self.current_index = 0
        self.score = 0
