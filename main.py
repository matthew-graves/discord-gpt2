from gtts import gTTS
import discord
import sys
import conditional_sample
import time
from mutagen.mp3 import MP3

# Start Session so model doesn't have to be loaded each time
sess, context, saver, output, enc = conditional_sample.init_model()

# Run a quick sample to save time on first run
print(conditional_sample.generate_response(str("Hello!"), sess, context, saver, enc, output))

# Define Voice Chat ID | Right Click Voice Channel Name > Copy ID
vc_id = 'voice channel ID (int)'

tc_id = 'text channel ID (int)'

# Define Bot Token ID | From Discord Bot Settings 
bot_token = 'bot token'

# Create Discord Client
client = discord.Client()

# Initalize Variable for TTS wait
ttsleep = 0
# TODO: Make Keyboard Exit Actually Work | Not sure how to do this with threading
# TODO: Clean handling of multiple voice threads? Queues or something. Not familiar enough with async atm.
# TODO: Specify Desired Channel for Bot
try:
    
    # Initialize Null Voice Channel Object
    vc = None

    # On Client Event (Message)
    @client.event
    async def on_message(message):
        # get current channel
        channel = client.get_channel(vc_id)
        if message.channel.id != tc_id:
            return
        # don't respond to ourselves
        # if message.author.id == client.user.id:
        #    return

        # Simple Ping Pong Function - This probably messes with the bot as it calls on_message
        # if message.content == 'pog':
        #    await message.channel.send('pog')

        # If DC'd RE-C
        if not client.voice_clients:
            global vc
            global ttsleep
            vc = await channel.connect()

        # Wait for previous TTS to finish
        # TODO: Detect when previous TTS is finished speaking somehow
        time.sleep(ttsleep)
        ttsleep = 0
       

        # Get Generation Time
        # Generate Response via message.content
        start_time = time.time()
        response = conditional_sample.generate_response(str(message.content), sess, context, saver, enc, output)
        print(response)
        while not response:
            print("Re-running due to only whitespace being returned")
            response = conditional_sample.generate_response(str(message.content), sess, context, saver, enc, output)
        timeshort = (time.time() - start_time)

        ttsleep -= (timeshort * .90)
        # Clean response for readability as well as shorter bits of information, only take first 300 characters. 
        response = response[0:300]
        response = " ".join(response.split("\n"))
        p = response.rfind('.')
        e = response.rfind('!')
        q = response.rfind('?')
        if not response[0:int(max(p,e,q))]:
	        response = response[0:int(max(p,e,q))+1]

	# If currently speaking, stop
        if vc.is_playing():
            vc.stop()

        # Generate TTS to MP3
        tts = gTTS(text=response, lang='en')
        tts.save("text.mp3")
        audio = MP3("text.mp3")
        ttsleep += audio.info.length
        ttsleep = abs(ttsleep)
        print("Waiting " + str(ttsleep) + " seconds for TTS")

	# Play Content via Voice Channel
        vc.play(discord.FFmpegPCMAudio('text.mp3'), after=lambda e: print('done', e))
        await message.channel.send(response)

	# Connect and disconnect on start to populate and empty voice_clients list
    @client.event
    async def on_ready():
        channel = client.get_channel(vc_id)
        print('Logged in as {0.user}'.format(client))
        try:
            await channel.connect()
            voiceclients = client.voice_clients
            await voiceclients[0].disconnect()
        except IndexError as e:
            print("Not Currently Connected")

    client.run(bot_token)

except KeyboardInterrupt:
    voiceclients = client.voice_clients
    voiceclients[0].disconnect()
    exit()


