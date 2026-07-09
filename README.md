# Smart Authentication System using Behavioral Biometrics and Machine Learning

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A Flask-based behavioral biometric authentication system that strengthens traditional password authentication using **Keystroke Dynamics** and **Machine Learning**.

Instead of verifying only **what the user types**, the system also verifies **how the user types** by analyzing typing behavior such as **Hold Time**, **Flight Time**, and **Typing Speed**.

---

# Project Overview

Traditional authentication systems rely on passwords or OTPs, which can be stolen or shared. This project introduces an additional layer of security using **Behavioral Biometrics**, making authentication more resistant to unauthorized access.

The system captures typing behavior during login, compares it with the user's enrolled behavioral profile, and evaluates the login using:

- Similarity Score
- Isolation Forest Anomaly Detection
- Final Behavior Score
- Risk Classification

The project also performs **Continuous Session Verification**, ensuring that authentication continues throughout the active session rather than ending immediately after login.

---

# Features

- Secure User Registration
- Password Hashing using bcrypt
- Behavioral Profile Enrollment
- Keystroke Dynamics Analysis
- Hold Time Calculation
- Flight Time Calculation
- Typing Speed Analysis
- Similarity Score Calculation
- Isolation Forest Anomaly Detection
- Final Behavior Score
- Risk Classification (LOW / MEDIUM / HIGH)
- Continuous Session Verification
- Adaptive Profile Learning
- Interactive Dashboard
- Login History
- Behavior Analytics

---

# Technology Stack

| Technology   | Purpose            |
| ------------ | ------------------ |
| Python       | Core Programming   |
| Flask        | Backend Framework  |
| SQLite       | Database           |
| HTML5        | Frontend Structure |
| CSS3         | User Interface     |
| JavaScript   | Client-side Logic  |
| Scikit-learn | Machine Learning   |
| bcrypt       | Password Security  |

---

# Authentication Workflow

```
User Login
      │
      ▼
Capture Keystroke Features
(Hold Time, Flight Time, Typing Speed)
      │
      ▼
Similarity Score Calculation
      │
      ▼
Isolation Forest
      │
      ▼
Behavior Score
      │
      ▼
Risk Classification
      │
      ▼
Dashboard
      │
      ▼
Continuous Session Verification
      │
      ▼
Adaptive Profile Learning
```

---

# Behavioral Features

The system extracts the following behavioral characteristics:

- Hold Time
- Flight Time
- Typing Speed

These features collectively create a behavioral profile unique to each user.

---

# Machine Learning

The authentication decision combines:

- Similarity Score
- Isolation Forest Prediction
- ML Confidence
- Final Behavior Score

The calculated Behavior Score determines the session's risk level.

---

# Dashboard Features

The dashboard provides:

- Authentication Status
- Risk Level
- Hold Time
- Flight Time
- Typing Speed
- Behavior Match Score
- Login History
- Analytics Dashboard
- Continuous Session Verification

---

# Continuous Authentication

Unlike traditional authentication systems that verify users only once during login, this project continuously monitors user behavior throughout the active session.

The user is periodically asked to type a verification phrase.

The captured behavioral features are compared against the enrolled profile to:

- Verify session authenticity
- Detect anomalous behavior
- Update the live behavior score
- Classify session risk
- Trigger adaptive profile learning for successful low-risk sessions

---

# Adaptive Profile Learning

Successful low-risk verification sessions with behavior closely matching the enrolled profile are used to update the stored behavioral profile.

This enables the authentication system to gradually adapt to natural changes in the user's typing behavior while preventing anomalous sessions from influencing the enrolled profile.

---

# Project Structure

```
SmartAuthenticationSystem/
│
├── app.py
├── requirements.txt
├── database.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── model/
│
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/your-repository.git
```

Go into the project directory

```bash
cd your-repository
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

# Future Improvements

- Touchscreen Biometrics
- Gait Recognition
- Face Recognition Integration
- Deep Learning Models
- Cloud Deployment
- Multi-factor Authentication

---

# Author

**Divyanshu Anand**

Bachelor of Engineering

Electronics and Communication Engineering

---

# License

This project is developed for academic and educational purposes.
