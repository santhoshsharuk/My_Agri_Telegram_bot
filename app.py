import logging
import random
import requests
import os  # <-- ADD THIS IMPORT for accessing environment variables
from dotenv import load_dotenv  # <-- ADD THIS IMPORT

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ----------------- Load Environment Variables -----------------
# This line loads the variables from your .env file into the environment
load_dotenv()

# ----------------- Logging and Error Handler -----------------
# This setup is great for local debugging. It will print info and errors to your terminal.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("❌ An unexpected error occurred. Please try again later.")
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.reply_text("❌ An unexpected error occurred. Please try again later.")
    except Exception as e:
        logger.error("Error sending error message: %s", e)

# ----------------- API Keys and Constants (SAFE FOR GITHUB) -----------------
# ###################################################################################
# # IMPORTANT! Your secrets are now loaded from the .env file.                     #
# # This code is now safe to commit to a public repository like GitHub.             #
# ###################################################################################
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# A check to ensure you've set up your .env file correctly.
if not TOKEN or not WEATHER_API_KEY:
    logger.critical("CRITICAL: Environment variables TELEGRAM_BOT_TOKEN and WEATHER_API_KEY must be set.")
    # This error is more descriptive for other developers (or you in the future).
    raise ValueError("Please create a .env file and set the required API keys. See the README.md for details.")


# ----------------- Generate Sample Mandi Data -----------------
districts = [
    "Chennai", "Nagercoil (Kanniyakumari)", "Coimbatore", "Madurai",
    "Salem", "Erode", "Tiruchirappalli", "Tirunelveli", "Tiruppur",
    "Vellore", "Villupuram", "Virudhunagar", "Kanchipuram", "Karur", "Namakkal"
]
markets = ["Market A", "Market B", "Market C", "Market D", "Market E"]
commodities = ["Tomato", "Potato", "Tapioca", "Onion", "Rice", "Wheat", "Cucumber", "Carrot", "Capsicum"]
varieties = ["Local", "Hybrid", "Organic"]

records = []
for i in range(200):
    rec = {
        "state": "Tamil Nadu",
        "district": random.choice(districts),
        "market": random.choice(markets),
        "commodity": random.choice(commodities),
        "variety": random.choice(varieties),
        "arrival_date": "18/03/2025",
        "min_price": random.randint(1000, 5000),
        "max_price": random.randint(5001, 10000),
        "modal_price": random.randint(3000, 8000)
    }
    records.append(rec)
MANDI_DATA = {"records": records}

# ----------------- Helper Functions (No changes needed here) -----------------
def get_mandi_data_by_district(district):
    filtered = [
        rec for rec in MANDI_DATA.get("records", [])
        if rec.get("district", "").strip().lower() == district.strip().lower()
    ]
    return {"records": filtered}

def format_mandi_data_simple(data):
    records = data.get("records", [])
    if not records:
        return "❌ No data found for this district."
    
    district_name = records[0].get('district', 'N/A')
    message = f"📊 *Mandi Prices for {district_name}*\n(Showing up to 5 records)\n\n"
    for rec in records[:5]:
        message += (
            f"🌾 *Commodity:* {rec.get('commodity', 'N/A')} ({rec.get('variety', 'N/A')})\n"
            f"📍 *Market:* {rec.get('market', 'N/A')}\n"
            f"💰 *Price (Min/Modal/Max):* ₹{rec.get('min_price', 'N/A')} / ₹{rec.get('modal_price', 'N/A')} / ₹{rec.get('max_price', 'N/A')}\n"
            f"📅 *Arrival Date:* {rec.get('arrival_date', 'N/A')}\n"
            "-----------------\n"
        )
    if len(records) > 5:
        message += f"\n_...and {len(records) - 5} more records exist for this district._"
    return message.strip()

def get_crop_info(crop_name):
    url = f'https://openfarm.cc/api/v1/crops?filter={crop_name}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        crops = data.get('data', [])
        if crops:
            crop = crops[0]['attributes']
            name = crop.get('name', 'N/A')
            description = crop.get('description', 'N/A')
            sun_requirements = crop.get('sun_requirements', 'N/A')
            sowing_method = crop.get('sowing_method', 'N/A')
            return (
                f"🌾 *{name}*\n\n"
                f"📌 *Description:* {description or 'Not available.'}\n"
                f"☀️ *Sun Requirements:* {sun_requirements or 'Not available.'}\n"
                f"🌱 *Sowing Method:* {sowing_method or 'Not available.'}"
            )
        return "❌ No information found for this crop."
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for crop info: {e}")
        return "❌ Failed to fetch crop information. The API might be down or your request failed."

