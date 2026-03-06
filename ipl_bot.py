# ============================================
# IPL CRICKET BETTING PRO BOT - MAIN CODE
# ============================================

import telebot
import random
import json
import os
import time
from datetime import datetime, timedelta
from threading import Thread

# ==================== APNA DATA YAHAN DALO ====================
BOT_TOKEN = "8543120380:AAEwyu14HLovJ0cgh5eAy7kzulyl_YL31EI"  # @BotFather se lo
ADMIN_IDS = ["935207891"]   # https://t.me/userinfobot se lo
UPI_ID = "aryan.bind1@ybl"      # Apna UPI ID dalo
QR_CODE_LINK = ""  # QR code link (optional)
# ===============================================================

bot = telebot.TeleBot(BOT_TOKEN)

# ==================== IPL TEAMS ====================
IPL_TEAMS = {
    "CSK": "💛 Chennai Super Kings (MS Dhoni)",
    "RCB": "❤️ Royal Challengers Bangalore (Virat Kohli)",
    "MI": "💙 Mumbai Indians (Rohit Sharma)",
    "KKR": "💜 Kolkata Knight Riders",
    "DC": "💚 Delhi Capitals",
    "SRH": "🧡 Sunrisers Hyderabad",
    "PBKS": "🩷 Punjab Kings",
    "RR": "💗 Rajasthan Royals",
    "GT": "💙 Gujarat Titans (Hardik Pandya)",
    "LSG": "💚 Lucknow Super Giants"
}

# ==================== IPL SCHEDULE 2024 ====================
IPL_SCHEDULE = [
    {"date": "2024-03-22", "team1": "CSK", "team2": "RCB", "time": "7:30 PM", "venue": "Chennai"},
    {"date": "2024-03-23", "team1": "PBKS", "team2": "DC", "time": "3:30 PM", "venue": "Mohali"},
    {"date": "2024-03-23", "team1": "KKR", "team2": "SRH", "time": "7:30 PM", "venue": "Kolkata"},
    {"date": "2024-03-24", "team1": "RR", "team2": "LSG", "time": "3:30 PM", "venue": "Jaipur"},
    {"date": "2024-03-24", "team1": "GT", "team2": "MI", "time": "7:30 PM", "venue": "Ahmedabad"},
]

# ==================== DATABASE ====================
DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

users = load_users()

# ==================== GAME SETTINGS ====================
GAME_CONFIG = {
    "welcome_bonus": 100,
    "referral_bonus": 50,
    "min_bet": 10,
    "max_bet": 1000,
    "min_withdrawal": 100,
    "max_daily_withdrawal": 2000,
    "daily_bet_limit": 5000,
    "team_bonus": 1.2,
    "match_bonus": 1.1,
}

# Game Results (20% House Edge)
GAME_RESULTS = [
    {"name": "🚀 SIX", "prob": 5, "payout": 2.5, "desc": "धोनी स्टाइल में छक्का!"},
    {"name": "🏏 FOUR", "prob": 10, "payout": 1.8, "desc": "कोहली जैसा फोर!"},
    {"name": "🏃 SINGLE", "prob": 20, "payout": 1.3, "desc": "हार्दिक की तरह दौड़!"},
    {"name": "⭕ DOT", "prob": 30, "payout": 0.7, "desc": "जडेजा की फील्डिंग!"},
    {"name": "❌ WICKET", "prob": 35, "payout": 0, "desc": "बुमराह की यॉर्कर!"},
]

# ==================== HELPER FUNCTIONS ====================
def get_today_match():
    today = datetime.now().strftime("%Y-%m-%d")
    for match in IPL_SCHEDULE:
        if match["date"] == today:
            return match
    return None

def get_upcoming_matches(count=5):
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming = []
    for match in IPL_SCHEDULE:
        if match["date"] > today and len(upcoming) < count:
            upcoming.append(match)
    return upcoming

