
# Mustaqeer: Your Companion for Consistent Quran Engagement

Mustaqeer is a powerful app designed to encourage and support Muslim brothers and sisters in their journey of daily Quran reading and learning. The name "Mustaqeer," derived from Arabic, means "one who is steadfast" or "one who is firm," embodying the app's purpose of promoting dedication and commitment to spiritual growth through consistent Quranic engagement.

## 🌟 Key Features

- **Daily Reading Tracker**: Log your daily Quran reading progress and visualize your consistency over time.
- **Personalized Goals**: Set custom reading goals tailored to your schedule and aspirations.
- **Verse of the Day**: Receive daily inspiration with a carefully selected Quranic verse and its explanation.
- **Progress Insights**: Gain valuable insights into your reading patterns and achievements.
- **Community Support**: Connect with other users, share experiences, and motivate each other in your Quranic journey.
- **Customizable Reminders**: Set notifications to help you maintain your reading routine.

## 🎯 Our Mission

At Mustaqeer, we strive to make Quran reading an integral part of your daily life. By providing tools for tracking, learning, and connecting with others, we aim to foster a deeper connection with the Quran and support your spiritual growth.

## 💡 Get Involved

We welcome contributions from the community! Whether you're a developer, designer, or have valuable insights to share, your input can help make Mustaqeer even better. Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## 🚀 Start Your Journey

Ready to embark on a transformative Quranic journey? Follow the installation instructions below to set up Mustaqeer and take the first step towards consistent and meaningful Quran engagement.



# 🚀 Getting Started with Mustaqeer

Follow these steps to set up and run Mustaqeer on your local machine:

1. **Prerequisites**
   - Python 3.12.2 or higher
   - Poetry (Python package manager)

2. **Install Poetry**
   Run the following command in your terminal:
   ```bash
   curl -sSL https://install.python-poetry.org | python3.12 -
   ```

3. **Install Dependencies**
   Navigate to the project directory and run:
   ```bash
   poetry install
   ```

4. **Set Up the Database**
   Create the necessary database tables by running:
   ```bash
   poetry run alembic upgrade head
   ```

5. **Run the Application**
   Start the Mustaqeer app with:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
   or
   ```bash
   poetry run fastapi dev app/main.py
   ```

6. **Access the Application**
   Open your web browser and go to `http://localhost:8000` to start using Mustaqeer!

For more detailed information on using and contributing to Mustaqeer, please refer to our documentation.
