from quiz_questions import conduct_quiz, get_random_questions, questions_pool

if __name__ == "__main__":
    # Ask the user for the number of questions
    num_questions = int(input("Enter the number of questions for the test: "))
    
    # Validate input
    if num_questions > len(questions_pool):
        print("Not enough questions in the pool. Please choose a smaller number.")
    else:
        # Select random questions and start the quiz
        selected_questions = get_random_questions(questions_pool, num_questions)
        conduct_quiz(selected_questions)
