# ML-Project-Backend

A Django-based backend for managing student data and predicting risk levels using a Hugging Face ML model.

## Overview
This project provides RESTful APIs to:
- Manage students, attendance, and marks
- Analyze student risk based on attendance and marks via a Hugging Face model
- Store and update risk predictions

## Tech Stack
- Django 5.1.7 with REST Framework
- MySQL (`ML-Project` database)
- Hugging Face Inference API

## Quick Setup
1. Clone the repo: `git clone https://github.com/your-username/ML-Project-Backend.git`
2. Install dependencies: `pip install django djangorestframework mysqlclient requests`
3. Set up MySQL database: `CREATE DATABASE `ML-Project`;`
4. Update `student_management/settings.py` with your MySQL credentials
5. Update `risk_analysis/views.py` with your Hugging Face model URL and API token
6. Run migrations: `python manage.py migrate`
7. Start the server: `python manage.py runserver`

## Main Endpoint
- **Risk Analysis**: `GET /api/student/<student_id>/risk/`
  - Returns student details and risk prediction

## Notes
- Replace Hugging Face placeholders with your actual model details
- Use a virtual environment for best practice
