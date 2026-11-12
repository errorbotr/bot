import telebot, json, os, time

TOKEN = "9108484453:AAExGYmzYxZcP42zdfFdUUN16HkmlgSYll0"
ADMIN_IDS = [7344860026, 1087968824]
ADMIN_ID = 7344860026
CHANNEL = "@aarrttyygmd"

bot = telebot.TeleBot(TOKEN)
DB = "users.json"

def load():
    if os.path.exists(DB):
        try:
            x=json.load(open(DB))
            return x if isinstance(x, dict) else {}
        except:
            return {}
    return {}

def save(d):
    json.dump(d, open(DB, "w"))

def get_user(uid):
    d = load()
    uid = str(uid)
    if uid not in d:
        d[uid] = {"coins": 0, "warns": 0, "banned": False}
        save(d)
    return d[uid]

def is_admin(uid):
    return uid in ADMIN_IDS

def is_group_admin(uid, chat_id):
    if uid in ADMIN_IDS:
        return True
    try:
        m = bot.get_chat_member(chat_id, uid)
        return m.status in ["administrator", "creator"]
    except:
        return False

def check_join(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=["start"])
def start(m):
    if m.chat.type != "private":
        return
    if not is_admin(m.from_user.id) and not check_join(m.from_user.id):
        bot.reply_to(m, f"Join first: {CHANNEL}")
        return
    bot.reply_to(m, "Bot is working. Send /admin")

@bot.message_handler(commands=["id"])
def id_cmd(m):
    bot.reply_to(m, f"Your ID: {m.from_user.id}")

@bot.message_handler(commands=["admin"])
def admin_cmd(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "You are not the king!")
        return
    bot.reply_to(m, "/id - your id\n/warn - reply to warn\n/ban - reply to ban\n/addme 1000 - add coins\n/give 123 100 - give coins")

@bot.message_handler(commands=["addme"])
def addme(m):
    if not is_admin(m.from_user.id):
        return
    try:
        amount = int(m.text.split()[1])
    except:
        amount = 1000
    d = load()
    u = get_user(m.from_user.id)
    u["coins"] += amount
    d[str(m.from_user.id)] = u
    save(d)
    bot.reply_to(m, f"Added {amount} coins. Total: {u['coins']}")

@bot.message_handler(commands=["give"])
def give(m):
    if not is_admin(m.from_user.id):
        return
    try:
        parts = m.text.split()
        target = parts[1]
        amount = int(parts[2])
        d = load()
        u = get_user(target)
        u["coins"] += amount
        d[str(target)] = u
        save(d)
        bot.reply_to(m, f"Gave {amount} to {target}")
    except:
        bot.reply_to(m, "Use: /give ID amount")

@bot.message_handler(commands=["warn"])
def warn(m):
    if not is_group_admin(m.from_user.id, m.chat.id):
        bot.reply_to(m, "Admins only!")
        return
    if not m.reply_to_message:
        bot.reply_to(m, "Reply to a message to warn")
        return
    target = m.reply_to_message.from_user.id
    if target in ADMIN_IDS:
        bot.reply_to(m, "Cannot warn the king!")
        return
    d = load()
    u = get_user(target)
    u["warns"] += 1
    d[str(target)] = u
    save(d)
    bot.reply_to(m, f"Warning {u['warns']}/3 for {m.reply_to_message.from_user.first_name}")
    if u["warns"] >= 3:
        try:
            bot.ban_chat_member(m.chat.id, target)
            bot.reply_to(m, "Banned after 3 warns")
        except:
            bot.reply_to(m, "Cannot ban, make bot admin")

@bot.message_handler(commands=["ban"])
def ban(m):
    if not is_group_admin(m.from_user.id, m.chat.id):
        bot.reply_to(m, "Admins only!")
        return
    if not m.reply_to_message:
        return
    try:
        bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
        bot.reply_to(m, "Banned")
    except:
        bot.reply_to(m, "Make bot admin first")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    if m.chat.type != "private":
        return
    if m.text == "7":
        bot.reply_to(m, "Game 7")
        return
    bot.reply_to(m, f"You said: {m.text}")

print("Bot running")
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Retrying...")
        time.sleep(5)
