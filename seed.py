import os
import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded BEFORE importing the app configuration
load_dotenv()

from app import app, db, Question  # Import the app, db instance, and Question model

API_URL = "https://api.le-systeme-solaire.net/rest.php/bodies?data=englishName,gravity,density,moons,discoveredBy,discoveryDate,sideralOrbit,sideralRotation,meanRadius"
API_KEY = os.getenv('API_KEY')


def generate_questions(body):
    questions = []
    name = body.get("englishName")
    if not name:
        return questions

    gravity = body.get("gravity")
    density = body.get("density")
    moons = body.get("moons")
    discovered_by = body.get("discoveredBy")
    discovery_date = body.get("discoveryDate")
    orbit = body.get("sideralOrbit")
    rotation = body.get("sideralRotation")
    radius = body.get("meanRadius")

    # --- Moons ---
    # Only make sense to ask how many moons a body has if it isn't a tiny moon itself
    if moons is not None or density is not None:
        moon_count = len(moons) if moons else 0
        questions.append(Question(
            question=f"How many moons does {name} have?", 
            correct_answer=str(moon_count), 
            difficulty=1
        ))

    # --- Gravity ---
    if gravity is not None:
        questions.append(Question(
            question=f"What is the surface gravity of {name} in m/s²?", 
            correct_answer=str(gravity), 
            difficulty=2
        ))

    # --- Density ---
    if density is not None:
        questions.append(Question(
            question=f"What is the density of {name} in g/cm³?", 
            correct_answer=str(density), 
            difficulty=3
        ))

    # --- Discovery History ---
    if discovered_by:
        questions.append(Question(
            # Dynamic text adjustment so it doesn't call a moon a "planet"
            question=f"Which astronomer discovered the celestial body {name}?", 
            correct_answer=str(discovered_by), 
            difficulty=4
        ))
    if discovery_date:
        questions.append(Question(
            question=f"In what year or date was {name} officially discovered?", 
            correct_answer=str(discovery_date), 
            difficulty=3
        ))

    # --- Orbit Safety Patch ---
    if orbit is not None:
        try:
            year_len = round(float(orbit))
            if year_len != 0:
                questions.append(Question(
                    question=f"How many Earth days does it take for {name} to complete one orbit (a year)?", 
                    correct_answer=str(year_len), 
                    difficulty=3
                ))
        except (ValueError, TypeError):
            pass 

    # --- Rotation Safety Patch ---
    if rotation is not None:
        try:
            day_len = round(abs(float(rotation)), 1)
            if day_len != 0:
                questions.append(Question(
                    question=f"How many Earth hours does one sidereal rotation (a day) take on {name}?", 
                    correct_answer=str(day_len), 
                    difficulty=4
                ))
        except (ValueError, TypeError):
            pass

    # --- Size (Radius) Safety Patch ---
    if radius is not None:
        try:
            questions.append(Question(
                question=f"What is the mean radius of {name} in kilometers?", 
                correct_answer=str(round(float(radius))), 
                difficulty=2
            ))
        except (ValueError, TypeError):
            pass

    return questions


def main():
    print("Fetching expanded solar system data...")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print("Error fetching data:", response.text[:200])
            return
        data = response.json()
    except Exception as e:
        print(f"Network error: {e}")
        return

    bodies = data.get("bodies", [])

    with app.app_context():
        print("Wiping old simple questions using ORM drop controls...")
        db.drop_all()
        db.create_all()

        inserted = 0
        for body in bodies:
            questions = generate_questions(body)
            for q in questions:
                db.session.add(q)
                inserted += 1

        db.session.commit()

    print(f"✅ Awesome! Inserted {inserted} diverse quiz questions into the database using SQLAlchemy ORM!")


if __name__ == "__main__":
    main()