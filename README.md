# 🗳️ Online Election Management System

An end-to-end secure, role-based online election management platform built using **Django**, designed for institutions and organizations to conduct smooth and transparent elections. This system supports admin-controlled workflows, OTP-based voter verification, secure voting logic, and result analytics.

---

## 🎯 Objectives
- To develop a secure, transparent, and user-friendly election system.
- To allow eligible users to register as voters or candidates.
- To manage and track elections efficiently through an admin panel.
- To automate the process of voting and result tabulation.

---
## 🚀 Features

- 🔐 **Secure Registration & OTP Verification** (SMS-based via SMSChef)
- 🧑‍💼 **Role-Based Access Control** for Admins, Voters, and Candidates
- 📩 **Email & SMS Notifications** (e.g., registration, voting, result)
- 🗳️ **Nomination & Election Approval Workflows** by Admin
- ✅ **One Vote per Election Enforcement**
- 📊 **Visual Result Analytics** and Vote Statistics
- 📄 **Report Generation** (PDF/Excel)
- 📝 **Feedback Mechanism** with Admin-only visibility
- 🔍 **Audit Logs** to track all critical actions
- 📂 **Document Uploads** for ID/nomination validation

---

## 🧱 Modules

### 👤 Authentication
- OTP-based registration for both voters and candidates
- Admin approval for activating accounts
- Login system with secure sessions

### 🗃️ Admin Panel
- Election creation and management
- Candidate and voter approval
- View feedback and generate reports
- Result publishing controls

### 🧑‍💼 Candidate Module
- OTP-verified registration
- Submit profile and nomination forms
- View approved elections
- Track result status

### 🧑‍🤝‍🧑 Voter Module
- OTP-verified registration
- Cast one vote per election
- View results after election ends

### 📉 Result & Analytics
- Real-time graphical representation of results
- Downloadable reports (PDF/Excel)

---

## 📸 Screenshots

**HomePage** :![image](https://github.com/user-attachments/assets/a793f8ff-fe0d-4f9c-9684-3b93b2fc0990)
**Admin Dashboard** : ![image](https://github.com/user-attachments/assets/d6686ccd-fc1a-4b7a-a840-ce8637b9dd89)


---

## ⚙️ Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Notifications**: Django Mail, SMSChef API
- **Reports**: xhtml2pdf, Pandas
- **Charts**: Chart.js / Matplotlib

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/your-username/election-management-system.git
cd election-management-system

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

#Create Admin(Superuser)
python manage.py createsuperuser

# Run the server
python manage.py runserver

---
## 📋 Usage Instructions
- **Admin Login:** Access the backend to monitor and manage elections.
- **Candidate Login:** Submit candidacy and view election status.
- **Voter Login:** Cast vote during active elections and check results.
---
## 🧑‍💻 Developed By
Anishkumar Jha 
Final Year BSc IT Student, VIVA College, Mumbai
📧 anishkjha89@gmail.com
🔗 LinkedIn

