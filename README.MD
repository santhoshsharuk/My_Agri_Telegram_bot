# MyAgriBot - Telegram Bot

A helpful Telegram bot for farmers and gardeners that provides quick access to agricultural information, including crop details, real-time weather forecasts, and local market (mandi) prices.


*(Feel free to replace the image above with a screenshot or GIF of your actual bot in action!)*

---

## ✨ Features

-   🌾 **Get Crop Information**: Fetches detailed information about various crops, including sowing methods and sun requirements, using the [OpenFarm API](https://openfarm.cc/).
-   ☀️ **Real-time Weather Forecasts**: Provides current weather conditions and a 3-day rain forecast for any location using the [WeatherAPI.com](https://www.weatherapi.com/).
-   📊 **Mandi Prices**: Displays sample commodity prices from various markets in Tamil Nadu districts (Note: This version uses sample data).
-   🤖 **Interactive Menus**: Easy-to-use inline keyboard buttons for seamless navigation.
-   🔒 **Secure**: API keys and secrets are managed safely using environment variables, making the code safe to share publicly.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

-   [Python 3.8+](https://www.python.org/downloads/) installed on your machine.
-   A Telegram Bot Token. You can get one by talking to the [@BotFather](https://t.me/BotFather) on Telegram.
-   An API Key from [WeatherAPI.com](https://www.weatherapi.com/). The free tier is sufficient for this project.

---

## 🚀 Installation & Setup

Follow these steps to get your bot up and running locally.

**1. Clone the Repository**
```bash
git clone https://github.com/santhoshsharuk/My_Agri_Telegram_bot
cd My_Agri_Telegram_bot
```

**2. Create a Virtual Environment**
It's a best practice to create a virtual environment to manage project dependencies.
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
This project uses a few Python libraries. A `requirements.txt` file is included for easy installation.
```bash
pip install -r requirements.txt
```
*(If you don't have a `requirements.txt` file yet, you can create one after installing the packages manually: `pip freeze > requirements.txt`)*

**4. Configure Environment Variables**
This project uses a `.env` file to store your secret API keys.

-   First, copy the example file:
    ```bash
    # For Windows
    copy .env.example .env

    # For macOS/Linux
    cp .env.example .env
    ```
-   Next, open the newly created `.env` file and add your secret keys:

    ```env
    # .env
    # This file contains your secret keys. DO NOT commit it to Git.
    TELEGRAM_BOT_TOKEN=""
    WEATHER_API_KEY=""
    ```
The `.gitignore` file is already configured to ignore the `.env` file, so your keys will not be accidentally committed to GitHub.

---

## ▶️ Running the Bot

Once you have completed the setup and configuration, you can start the bot with a single command:

```bash
python bot.py
```
*(Replace `bot.py` with the actual name of your Python script if it's different.)*

Your bot should now be running! Open Telegram, find your bot, and send the `/start` command to begin interacting with it.

---

## 📁 Project Structure

```
myagribot-telegram/
├── bot.py             # Main bot script
├── .env               # Your local secrets file (ignored by Git)
├── .env.example       # Example file for environment variables
├── .gitignore         # Tells Git which files to ignore
└── requirements.txt   # List of Python dependencies
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME/issues).

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).