# ==================== START COMMAND ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    
    # Referral check
    referrer_id = None
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
    
    if user_id not in users:
        # New user
        users[user_id] = {
            "balance": GAME_CONFIG["welcome_bonus"],
            "team": None,
            "total_deposit": 0,
            "total_withdrawal": 0,
            "total_bets": 0,
            "total_wins": 0,
            "referrals": 0,
            "referred_by": referrer_id,
            "daily_bet": 0,
            "last_bet_date": str(datetime.now().date()),
            "joined": str(datetime.now()),
            "username": message.from_user.username or "No username",
            "first_name": message.from_user.first_name or ""
        }
        
        # Referral bonus
        if referrer_id and referrer_id in users:
            users[referrer_id]["balance"] += GAME_CONFIG["referral_bonus"]
            users[referrer_id]["referrals"] += 1
            try:
                bot.send_message(
                    referrer_id,
                    f"🎉 दोस्त जुड़ गया! ₹{GAME_CONFIG['referral_bonus']} बोनस मिला!"
                )
            except:
                pass
        
        save_users(users)
        
        msg = (
            "🏏 *IPL CRICKET BETTING PRO 2024* 🏏\n\n"
            f"🎁 वेलकम बोनस: ₹{GAME_CONFIG['welcome_bonus']}\n"
            "🔥 IPL स्पेशल: हर मैच पर बोनस\n\n"
            "*कमांड्स:*\n"
            "/play 100 - बेट लगाओ\n"
            "/team - IPL टीम चुनो\n"
            "/matches - आज के मैच\n"
            "/balance - बैलेंस चेक\n"
            "/recharge - पैसे जमा करो\n"
            "/withdraw - पैसे निकालो\n"
            "/refer - दोस्त को बुलाओ\n"
            "/ipl - IPL अपडेट\n"
            "/help - हेल्प\n\n"
            "⚡ IPL 2024 शुरू: 22 मार्च"
        )
    else:
        msg = "👋 वापस आ गए! खेलते हैं?"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== PLAY GAME ====================
@bot.message_handler(commands=['play'])
def play(message):
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        bot.reply_to(message, "पहले /start करो!")
        return
    
    user = users[user_id]
    
    try:
        bet = int(message.text.split()[1])
    except:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
        markup.add(
            telebot.types.KeyboardButton("/play 50"),
            telebot.types.KeyboardButton("/play 100"),
            telebot.types.KeyboardButton("/play 200"),
            telebot.types.KeyboardButton("/play 500"),
            telebot.types.KeyboardButton("/play 1000"),
            telebot.types.KeyboardButton("/balance")
        )
        bot.reply_to(
            message,
            f"💰 बैलेंस: ₹{user['balance']}\nकितना लगाओगे?",
            reply_markup=markup
        )
        return
    
    if bet < GAME_CONFIG["min_bet"]:
        bot.reply_to(message, f"मिनिमम बेट ₹{GAME_CONFIG['min_bet']} है!")
        return
    
    if bet > user["balance"]:
        bot.reply_to(message, f"बैलेंस कम है! Current: ₹{user['balance']}")
        return
    
    if bet > GAME_CONFIG["max_bet"]:
        bot.reply_to(message, f"एक बार में मैक्स ₹{GAME_CONFIG['max_bet']}!")
        return
    
    # Daily limit
    today = str(datetime.now().date())
    if user.get("last_bet_date") != today:
        user["daily_bet"] = 0
        user["last_bet_date"] = today
    
    if user["daily_bet"] + bet > GAME_CONFIG["daily_bet_limit"]:
        bot.reply_to(message, "आज का लिमिट खत्म! कल आना!")
        return
    
    # Deduct bet
    user["balance"] -= bet
    user["daily_bet"] += bet
    user["total_bets"] += 1
    
    # Bonuses
    multiplier = 1.0
    today_match = get_today_match()
    
    if today_match and user["team"]:
        if user["team"] == today_match["team1"] or user["team"] == today_match["team2"]:
            multiplier *= GAME_CONFIG["team_bonus"]
    
    if today_match:
        multiplier *= GAME_CONFIG["match_bonus"]
    
    # Game result
    r = random.randint(1, 100)
    cumulative = 0
    
    for result in GAME_RESULTS:
        cumulative += result["prob"]
        if r <= cumulative:
            selected = result
            break
    
    win_amount = int(bet * selected["payout"] * multiplier)
    
    # Result message
    if win_amount > 0:
        user["balance"] += win_amount
        user["total_wins"] += 1
        result_text = f"{selected['name']}! {selected['desc']}\n\nजीत: ₹{win_amount}"
    else:
        result_text = f"{selected['name']}! {selected['desc']}\n\nहार: ₹{bet}"
    
    result_text += f"\n\n💰 नया बैलेंस: ₹{user['balance']}"
    
    if today_match:
        result_text += f"\n\n📺 आज का मैच: {IPL_TEAMS[today_match['team1']]} vs {IPL_TEAMS[today_match['team2']]}"
    
    bot.reply_to(message, result_text, parse_mode="Markdown")
    save_users(users)