def get_detailed_weather(query):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={query}&days=3&aqi=yes&alerts=no"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        location = data["location"]["name"]
        region = data["location"]["region"]
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        wind_speed = data["current"]["wind_kph"]
        humidity = data["current"]["humidity"]
        uv_index = data["current"]["uv"]
        sunrise = data["forecast"]["forecastday"][0]["astro"]["sunrise"]
        sunset = data["forecast"]["forecastday"][0]["astro"]["sunset"]

        forecast_msg = "🌧️ *3-Day Rain Forecast:*\n"
        for day in data["forecast"]["forecastday"]:
            date = day["date"]
            rain_chance = day["day"]["daily_chance_of_rain"]
            forecast_msg += f"  - `{date}`: *{rain_chance}%* chance\n"

        return (
            f"🌍 *Weather for {location}, {region}*\n\n"
            f"🌡️ *Temperature:* {temp}°C\n"
            f"☁️ *Condition:* {condition}\n"
            f"💨 *Wind Speed:* {wind_speed} km/h\n"
            f"💧 *Humidity:* {humidity}%\n"
            f"☀️ *Sunrise:* {sunrise} | 🌅 *Sunset:* {sunset}\n"
            f"🔥 *UV Index:* {uv_index}\n\n"
            f"{forecast_msg}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for weather: {e}")
        return "❌ Unable to fetch weather. Please check the city name or try again."

# ----------------- Telegram Bot Handlers (No changes needed here) -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to MyAgriBot! I can help you with crop information, weather forecasts, and mandi prices."
    )
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌾 Get Crop Info", callback_data='crop_info')],
        [InlineKeyboardButton("☀️ Get Weather Info", callback_data='weather_info')],
        [InlineKeyboardButton("📊 Mandi Prices", callback_data='mandi_prices_menu')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='contact_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = "📍 *Main Menu*\n\nHow can I assist you today?"
    if update.callback_query:
        await update.callback_query.message.edit_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *MyAgriBot Help*\n\n"
        "Use /start to see the main menu.\n\n"
        "You can get:\n"
        "   - 🌾 *Crop Info:* Details on various crops.\n"
        "   - ☀️ *Weather Info:* Detailed weather forecasts.\n"
        "   - 📊 *Mandi Prices:* Local market prices.\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data.pop('state', None)
    data = query.data
    
    if data == 'crop_info':
        context.user_data['state'] = 'awaiting_crop'
        await query.message.edit_text(text="🌾 Please enter the name of the crop (e.g., Tomato):")
    
    elif data == 'weather_info':
        context.user_data['state'] = 'awaiting_location'
        await query.message.edit_text(text="🌍 Please enter your city or location for the forecast:")
        
    elif data == 'mandi_prices_menu':
        await show_mandi_districts_menu(update, context)
        
    elif data.startswith('mandi_district_'):
        district_name = data.replace('mandi_district_', '')
        await query.message.edit_text("⏳ Fetching data, please wait...")
        mandi_data = get_mandi_data_by_district(district_name)
        formatted_data = format_mandi_data_simple(mandi_data)
        await query.message.edit_text(
            formatted_data, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Districts", callback_data='mandi_prices_menu')]]))
        
    elif data == 'contact_support':
        await query.message.edit_text(
            text="📞 *Support*\n\nFor issues, please contact support@myagribot.dev.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')]]))
        
    elif data == 'main_menu':
        await show_main_menu(update, context)

async def show_mandi_districts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(d, callback_data=f'mandi_district_{d}')] for d in districts]
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("📊 Please select a district:", reply_markup=reply_markup)
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get('state')
    if not state:
        await update.message.reply_text("I'm not sure what you mean. Use /start to see the main menu.")
        return
    user_input = update.message.text
    await update.message.reply_text(f"⏳ Searching for `{user_input}`...", parse_mode="Markdown")
    if state == 'awaiting_crop':
        response_text = get_crop_info(user_input)
    elif state == 'awaiting_location':
        response_text = get_detailed_weather(user_input)
    else:
        response_text = "Something went wrong. Please start over with /start."
    del context.user_data['state']
    await update.message.reply_text(response_text, parse_mode="Markdown")
    await show_main_menu(update, context)

def main() -> None:
    """Start the bot locally."""
    app = Application.builder().token(TOKEN).build()
    
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting locally...")
    print("Bot is running! Press Ctrl+C to stop.")
    
    # Start the Bot
    app.run_polling()

if __name__ == "__main__":
    main()