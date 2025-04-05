import os
import nest_asyncio
from pyrogram import Client, filters
import asyncio

# Necesario para Google Colab
nest_asyncio.apply()

# Configuración del bot a través de variables de entorno
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN"))

# Archivo para almacenar los datos de los usuarios
USER_FILE = "user_ids.txt"

app = Client("anon_bot3", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Diccionario para manejar usuarios y apodos
user_data = {}

# Cargar datos de usuarios desde el archivo al iniciar
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        for line in f:
            user_id, nickname = line.strip().split(",")
            user_data[int(user_id)] = nickname


def save_user_data():
    """Guardar los datos de los usuarios en el archivo."""
    with open(USER_FILE, "w") as f:
        for user_id, nickname in user_data.items():
            f.write(f"{user_id},{nickname}\n")


async def find_user_file(client):
    """Buscar el archivo user_ids.txt en el historial del chat del admin."""
    async for message in client.get_chat_history(ADMIN_ID):
        if message.document and message.document.file_name == USER_FILE:
            return message.document.file_id
    return None


async def send_user_file(client):
    """Enviar el archivo al administrador, borrar el anterior y reemplazarlo."""
    existing_file_id = await find_user_file(client)
    if existing_file_id:
        await client.delete_messages(ADMIN_ID, [existing_file_id])  # Eliminar el archivo anterior

    # Enviar el archivo actualizado
    if os.path.exists(USER_FILE):
        await client.send_document(ADMIN_ID, USER_FILE)
        os.remove(USER_FILE)  # Eliminar el archivo local después de enviar


@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    user_nick = f"User{user_id}"  # Nickname predeterminado

    if user_id not in user_data:
        user_data[user_id] = user_nick
        save_user_data()
        await send_user_file(client)

    await message.reply(f"¡Bienvenido! Has sido añadido a la lista como {user_data[user_id]}.")


@app.on_message(filters.command("leave") & filters.private)
async def leave_command(client, message):
    user_id = message.from_user.id

    if user_id in user_data:
        user_data.pop(user_id)  # Eliminar al usuario
        save_user_data()
        await send_user_file(client)  # Enviar el archivo actualizado al admin
        await message.reply("Has salido de la lista correctamente.")
    else:
        await message.reply("No estás registrado en la lista.")


@app.on_message(filters.command("nick") & filters.private)
async def change_nick_command(client, message):
    user_id = message.from_user.id
    new_nick = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if new_nick:
        if user_id in user_data:
            user_data[user_id] = new_nick  # Actualizar el apodo
            save_user_data()
            await send_user_file(client)  # Enviar el archivo actualizado al admin
            await message.reply(f"Tu apodo ha sido actualizado a {new_nick}.")
        else:
            await message.reply("No estás registrado. Usa /start para registrarte primero.")
    else:
        await message.reply("Por favor, incluye un apodo. Ejemplo: /nick NuevoApodo.")


async def run_bot():
    async with app:
        print("Bot en ejecución...")
        await asyncio.Future()  # Mantener la tarea en ejecución indefinidamente


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