# ==================== TEAM SELECTION ====================
@bot.message_handler(commands=['team'])
def team(message):
    teams_list = ""
    for code, name in IPL_TEAMS.items():
        teams_list += f"{code}: {name}\n"
    
    msg = (
        "🏏 *IPL टीम चुनो*\n\n"
        f"{teams_list}\n"
        "/setteam CSK - CSK के लिए\n"
        "फायदा: अपनी टीम के मैच पर 20% extra!"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['setteam'])
def set_team(message):
    user_id = str(message.from_user.id)
    
    try:
        team = message.text.split()[1].upper()
        if team in IPL_TEAMS:
            users[user_id]["team"] = team
            save_users(users)
            msg = f"✅ आपने {IPL_TEAMS[team]} को चुना!"
        else:
            msg = "❌ गलत टीम कोड! /team देखो"
    except:
        msg = "❌ सही फॉर्मेट: /setteam CSK"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== MATCHES ====================
@bot.message_handler(commands=['matches'])
def matches(message):
    today_match = get_today_match()
    upcoming = get_upcoming_matches(5)
    
    msg = "📅 *IPL 2024 SCHEDULE*\n\n"
    
    if today_match:
        msg += "🔥 *आज का मैच:* 🔥\n"
        msg += f"{IPL_TEAMS[today_match['team1']]} vs {IPL_TEAMS[today_match['team2']]}\n"
        msg += f"⏰ {today_match['time']} | 🏟️ {today_match['venue']}\n\n"
    
    msg += "📌 *अगले मैच:*\n"
    for match in upcoming:
        msg += f"📆 {match['date']}: {IPL_TEAMS[match['team1']]} vs {IPL_TEAMS[match['team2']]}\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== IPL INFO ====================
@bot.message_handler(commands=['ipl'])
def ipl_info(message):
    today_match = get_today_match()
    
    msg = "🏏 *IPL 2024 UPDATE*\n\n"
    
    if today_match:
        msg += "🔥 *आज का मैच:* 🔥\n"
        msg += f"{IPL_TEAMS[today_match['team1']]} vs {IPL_TEAMS[today_match['team2']]}\n"
        msg += f"⏰ {today_match['time']} | 🏟️ {today_match['venue']}\n\n"
        msg += "⚡ *मैच स्पेशल:*\n"
        msg += "• सभी बेट्स पर 10% extra\n"
        msg += "• अपनी टीम पर 20% extra\n"
    else:
        msg += "❌ आज कोई मैच नहीं\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== BALANCE ====================
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    
    if user_id in users:
        user = users[user_id]
        team_name = IPL_TEAMS.get(user["team"], "कोई नहीं")
        
        win_rate = 0
        if user["total_bets"] > 0:
            win_rate = (user["total_wins"] / user["total_bets"]) * 100
        
        msg = (
            f"💰 *आपका अकाउंट*\n\n"
            f"बैलेंस: ₹{user['balance']}\n"
            f"टीम: {team_name}\n"
            f"कुल बेट्स: {user['total_bets']}\n"
            f"जीत %: {win_rate:.1f}%\n"
            f"दोस्त बुलाए: {user['referrals']}\n"
            f"कुल जमा: ₹{user['total_deposit']}\n"
            f"कुल निकासी: ₹{user['total_withdrawal']}"
        )
    else:
        msg = "पहले /start करो!"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== RECHARGE ====================
