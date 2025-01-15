import random
import time

def generate_question(question, options, correct_option):
    """
    Creates a question dictionary.
    """
    return {
        "question": question,
        "options": options,
        "correct_option": correct_option
    }

def get_random_questions(question_pool, count):
    """
    Randomly selects a given number of questions from the pool.
    """
    return random.sample(question_pool, count)

def conduct_quiz(questions):
    """
    Runs the quiz with a timer for each question.
    """
    correct_answers = 0
    total_questions = len(questions)

    print("\nWelcome to the Aptitude Test!")
    print(f"You will be answering {total_questions} questions. Each question has a 1-minute timer.\n")

    for idx, question in enumerate(questions, start=1):
        print(f"Question {idx}: {question['question']}")
        for i, option in enumerate(question["options"], start=1):
            print(f"{i}. {option}")

        start_time = time.time()
        try:
            user_choice = input("\nEnter your choice (1-4): ")
            elapsed_time = time.time() - start_time

            if elapsed_time > 60:
                print("Time's up! Moving to the next question.\n")
                continue

            if question["options"][int(user_choice) - 1] == question["correct_option"]:
                print("Correct!\n")
                correct_answers += 1
            else:
                print(f"Wrong! The correct answer is: {question['correct_option']}\n")
        except (ValueError, IndexError):
            print("Invalid choice! Moving to the next question.\n")

    print(f"\nQuiz Complete! You answered {correct_answers} out of {total_questions} questions correctly.")
