# SpaceFactTester
# Link to demo: https://youtu.be/SayfkPpG6G4

A dynamic, full-stack, data-driven web application that transforms real-time astronomical data from the Le Système Solaire Open API into an interactive, gamified educational experience. 

The application features a responsive, context-aware multiple-choice trivia system powered by an adaptive difficulty engine. Users start their journey at an introductory baseline (Difficulty Level 1). For every correct answer, the backend scales the user up by one level to present more challenging cosmic data; for every incorrect answer, the difficulty drops by one level. 


The progression system dynamically caps between **Levels 1 and 4**, adjusting user paths without breaking the application state. 

It also displays the user's running session score (**+10 for success, -5 for failure**).

##  📂 File Structure
```text
space-fact-tester/
├── static/
│   ├── app.js
│   ├── bg.jpg
│   ├── bgasteroids.jpg
│   ├── milkyway.jpg
│   ├── nebula.jpg
│   └── surface.jpg
├── templates/
│   └── index.html
├── tests/
│   └── test_selenium.py
├── .gitignore
├── LICENSE
├── README.md
├── app.py
├── docker-compose.yml
├── requirements.txt
└── seed.py
```

## 🛠️ Technical Stack

### 🌐 Core Application & Storage
* **`app.py`** — The backbone of the application. It hosts the Flask server and implements a REST API framework. Database interactions are completely abstract and managed via an Object-Relational Mapper (ORM) using **Flask-SQLAlchemy** for efficient, structured data models without hardcoded SQL scripts.
* **`seed.py`** — An automated data ingestion and preprocessing pipeline. It is responsible for initializing the local or remote PostgreSQL database instance, handling relational entity constraints, and seeding the database with foundational mock mission profiles/data configurations.
* **`requirements.txt`** — The project's package manifest file, documenting specific versions of dependencies (like `Flask`, `Flask-SQLAlchemy`, and `psycopg2-binary`) for deterministic and reproducible environment builds across platforms.

### 📦 Containerization & Configuration
* **`docker-compose.yml`** — Defines the local development orchestration layer. It provisions an isolated **PostgreSQL 15** service volume container (`space_quiz_db`). 
    * It abstracts all authentication variables to prevent plain-text credential leaks.
    * Network exposure is explicitly bound to the loopback interface (`127.0.0.1`), eliminating unauthorized public Wi-Fi access vectors to the local database layer.
* **`.gitignore`** — ensures local build caches (`__pycache__`) and critical secret vaults (`.env`) are never indexed or committed to public version control.

### 🎨 Frontend UI Engine
* **`templates/index.html`** — The user interface rendering plane. It features a responsive, frosted-glass glassmorphism dashboard layout.
* **`static/` (Asset Directory)** — Houses client-side logic (`app.js`) and multimedia resources. 
    * *Cinematic Crossfading:* To bypass the browser's native limitation regarding abrupt `background-image` layout updates, the application utilizes an asynchronous JavaScript engine paired with a dual-layered overlapping CSS DOM layer (`#bg-overlay`). 

### 🧪 Quality Assurance
* **`tests/test_selenium.py`** — The automated End-to-End testing module. It utilizes WebDriver browser binaries to step through user navigation tracks, ensuring runtime functional testing across system states.

### 🛠️  Installation & Setup
Clone the repo: `git clone https://github.com/ricotti19/space-fact-tester.git`

Create a new file in the root directory named exactly `.env`.

Add your own local or cloud PostgreSQL connection string using the following format: `DATABASE_URL=your_postgresql_connection_string_here`

Make sure you have Python installed (version 3.10 or higher), then run: `pip install -r requirements.txt`

Initialize the database tables and populate them with baseline data by running: `python seed.py`

Last but not least, run: `python app.py`

Navigate browser to `http://127.0.0.1:5000`
