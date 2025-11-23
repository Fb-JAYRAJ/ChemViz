# ChemViz – Chemical Data Visualization System

ChemViz is a complete chemical-data analysis platform that allows users to upload CSV files, generate summaries, visualize trends, and export structured PDF reports.  
It contains three interconnected modules:

- **Django REST Backend**
- **React Web Client**
- **PyQt5 Desktop Client**

---

## 🚀 Features

### Backend (Django REST API)
- CSV upload & validation  
- Computes:
  - Total row count  
  - Average flowrate  
  - Average pressure  
  - Average temperature  
- Type distribution mapping  
- Stores analysis history  
- PDF report generation  
- Basic Authentication  

### Web Client (React.js)
- Modern dashboard  
- CSV upload  
- Summary metrics  
- Pie & Bar chart visualizations  
- History viewer  
- Smooth sidebar navigation  
- PDF export  

### Desktop Client (PyQt5)
- Local CSV upload  
- Summary panel  
- Embedded Matplotlib charts  
- History viewer  
- PDF download  

---

## 🧰 Tech Stack

**Backend:** Django, Django REST Framework  
**Frontend:** React.js, Chart.js  
**Desktop:** PyQt5, Matplotlib  
**Database:** SQLite  
**Auth:** Basic Auth  
**Utilities:** Axios, Requests, CORS  

---

## 📂 Project Structure
```
ChemViz/
│
├── Backend/                # Django backend
│   ├── chemviz_backend/    # Core backend project
│   ├── equipment/          # App for CSV processing & analysis
│   ├── db.sqlite3
│   ├── manage.py
│   └── ...
│
├── Frontend/               # React web client
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── Desktop/                # PyQt5 desktop application
│   └── main.py
│
├── env/                    # Python virtual environment
│
├── .gitignore
└── README.md
```
---

## ⚙️ Setup Instructions

### 1) Backend – Django

```sh
cd Backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Backend URL: http://127.0.0.1:8000

### 2) Frontend – React

```sh
cd Frontend
npm install
npm start
```
Frontend URL: http://localhost:3000

### 3) Desktop App – PyQt5
```sh
cd Desktop
python main.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/` | Upload CSV & process |
| GET  | `/api/summary/latest/` | Latest summary |
| GET  | `/api/history/` | All previous analyses |
| GET  | `/api/report/<id>/` | PDF download |

**Auth:** Basic Auth

# 👤Developed by: ***Jayraj Sawant***
