# 🚀 Clarify – AI-Assisted Requirement Automation System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-black)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

> **Clarify** is a web-based AI-assisted Requirement Automation System that simplifies and improves the process of gathering, managing, and analyzing software requirements for both clients and requirement engineers.

---

## ✨ Key Highlights

✔ Streamlined requirement gathering
✔ Automatic categorization (Functional / Non-Functional / Uncertain)
✔ Secure user authentication
✔ Project-based requirement management
✔ Admin monitoring panel

---

## 📦 Features

### 👤 Role-Based System

* User & Admin authentication
* Secure login with encrypted passwords

### 📁 Project Management

* Create and manage multiple projects
* Isolated requirements per project

### 📝 Requirement Processing

* Requirement extraction
* Tokenization and keyword filtering
* Automatic classification

### 📊 Admin Panel

* View all projects
* Inspect requirements
* Monitor communication

---

## 🛠️ Tech Stack

### Backend

* **Python (Flask)**
* **MySQL**
* Flask-Bcrypt
* Regex-based NLP

### Frontend

* HTML5
* CSS3
* JavaScript

### Tools

* Postman
* phpMyAdmin

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/clarify.git
cd clarify
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install flask mysql-connector-python flask-bcrypt
```

### 4️⃣ Database Setup

Create database:

```sql
CREATE DATABASE requirement_automation;
```

Then create tables:

* users
* projects
* requirements
* messages

### 5️⃣ Run the Application

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 🔑 Core Routes

| Route           | Description     |
| --------------- | --------------- |
| /register_page  | Register user   |
| /login_page     | Login           |
| /ui             | User dashboard  |
| /dashboard      | Admin dashboard |
| /project/create | Create project  |
| /admin/projects | Admin view      |

---

## 🎯 Project Goal

To enhance the quality and efficiency of requirement engineering by:

* Reducing ambiguity
* Improving collaboration
* Automating classification
* Supporting structured documentation

---

## 🚧 Future Enhancements

* Smart Chatbot for Requirement Refinement
* Integration with project management tools (Jira, Trello)

---

## 👩‍💻 Author

**Aisha Noor**
Bachelor in Software Engineering – Bahria University Karachi Campus
Diploma in Software Engineering – Aptech

🔗 LinkedIn: https://www.linkedin.com/in/aisha-noor-3520062a6/

---

## 📄 License

This project is developed for academic purposes.
© 2026 – All Rights Reserved.

---
