# 🏋️ Trainify – Personal Trainer Dashboard

**Trainify** is a full-stack web application that enables personal trainers to manage clients, generate personalised workout and meal plans, and track progress — all in one place. The platform uses automation and data-driven features to help trainers focus on coaching, not admin.

---

## 🚀 Features

- Trainer and client login
- Optimised **meal plan** generator (based on macronutrient needs)
- Automatic **workout plan** generation with equipment/muscle filters
- **Recommender system** to suggest effective plans using K Nearest Neighbours
- Weight tracking and graphical insights
- Trainer notes for workouts and meals
- Built with Django (backend) and Vue (frontend)

---

## 🧰 Prerequisites

- Python 3.11+  
- Node.js (v16+ recommended)  
- npm (comes with Node)  

---

## 🔧 Getting Started

1. Clone this repository:  
   `git clone https://github.com/Ehsaan04/Trainify.git`

2. Navigate into the project folder:  
   `cd Trainify`

3. Follow the setup instructions below for setting up the backend and frontend.


---

## ⚙️ Setup Instructions

### 🛠️ Backend
1. Open a terminal
2. Create and activate a virtual environment:
   If using venv (standard Python):
   * Run: python -m venv venv
   * On Windows: venv\Scripts\activate
   * On macOS/Linux: source venv/bin/activate

   If using conda:
   * Run: conda create -n trainify python=3.11
   * Then: conda activate trainify

3. Install dependencies: pip install -r requirements.txt
4. Navigate into the backend folder: cd backend
5. Start the Django server: python manage.py runserver

### 🎨 Frontend
1. Open a second terminal
2. Navigate into frontend folder with cd Trainify followed by cd frontend
3. Run: npm install
4. Run: npm run dev
5. Keep this terminal open

### 🌐 Access the App
Once both servers are running, visit:
http://127.0.0.1:8000


## 👥 Demo Accounts
### 🔐 Trainer Login
Username: alexTrainer

Password: testpass123

### 👤 Client Login
Username: danielr

Password: testpass123

### 📦 Included Demo Data
This repository includes a pre-seeded db.sqlite3 database with:

* Trainer and client profiles

* Pre-generated meal/workout plans

* Sample ratings for recommender demo

* ✅ No real user data included.

### 📝 License
This project is intended for educational and demonstration purposes. A license will be added when the project is made public.

### 🙌 Acknowledgements
Built using Django, Vue, Pandas, PuLP, scikit-learn

Powered by PuLP, pandas, and data from Nutritionix API

---