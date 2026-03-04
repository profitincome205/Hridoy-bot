import telebot
from telebot import types
import datetime

# --- সেটিংস ---
API_TOKEN = '7760979122:AAFyxBtoBtzU5wLreLl9jfUurlimtDGhKIY'
ADMIN_ID = 8290768037
USDT_ADDRESS = "0xa40e6b91cf5a1810ef0b118f32f44330cb820ab3"
MIN_DEPOSIT = 10.0

bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস (বট রিস্টার্ট দিলে এটি রিসেট হবে, স্থায়ী করতে SQLite ব্যবহার করুন)
users = {} # {id: {'balance': 0, 'status': 'Member'}}

def get_user_data(uid):
    if uid not in users:
        users[uid] = {'balance': 0.0, 'status': 'Member', 'joined': datetime.date.today()}
    return users[uid]

# --- ১. ইউজার মেইন মেনু ---
def send_main_menu(chat_id, user_id):
    data = get_user_data(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btns = [
        types.InlineKeyboardButton("🛒 Buy Account", callback_data="buy_acc"),
        types.InlineKeyboardButton("💰 Sell Account", callback_data="sell_acc"),
        types.InlineKeyboardButton("💳 TopUp Balance", callback_data="topup"),
        types.InlineKeyboardButton("💸 Payout Money", callback_data="payout"),
        types.InlineKeyboardButton("👤 My Profile", callback_data="profile"),
        types.InlineKeyboardButton("🌍 Language / More", callback_data="more_lang"),
        types.InlineKeyboardButton("📞 Contact Support", url="https://t.me/Hridoy_Support"),
        types.InlineKeyboardButton("📢 News Channel", url="https://t.me/Hridoy_News")
    ]
    markup.add(*btns)
    
    text = (
        f"👋 **Welcome to Hridoy-bot Store!**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"💵 **Total Balance:** `{data['balance']}$`\n"
        f"🎖️ **Status:** `{data['status']}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔥 _Select an option from below to start!_"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    send_main_menu(message.chat.id, message.from_user.id)

# --- ২. অ্যাডমিন প্যানেল ---
@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 User Stats", callback_data="admin_stats"),
            types.InlineKeyboardButton("💰 Add Balance", callback_data="admin_add_bal"),
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_bc"),
            types.InlineKeyboardButton("🔙 Back to User", callback_data="main_menu")
        )
        bot.send_message(message.chat.id, "👨‍💻 **Hridoy-bot Admin Panel**", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Access Denied!")

# --- ৩. অল কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    user = get_user_data(uid)

    if call.data == "main_menu":
        bot.delete_message(cid, mid)
        send_main_menu(cid, uid)

    # --- Buy Section ---
    elif call.data == "buy_acc":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🚀 Server (1) - Fresh", callback_data="server_1"),
            types.InlineKeyboardButton("💦 Server (2) - Old Accounts", callback_data="server_2"),
            types.InlineKeyboardButton("🔙 Back", callback_data="main_menu")
        )
        bot.edit_message_text("📂 **Select Purchase Server:**", cid, mid, reply_markup=markup)

    elif call.data == "server_1":
        markup = types.InlineKeyboardMarkup(row_width=2)
        countries = [("🇧🇩 BD", 0.4), ("🇺🇸 USA", 0.1), ("🇪🇸 SP", 0.5), ("🇸🇦 SA", 0.4), ("🇵🇹 PO", 0.1), ("🇳🇬 NG", 0.3), ("🇮🇳 IND", 0.4), ("🇧🇷 BRA", 0.2), ("🇮🇹 ITALY", 1.0)]
        for name, price in countries:
            markup.add(types.InlineKeyboardButton(f"{name}: {price}$", callback_data=f"conf_buy_{price}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="buy_acc"))
        bot.edit_message_text("🌍 **Server (1) - Choose Country:**", cid, mid, reply_markup=markup)

    elif call.data == "server_2":
        markup = types.InlineKeyboardMarkup(row_width=3)
        years = [str(y) for y in range(2015, 2026)]
        btns = [types.InlineKeyboardButton(y, callback_data=f"year_{y}") for y in years]
        markup.add(*btns)
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="buy_acc"))
        bot.edit_message_text("📅 **Server (2) - Choose Account Age:**", cid, mid, reply_markup=markup)

    # --- Sell Section ---
    elif call.data == "sell_acc":
        prices = "🇧🇩 BD: 0.20$\n🇺🇸 USA: 0.20$\n🇺🇿 UZ: 0.60$\n🇮🇹 IT: 0.70$\n*Number No Need*"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="main_menu"))
        bot.edit_message_text(f"💰 **Sell Prices:**\n{prices}\n\n_Send number to admin for selling!_", cid, mid, reply_markup=markup)

    # --- TopUp (Deposit) ---
    elif call.data == "topup":
        msg = bot.send_message(cid, f"💳 **Deposit System**\nMin: {MIN_DEPOSIT}$\nEnter Amount:")
        bot.register_next_step_handler(msg, process_deposit)

    # --- Language / More ---
    elif call.data == "more_lang":
        markup = types.InlineKeyboardMarkup(row_width=2)
        langs = ["🇺🇸 English", "🇧🇩 Bengali", "🇮🇳 Hindi", "🇸🇦 Arabic", "🇫🇷 French", "🇪🇸 Spanish"]
        btns = [types.InlineKeyboardButton(l, callback_data=f"set_lang_{l}") for l in langs]
        markup.add(*btns)
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="main_menu"))
        bot.edit_message_text("🌐 **Choose Your Language:**", cid, mid, reply_markup=markup)

# --- ৪. ডিপোজিট লজিক ---
def process_deposit(message):
    try:
        amt = float(message.text)
        if amt < MIN_DEPOSIT:
            bot.reply_to(message, "❌ Amount too low!")
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{amt}"))
        text = f"💳 **Send {amt}$ to:**\n`{USDT_ADDRESS}`\nNetwork: **USDT BEP20**"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Invalid Input!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("paid_"))
def submit_proof(call):
    amt = call.data.split("_")[1]
    msg = bot.send_message(call.message.chat.id, "📸 Send Payment Proof (Screenshot):")
    bot.register_next_step_handler(msg, notify_admin, amt)

def notify_admin(message, amt):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{message.from_user.id}_{amt}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{message.from_user.id}")
    )
    admin_msg = f"🔔 **New Deposit**\nUser: `{message.from_user.id}`\nAmount: `{amt}$`"
    if message.content_type == 'photo':
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_msg, reply_markup=markup)
    else:
        bot.send_message(ADMIN_ID, f"{admin_msg}\nProof: {message.text}", reply_markup=markup)
    bot.send_message(message.chat.id, "⏳ Proof sent to admin!")

# --- ৫. অ্যাডমিন অ্যাকশন হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_actions(call):
    data = call.data.split("_")
    action, t_id = data[1], int(data[2])
    
    if action == "app":
        amt = float(data[3])
        users[t_id]['balance'] += amt
        bot.send_message(t_id, f"✅ Your deposit of {amt}$ has been approved!")
        bot.edit_message_text(f"✅ Approved {amt}$ for {t_id}", ADMIN_ID, call.message.message_id)
    else:
        bot.send_message(t_id, "❌ Your deposit request was rejected.")
        bot.edit_message_text(f"❌ Rejected for {t_id}", ADMIN_ID, call.message.message_id)

bot.infinity_polling()
