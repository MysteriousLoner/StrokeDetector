import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv

#env config 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#set up gemini

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction="You will be a key component in a discord bot. I will be passing in conversations into your prompt with date and time so that you can keep track of its sequence. A normal log will look like this: \"Message ID: 1248288083607158926 | User: razette | message: hi | time: 2024-06-06 14:51:11.203000+00:00\" output and if its a reply to an earlier message, it will look like this: \"Message ID: 1248288104566095903 | User: razette replied to: dummydumbdumb At message with ID: 1248288085519765585 | message: hi | time: 2024-06-06 14:51:16.200000+00:00\" when User dummydumbdumb or User razette is detected to be complimenting another, output \"compliment\". Output \"normal\" if it is a normal conversation. Sacarstic compliments that sound like a complain like \"Why you so pro?\" can also be counted as a compliment. Remember, you are given an entire log of conversations, remember to check the entire log to get the context of the conversation. Most importantly, only output compliment when User dummydumbdumb is complimenting User razette and vice versa.",
)

chat_session = model.start_chat()

#intents
intents = discord.Intents.default()
intents.message_content=True

#setup client
client = discord.Client(intents=intents)

#set up variables
string_list = [''] * 30
count = 0

#utility functions
def insert_string(new_string):
    # Shift existing strings up by 1
    for i in range(len(string_list) - 1):
        string_list[i] = string_list[i + 1]
    # Insert the new string at the end
    string_list[-1] = new_string

def get_list_as_string():
    # Join all strings in the list with a newline character as a delimiter
    list_as_string = '\n'.join(string_list)
    return list_as_string

#discord client functions
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("Bot is connected to the following servers: " + str(client.guilds))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.author) == "razette" or str(message.author) == "dummydumbdumb":
        await message.reply('hello world')
    if message.reference is not None:
        # This message is a reply
        replied_to_message_id = message.reference.message_id

        try:
            replied_to_message = await message.channel.fetch_message(replied_to_message_id)
            original_author = replied_to_message.author

            # Now you have the user object (original_author) of who the message was replying to
            await message.channel.send(f"You replied to {original_author}")

        except discord.NotFound:
            await message.channel.send("Couldn't find the original message (might be deleted).")
    else:
        # This message is not a reply
        original_author = None
        pass
    if message.content:
        if original_author:
            formatted_message = "Message ID: " + str(message.id) + " | User: " + str(message.author) + " replied to: " + str(original_author) + " At message with ID: " + str(replied_to_message_id) + " | message: " + message.content + " | time: " + str(message.created_at)
            print(formatted_message)
            insert_string(formatted_message)
        else:
            formatted_message = "Message ID: " + str(message.id) + " | User: " + str(message.author) + " | message: " + message.content + " | time: " + str(message.created_at)
            print(formatted_message)
            insert_string(formatted_message)
        list_as_string = get_list_as_string()
        print(list_as_string)
        response = chat_session.send_message(list_as_string)
        print(response.text)
        if "compliment" in str(response.text):
            # await message.reply("compliment")
            count += 1
            await message.reply("Number of times Ding and Eulee suck each other off: " + str(count))
        elif "normal" in str(response.text):
            # await message.reply("normal")
            pass
client.run(TOKEN)