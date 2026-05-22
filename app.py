import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import random

# Load .env variables right at startup
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy 
db = SQLAlchemy(app)


# ----------------------------
# DATABASE MODEL
# ----------------------------
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    correct_answer = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)


# ----------------------------
# HELPER: CLEAN AND NORMALIZE STRINGS
# ----------------------------
def clean_value(val):
    """Turns '1.0' into '1', keeps floats like '9.8', and handles strings cleanly."""
    if val is None:
        return "0"
    val_str = str(val).strip()
    try:
        f_val = float(val_str)
        if f_val.is_integer():
            return str(int(f_val))
        return str(f_val)
    except ValueError:
        return val_str


# ----------------------------
# GET OPTIONS (CONTEXT-AWARE ORM MCQ BUILDER)
# ----------------------------
def get_options(correct_answer, question_text=""):
    correct_clean = clean_value(correct_answer)
    
    # Micro-targeted filtering to completely separate dates from names
    category_keyword = ""
    if "moons" in question_text.lower():
        category_keyword = "%moons%"
    elif "gravity" in question_text.lower():
        category_keyword = "%gravity%"
    elif "density" in question_text.lower():
        category_keyword = "%density%"
    elif "year" in question_text.lower() or "date" in question_text.lower():
        category_keyword = "%year%discovered%" if "discovered" in question_text.lower() else "%year%"
        if not category_keyword or category_keyword == "%year%": 
            category_keyword = "%date%"
    elif "astronomer" in question_text.lower() or "discovered the" in question_text.lower() or "who" in question_text.lower():
        category_keyword = "%astronomer%"
        if "who" in question_text.lower():
            category_keyword = "%which astronomer%"
    elif "orbit" in question_text.lower() or "days" in question_text.lower():
        category_keyword = "%orbit%"
    elif "rotation" in question_text.lower() or "hours" in question_text.lower():
        category_keyword = "%rotation%"
    elif "radius" in question_text.lower() or "size" in question_text.lower() or "kilometers" in question_text.lower():
        category_keyword = "%radius%"

    # ORM SELECT DISTINCT QUERY WITH CONTEXT FILTERING
    if category_keyword:
        query = db.session.query(Question.correct_answer).distinct().filter(
            Question.correct_answer != correct_answer,
            Question.question.like(category_keyword)
        ).limit(40)
    else:
        query = db.session.query(Question.correct_answer).distinct().filter(
            Question.correct_answer != correct_answer
        ).limit(40)

    db_wrong_answers = [clean_value(r[0]) for r in query.all()]
    random.shuffle(db_wrong_answers)

    # Use a set to prevent duplicate choices on frontend buttons
    options_set = {correct_clean}

    # Populate matching items with strict structural filters
    for wrong in db_wrong_answers:
        if len(options_set) >= 4:
            break
        
        # Stop text answers from leaking into number questions and vice versa
        is_correct_digit = correct_clean.replace(".", "", 1).isdigit()
        is_wrong_digit = wrong.replace(".", "", 1).isdigit()
        
        if is_correct_digit and not is_wrong_digit:
            continue  # Skip text strings if looking for a number
        if not is_correct_digit and is_wrong_digit:
            continue  # Skip numbers if looking for a textual name
            
        if wrong != correct_clean:
            options_set.add(wrong)

    # Intelligent Math Fallback System if database doesn't have 4 unique structural entries yet
    if len(options_set) < 4:
        try:
            if correct_clean.isdigit():
                base_num = int(correct_clean)
                attempts = 0
                if len(correct_clean) == 4 and correct_clean.startswith(("1", "2")):
                    while len(options_set) < 4 and attempts < 30:
                        options_set.add(str(base_num + random.choice([-40, -20, -10, 10, 20, 50])))
                        attempts += 1
                else:
                    while len(options_set) < 4 and attempts < 30:
                        options_set.add(str(max(0, base_num + random.choice([-3, -2, -1, 1, 2, 3, 5]))))
                        attempts += 1
            else:
                base_float = float(correct_clean)
                attempts = 0
                while len(options_set) < 4 and attempts < 30:
                    val = base_float + random.choice([-0.4, -0.2, 0.2, 0.4, 1.1])
                    options_set.add(f"{max(0.0, val):.1f}")
                    attempts += 1
        except ValueError:
            text_fallbacks = ["Unknown Astronomer", "International Team", "Ancient Observers", "None"]
            for item in text_fallbacks:
                if len(options_set) >= 4:
                    break
                if item != correct_clean:
                    options_set.add(item)

    # Turn back into a shuffled list for delivery
    options_list = list(options_set)
    random.shuffle(options_list)
    return options_list


# ----------------------------
# FRONTEND PAGE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# START QUIZ (FIRST QUESTION)
# ----------------------------
@app.route("/start", methods=["GET"])
def start():
    # ORM RANDOM SAMPLING
    all_ids = [q.id for q in db.session.query(Question.id).all()]
    if not all_ids:
        return jsonify({"error": "No questions found in database. Run seed.py first!"}), 500

    random_id = random.choice(all_ids)
    q = Question.query.get(random_id)

    return jsonify({
        "question_id": q.id,
        "question": q.question,
        "correct_answer": clean_value(q.correct_answer),
        "difficulty": q.difficulty,
        "options": get_options(q.correct_answer, q.question)
    })


# ----------------------------
# CHECK ANSWER + NEXT QUESTION
# ----------------------------
@app.route("/answer", methods=["POST"])
def answer():
    data = request.json

    question_id = data["question_id"]
    user_answer = clean_value(data["answer"])

    # ORM RECORD LOOKUP
    q = Question.query.get(question_id)
    if not q:
        return jsonify({"error": "Question not found"}), 404
        
    correct_clean = clean_value(q.correct_answer)
    correct = (user_answer == correct_clean)

    # Adaptive difficulty system
    new_difficulty = min(5, q.difficulty + 1) if correct else max(1, q.difficulty - 1)

    # ORM FILTER TIER POOL WITH RANDOM SAMPLING
    questions_pool = Question.query.filter_by(difficulty=new_difficulty).all()
    
    # Fallback to any random question if that specific difficulty tier is completely empty
    if not questions_pool:
        questions_pool = Question.query.all()

    next_q = random.choice(questions_pool)

    return jsonify({
        "correct": correct,
        "next_question": {
            "question_id": next_q.id,
            "question": next_q.question,
            "correct_answer": clean_value(next_q.correct_answer),
            "difficulty": next_q.difficulty,
            "options": get_options(next_q.correct_answer, next_q.question)
        }
    })


# ----------------------------
# RUN SERVER
# ----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)