@bot.message_handler(commands=['recharge'])
def recharge(message):
    msg = (
        "💳 *रिचार्ज*\n\n"
        f"UPI ID: `{UPI_ID}`\n\n"
        "*स्टेप्स:*\n"
        "1️⃣ UPI app खोलो\n"
        "2️⃣ उपर वाले ID पर भेजो\n"
        "3️⃣ स्क्रीनशॉट यहाँ भेजो\n"
        "4️⃣ 5 मिनट में बैलेंस ऐड\n\n"
        "*बोनस:*\n"
        "₹100-500 → 5% extra\n"
        "₹501-2000 → 10% extra\n"
        "₹2000+ → 15% extra"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== WITHDRAWAL ====================
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        bot.reply_to(message, "पहले /start करो!")
        return
    
    user = users[user_id]
    
    if user["balance"] < GAME_CONFIG["min_withdrawal"]:
        bot.reply_to(message, f"मिनिमम निकासी ₹{GAME_CONFIG['min_withdrawal']} है!")
        return
    
    msg = (
        "📤 *निकासी*\n\n"
        f"बैलेंस: ₹{user['balance']}\n\n"
        "*फॉर्मेट:*\n"
        "`/withdraw अमाउंट@UPI_ID`\n\n"
        "*Example:*\n"
        "`/withdraw 500@user@okhdfcbank`\n\n"
        f"मिन: ₹{GAME_CONFIG['min_withdrawal']}\n"
        f"मैक्स/दिन: ₹{GAME_CONFIG['max_daily_withdrawal']}"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['withdraw'])
def process_withdrawal(message):
    user_id = str(message.from_user.id)
    
    try:
        _, data = message.text.split()
        amount, upi = data.split('@')
        amount = int(amount)
        
        user = users[user_id]
        
        if amount < GAME_CONFIG["min_withdrawal"]:
            bot.reply_to(message, f"मिनिमम ₹{GAME_CONFIG['min_withdrawal']}!")
            return
        
        if amount > user["balance"]:
            bot.reply_to(message, "बैलेंस कम है!")
            return
        
        if amount > GAME_CONFIG["max_daily_withdrawal"]:
            bot.reply_to(message, f"मैक्स ₹{GAME_CONFIG['max_daily_withdrawal']} प्रति दिन!")
            return
        
        user["balance"] -= amount
        user["total_withdrawal"] += amount
        save_users(users)
        
        for admin in ADMIN_IDS:
            bot.send_message(
                admin,
                f"💰 Withdrawal Request\nUser: {user_id}\nAmount: ₹{amount}\nUPI: {upi}"
            )
        
        bot.reply_to(message, f"✅ ₹{amount} का request भेज दिया! 2-4 घंटे लगेंगे।")
        
    except:
        bot.reply_to(message, "❌ गलत फॉर्मेट! /withdraw देखो")

# ==================== REFERRAL ====================
@bot.message_handler(commands=['refer'])
def refer(message):
    user_id = str(message.from_user.id)
    bot_username = bot.get_me().username
    
    msg = (
        "👥 *Refer & Earn*\n\n"
        f"हर दोस्त पर: ₹{GAME_CONFIG['referral_bonus']}\n"
        f"दोस्त को: ₹{GAME_CONFIG['welcome_bonus']}\n\n"
        f"आपका लिंक:\n"
        f"`https://t.me/{bot_username}?start={user_id}`\n\n"
        f"अब तक बुलाए: {users[user_id]['referrals']} दोस्त"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== HELP ====================
@bot.message_handler(commands=['help'])
def help(message):
    msg = (
        "📚 *HELP*\n\n"
        "*गेम कैसे खेलें:*\n"
        "/start - शुरू करें\n"
        "/team - टीम चुनें\n"
        "/play 100 - बेट लगाएं\n\n"
        "*पेमेंट:*\n"
        "/recharge - जमा करें\n"
        "/withdraw - निकालें\n\n"
        "*गेम रिजल्ट:*\n"
        "🚀 SIX (5%) → 2.5x\n"
        "🏏 FOUR (10%) → 1.8x\n"
        "🏃 SINGLE (20%) → 1.3x\n"
        "⭕ DOT (30%) → 0.7x\n"
        "❌ WICKET (35%) → 0x\n\n"
        "*बोनस:*\n"
        "टीम बोनस: 20% extra\n"
        "मैच बोनस: 10% extra"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================== PHOTO HANDLER ====================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = str(message.from_user.id)
    file_id = message.photo[-1].file_id
    
    bot.reply_to(message, "✅ स्क्रीनशॉट मिल गया! एडमिन चेक करेगा।")
    
    for admin in ADMIN_IDS:
        bot.send_photo(
            admin,
            file_id,
            caption=f"📸 Recharge Screenshot\nUser: {user_id}\nName: {message.from_user.first_name}"
        )

# ==================== ADMIN COMMANDS ====================
@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = str(message.from_user.id)
    
    if user_id not in ADMIN_IDS:
        return
    
    total_users = len(users)
    total_balance = sum(u['balance'] for u in users.values())
    total_deposits = sum(u['total_deposit'] for u in users.values())
    total_withdrawals = sum(u['total_withdrawal'] for u in users.values())
    total_bets = sum(u['total_bets'] for u in users.values())
    
    msg = (
        f"👑 *ADMIN PANEL*\n\n"
        f"कुल यूजर्स: {total_users}\n"
        f"कुल बैलेंस: ₹{total_balance}\n"
        f"कुल जमा: ₹{total_deposits}\n"
        f"कुल निकासी: ₹{total_withdrawals}\n"
        f"हाउस प्रॉफिट: ₹{total_deposits - total_withdrawals}\n"
        f"कुल बेट्स: {total_bets}"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = str(message.from_user.id)
    
    if user_id not in ADMIN_IDS:
        return
    
    try:
        broadcast_msg = message.text.replace('/broadcast', '').strip()
        
        if not broadcast_msg:
            bot.reply_to(message, "मैसेज भी लिखो!")
            return
        
        sent = 0
        for uid in users.keys():
            try:
                bot.send_message(uid, f"📢 {broadcast_msg}")
                sent += 1
            except:
                pass
        
        bot.reply_to(message, f"✅ भेजे गए: {sent}")
        
    except:
        bot.reply_to(message, "❌ Error")

# ==================== AUTO BROADCAST ====================
def auto_broadcast_worker():
    while True:
        try:
            now = datetime.now()
            
            # Morning bonus (10 AM)
            if now.hour == 10 and now.minute == 0:
                for uid in users.keys():
                    try:
                        bot.send_message(
                            uid,
                            "🌅 गुड मॉर्निंग! आज के लिए ₹50 बोनस! /play 50"
                        )
                    except:
                        pass
            
            time.sleep(60)
            
        except:
            time.sleep(60)

# ==================== START BOT ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🏏 IPL CRICKET BETTING PRO BOT 🏏")
    print("=" * 50)
    print(f"✅ Bot starting...")
    print(f"✅ Users loaded: {len(users)}")
    print(f"✅ Admin IDs: {ADMIN_IDS}")
    print(f"✅ UPI ID: {UPI_ID}")
    print("✅ Auto broadcast starting...")
    
    broadcast_thread = Thread(target=auto_broadcast_worker)
    broadcast_thread.daemon = True
    broadcast_thread.start()
    
    print("✅ Bot is running! Press Ctrl+C to stop")
    print("=" * 50)
    
    bot.infinity_polling()