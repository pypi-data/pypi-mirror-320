from quiz_questions.core import generate_question

questions_pool = [
    generate_question("What is 5 + 3?", ["5", "6", "7", "8"], "8"),
    generate_question("If A = 1, B = 2, what is Z?", ["24", "25", "26", "27"], "26"),
    generate_question("What is the square root of 64?", ["6", "7", "8", "9"], "8"),
    generate_question("What is 12 * 12?", ["120", "144", "148", "132"], "144"),
    generate_question("Which number is prime?", ["4", "6", "9", "7"], "7"),
    generate_question("What is 100 ÷ 5?", ["20", "25", "15", "30"], "20"),
    generate_question("What is 15% of 200?", ["20", "25", "30", "35"], "30"),
    generate_question("What is 45 ÷ 3?", ["12", "15", "18", "21"], "15"),
    generate_question("What is 7 × 8?", ["54", "56", "58", "60"], "56"),
    generate_question("What is 9²?", ["72", "81", "64", "100"], "81"),
]
