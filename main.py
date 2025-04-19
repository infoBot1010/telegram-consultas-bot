from telethon import TelegramClient, events
from telethon.tl.custom import Button
import asyncio
import os

# Suas credenciais
api_id = 24410646
api_hash = '94f34e67625502bc30c3aa29cf49fab7'
phone_number = '5581995483906'

# Sessão
session_dir = '/home/runner/workspace/replit_session'
if not os.path.exists(session_dir):
    os.makedirs(session_dir)

client = TelegramClient(f'{session_dir}/session_name', api_id, api_hash)

# IDs dos grupos
grupo_consultas_vip = 1002640635480
grupo_adm = 1002344973122

# Iniciar cliente
async def main():
    await client.start(phone_number)
    print("Bot conectado com sucesso!")

# Função para enviar as instruções de como usar os comandos
async def enviar_instrucoes(event):
    texto_instrucoes = """
    👋 Seja bem-vindo ao sistema de consultas!

📘 COMO USAR OS COMANDOS

/cpf 00000000000  
/email exemplo@email.com  
/telefone 11988887777  
/nome JOAO DA SILVA  
/cnpj 00000000000000  
/placa ABC1D23  
/pix JOAO DA SILVA /123456

Exemplo de pix: /pix JOAO DA SILVA /123456  
(Use os 6 dígitos do meio do CPF do dono da chave Pix)
    """
    await client.send_message(
        event.chat_id,
        texto_instrucoes,
        buttons=[Button.inline("Como Usar", data="comousar")]
    )

# Toda mensagem recebida no grupo Consultas_vip será enviada ao grupo ADM
@client.on(events.NewMessage(chats=grupo_consultas_vip))
async def encaminhar_para_adm(event):
    try:
        message = event.message
        if message.text:
            await client.send_message(grupo_adm, message.text)
        elif message.media:
            await client.send_file(grupo_adm, file=message.media, caption=message.text or "")
    except Exception as e:
        print(f"Erro ao encaminhar comando para ADM: {e}")

# Toda resposta no grupo ADM será filtrada e enviada ao grupo Consultas_vip
@client.on(events.NewMessage(chats=grupo_adm))
async def encaminhar_para_consultas_vip(event):
    try:
        message = event.message

        # Filtrar texto
        if message.text:
            linhas = message.text.splitlines()
            linhas_filtradas = [
                linha for linha in linhas
                if all(palavra not in linha for palavra in ["CLIQUE PARA VER", "USUÁRIO:", "BY:", "Canal:"])
            ]
            texto_final = "\n".join(linhas_filtradas).strip()
        else:
            texto_final = ""

        # Verificar se há arquivo
        if message.media:
            file = await client.download_media(message)
            await client.send_file(grupo_consultas_vip, file, caption=texto_final)
        else:
            if texto_final:
                await client.send_message(grupo_consultas_vip, texto_final)

    except Exception as e:
        print(f"Erro ao encaminhar resposta para Consultas_vip: {e}")

# Função que responde ao clique no botão de "Como Usar"
@client.on(events.CallbackQuery)
async def callback(event):
    if event.data == b"comousar":
        await enviar_instrucoes(event)

# Detecta quando um novo participante entra no grupo
@client.on(events.ChatAction)
async def novo_participante(event):
    if event.user_added or event.user_joined:
        try:
            # Envia as instruções quando um novo usuário entra no grupo
            await enviar_instrucoes(event)
        except Exception as e:
            print(f"Erro ao enviar mensagem inicial para novo participante: {e}")

# Executar bot
try:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
except Exception as e:
    print(f"Erro na execução do bot: {e}")
