from twitchio.ext import commands, pubsub
from chat import *
from google.cloud import texttospeech_v1beta1 as texttospeech
from profanityfiltermaster import profanity_filter as profanityfilter
from twitchchatmaster.twitch_chat import *
import vlc
import os 
import time
import nltk
import creds
import re
import requests
import blocklist
import settings
import threading
import random
import elevenlabs import *
from elevenlabs.client import ElevenLabs

last_message_time_bitsMessages = 0
last_message_time_RawMessages = 0
last_message_time_keywords = 0
REDEEM_ID = settings.redeemID
CONVERSATION_LIMIT = int(settings.CONVERSATION_LIMIT)
AINAME_FIXED=settings.AINAME+":"

Version = "1.2.0" #Do not touch this line. It is used for version checking.
class Bot(commands.Bot):
 
    conversations = {}
 
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
 
        self.context_string = open_file('prompt_chat.txt');
        super().__init__(token= creds.TWITCH_TOKEN, prefix='!', initial_channels=[creds.TWITCH_CHANNEL])
        
    def version_Check(self, local_version):
        #Informs if an update is available.
        url = "https://raw.githubusercontent.com/TheSoftDiamond/Kazushin/main/version.txt"
        response = requests.get(url)
        if response.status_code == 200:
            version_online = response.text.strip()
            if local_version > version_online:
                #This case should never be passed
                print("ERROR: Kazushin Build "+Version+" is not supposed to be newer than online version. Please change the version tag back.")
            elif local_version < version_online:
                print("Kazushin Build "+Version+" is older than the online version. Consider updating your bot.")
            else:
                print("Your Kazushin Build is up to date")
        
            return version_online
        else:
            print(f"Failed to retrieve version check link data")
            return None
        
    def minmax(self, value, minvalue, maxvalue):
        #Minmax function
        recalculatedvalue = max(min(value, maxvalue), minvalue)
        return recalculatedvalue
           
    def is_between(self, value, minvalue, maxvalue):
        #Similar to minmax, but we return true or false here, but instead of forcing between two variables, tests if between two variables
        return minvalue <= value <= maxvalue
 
    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'(Version '+Version+') - Logged in as '+str(self.nick))
        if settings.doVersionCheck:
            self.version_Check(Version)
        
    def detect_cheer(self, text):
        pattern = r'cheer(\d+)' #detect messages with cheering in it
        matches = re.findall(pattern, text, re.IGNORECASE) #look for all cases of cheer messages   
        amount = 0 #Reset to 0 so that we ensure proper number counting
        for match in matches:
            if match:
                amount += int(match)  # Add the bits from this amount to the total
        has_message = bool(re.sub(pattern, '', text, flags=re.IGNORECASE).strip())  #Boolean Check if there's non-cheer text
        return amount, has_message
    
    def extract_pitch_speed(self, message):
        #pitch and speed patterns to read. This is used for Google Text to Speech.
        pattern = r'(pitch:[-\d.]+)|(speed:[-\d.]+)'

        #Find all matches in the message for these
        matches = re.findall(pattern, message)

        #Attributee to None to start
        pitch = speed = None

        pitch_match = next((match for match in matches if match[0]), None)
        speed_match = next((match for match in matches if match[1]), None)

        pitch = float(re.search(r'[-\d.]+', pitch_match[0]).group()) if pitch_match else None
        speed = float(re.search(r'[-\d.]+', speed_match[1]).group()) if speed_match else None
        return pitch, speed
    
    def remove_pitch_and_speed(self, message):
        #Cleaning time. Remove any other instaances of pitch and speed from the message, especially so it does not speak it out loud too. This is used for Google Text to Speech.
        cleaned_message = re.sub(r'(pitch:[-\d.]+)|(speed:[-\d.]+)', '', message)
        return cleaned_message.strip()

    def split_messages(self, messageChat):
        # Used to split messages for the chat messages that Kazushin responds with
        max_length = self.minmax(int(settings.globalmaximumLength),200,500)
        messages = []
        current_message = [AINAME_FIXED]
        words = messageChat.split()

        for word in words:
            if len(" ".join(current_message + [word])) <= max_length:
                current_message.append(word)
            else:
                messages.append(" ".join(current_message))
                current_message = [AINAME_FIXED, word]

        # Adding the last message
        if len(" ".join(current_message)) > len(AINAME_FIXED):
            messages.append(" ".join(current_message))

        return messages
    
    def reply_from_keyword(self, message_content, keywords_list, chance_threshold):
        # Used to determine the chance of the keyword activation being "thrown" away by the AI.
        if any(keyword in message_content for keyword in keywords_list):
            return random.randint(0, 100) < chance_threshold
        else:
            False

    def send_messages_to_chat(self, textresponse):
        #Send Messages to Chat?
        sendMessage = True
        my_chat = TwitchChat(oauth=creds.BOT_ACCOUNT_TWITCH_OAUTH, bot_name=creds.BOT_ACCOUNT_TWITCH_CHANNEL, channel_name=creds.SENDMESSAGE_TO_THIS_CHANNEL)
        messages = self.split_messages(textresponse)
    
        if sendMessage:
            [my_chat.send_to_chat(messageChat) for messageChat in messages]

    def generate_speech(self, response, user_context, CONVERSATION_LIMIT, copiedmessage, author):
        if user_context.count({ 'role': 'assistant', 'content': response }) == 0:
            user_context.append({ 'role': 'assistant', 'content': response })

        if len(user_context) > CONVERSATION_LIMIT:
            try:
                user_context.pop(1) #Pull the SECOND element only. Must be at least 1, so that AI keeps context
            except IndexError:
                print("IndexError on pop of user context")

        if string.lower(settings.chatEngine) == "google":
            # Initialize the TextToSpeechClient from the Text-to-Speech API.

            client = texttospeech.TextToSpeechClient()

            # Process the response text to create SSML for speech synthesis. For Google Text to Speech.
            ssml_text = '<speak>'
            response_counter = 0
            mark_array = []
            for s in response.split(' '):
                ssml_text += f'<mark name="{response_counter}"/>{s}'
                mark_array.append(s)
                response_counter += 1
            ssml_text += '</speak>'

            input_text = texttospeech.SynthesisInput(ssml=ssml_text)

            # Configure the voice for the speech synthesis for Google Text to Speech.
            if settings.ssmlGender.lower().strip() == "male":
                voice = texttospeech.VoiceSelectionParams(
                    language_code=settings.languageCode.strip("'"),
                    name=settings.voiceName.strip("'"),
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE,
                )
            elif settings.ssmlGender.lower().strip() == "female":
                voice = texttospeech.VoiceSelectionParams(
                    language_code=settings.languageCode.strip("'"),
                    name=settings.voiceName.strip("'"),
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=self.minmax(settings.voicePitch, -20, 20),
                volume_gain_db=self.minmax(settings.voiceGain, -96, 16),
                speaking_rate=self.minmax(settings.voiceRate, 0.25, 4),
                sample_rate_hertz=self.minmax(settings.voiceHertz, 8000, 48000)
            )
            if (settings.listenForAudioEvent and author in settings.listOfUsersAudioEvent) or (settings.listenForAudioEvent and settings.globalAudioEventMode):
                thepitch, thespeed = self.extract_pitch_speed(copiedmessage)
                try:
                    if not self.is_between(thepitch, -20, 20):
                        thepitch=settings.voicePitch
                except TypeError:
                    thepitch=settings.voicePitch
                try:
                    if not self.is_between(thespeed, 0.25, 4):
                        thespeed=settings.voiceRate
                except TypeError:
                    thespeed=settings.voiceRate
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    pitch=self.minmax(thepitch, -20, 20),
                    volume_gain_db=self.minmax(settings.voiceGain, -96, 16),
                    speaking_rate=self.minmax(thespeed, 0.25, 4),
                    sample_rate_hertz=self.minmax(settings.voiceHertz, 8000, 48000)
                )


            # Use the Text-to-Speech client to synthesize speech from the input text.
            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config, "enable_time_pointing": ["SSML_MARK"]}
            )

        if string.lower(settings.chatEngine) == "elevenlabs" or "eleven":
            #client = ElevenLabs(api.key=creds.ELEVANLABS_API_KEY)

            elevensettings = VoiceSettings(speaking_rate=self.minmax(settings.elevenSpeakingRate, 0, 4), stability=settings.elevenStability, similarity_boost=settings.elevenSimilarityBoost, style=settings.elevenStlye, use_speaker_boost=settings.elevenSpeakerBoost) 
            audio = generate(
                text=response,
                voice=Voice(
                    voice_id='settings.elevenVoiceID',
                    settings=VoiceSettings(settings=elevensettings)
                )
            )

        # Save the generated audio content to a file and play it using VLC.
        if settings.playAudio:
            if string.lower(settings.chatEngine) == "google":
                with open("output.mp3", "wb") as out:
                    out.write(response.audio_content)

                audio_file = os.path.dirname(__file__) + '/output.mp3'
                media = vlc.MediaPlayer(audio_file)
                media.play()
            if string.lower(settings.chatEngine) == "elevenlabs" or "eleven":
                with open("output.mp3", "wb") as out:
                    out.write(audio)

                audio_file = os.path.dirname(__file__) + '/output.mp3'
                media = vlc.MediaPlayer(audio_file)
                media.play()
        

            # Generate and save a transcript of the speech with timing information.

            count = 0
            current = 0
            for i in range(len(response.timepoints)):
                count += 1
                current += 1
                with open("output.txt", "a", encoding="utf-8") as out:
                    out.write(mark_array[int(response.timepoints[i].mark_name)] + " ")
                if i != len(response.timepoints) - 1:
                    total_time = response.timepoints[i + 1].time_seconds
                    time.sleep(total_time - response.timepoints[i].time_seconds)
                if current == 25:
                    open('output.txt', 'w', encoding="utf-8").close()
                    current = 0
                    count = 0
                elif count % 7 == 0:
                    with open("output.txt", "a", encoding="utf-8") as out:
                        out.write("\n")
            time.sleep(2)
            open('output.txt', 'w').close()

            # Remove the generated audio file and print some information.

            os.remove(audio_file)

        print('------------------------------------------------------')
        
    async def run_methods_concurrently(self, textresponse, response, user_context, CONVERSATION_LIMIT, copiedmessage, author):
        thread1 = threading.Thread(target=self.generate_speech, args=(response, user_context, CONVERSATION_LIMIT, copiedmessage, author))
        thread2 = threading.Thread(target=self.send_messages_to_chat, args=(textresponse,))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    async def event_message(self, message):
        global last_message_time_bitsMessages, last_message_time_RawMessages, last_message_time_keywords
        copiedmessage = message.content
        currentTimeBits = time.time()
        currentTimeMsg = time.time()
        currentTimeKeywords = time.time()
        cooldownBits = int(settings.cooldownBits)
        cooldownMsg = int(settings.cooldownMsg)
        cooldownKeywords = int(settings.cooldownKeywords)
        pfilter = profanityfilter.ProfanityFilter()
        cheer_pattern = re.compile(r'cheer(\d+)')
        bitsAmount2, has_message2 = self.detect_cheer(message.content)
        didKeywordWork = self.reply_from_keyword(message.content, settings.keywordsinUserMsg, settings.keywordsinUserChance)
        if settings.doBits:
            bitsAmount, has_message = self.detect_cheer(message.content)
        if message.echo:
            return
        if settings.listenForAudioEvent:
            message.content = self.remove_pitch_and_speed(message.content)
        if (settings.doBits and (message.author.name not in blocklist.blocked_names and has_message) and int(settings.bitsLookAtLowNumber) <= bitsAmount <= int(settings.bitsLookAtHighNumber)) and (currentTimeBits - last_message_time_bitsMessages < cooldownBits):
            time_leftBits = int(cooldownBits - (currentTimeBits - last_message_time_bitsMessages))
            the_chat = TwitchChat(oauth=creds.BOT_ACCOUNT_TWITCH_OAUTH, bot_name=creds.BOT_ACCOUNT_TWITCH_CHANNEL, channel_name=creds.SENDMESSAGE_TO_THIS_CHANNEL)
            the_chat.send_to_chat(message.author.name+". this command has a cooldown time of "+str(cooldownBits)+ " seconds. You must wait "+str(time_leftBits)+" seconds.") 
            return
        if (settings.doRawMessages and (message.author.name not in blocklist.blocked_names) and message.content.startswith(settings.prefix+settings.detectMSGName)) and (currentTimeMsg - last_message_time_RawMessages < cooldownMsg):
            time_leftMsg = int(cooldownMsg - (currentTimeMsg - last_message_time_RawMessages))
            the_chat = TwitchChat(oauth=creds.BOT_ACCOUNT_TWITCH_OAUTH, bot_name=creds.BOT_ACCOUNT_TWITCH_CHANNEL, channel_name=creds.SENDMESSAGE_TO_THIS_CHANNEL)
            the_chat.send_to_chat(message.author.name+". this command has a cooldown time of "+str(cooldownMsg)+ " seconds. You must wait "+str(time_leftMsg)+" seconds.") 
            return

        if (settings.doKeywords and (message.author.name not in blocklist.blocked_names) and message.author.name != creds.BOT_ACCOUNT_TWITCH_CHANNEL.lower() and (message.tags.get('custom-reward-id') is None and not cheer_pattern.search(message.content))):
            if ((any(keyword in message.content for keyword in settings.keywordsinUserMsg)) and ((currentTimeKeywords - last_message_time_keywords) < cooldownKeywords)):
                time_leftKeywords = int(cooldownKeywords - (currentTimeKeywords - last_message_time_keywords))
                print(message.author.name+" attempted to run a keywords detected message, but cooldown is at "+str(time_leftKeywords)+" seconds left.")
                return
        if (not didKeywordWork and (message.author.name not in blocklist.blocked_names)) and any(keyword in message.content for keyword in settings.keywordsinUserMsg) and message.author.name != creds.BOT_ACCOUNT_TWITCH_CHANNEL.lower() and (message.tags.get('custom-reward-id') is None and not cheer_pattern.search(message.content)):
            print(message.author.name+" attempted a keyworded message, but random chance said no.")
            return
        #Begin AI Generation of Messages Below 
        if (
            (settings.doRedeem and message.tags.get('custom-reward-id') == REDEEM_ID) or
            (settings.doBits and has_message and int(settings.bitsLookAtLowNumber) <= bitsAmount <= int(settings.bitsLookAtHighNumber)) or
            (settings.doRawMessages and message.content.startswith(settings.prefix+settings.detectMSGName)) or
            (settings.doKeywords and self.reply_from_keyword(message.content, settings.keywordsinUserMsg, settings.keywordsinUserChance) and message.author.name != creds.BOT_ACCOUNT_TWITCH_CHANNEL.lower() and (message.tags.get('custom-reward-id') is None or not (cheer_pattern.search(message.content))))
        ):
            if settings.blockList: 
                if message.author.name in blocklist.blocked_names:
                    print("Blocked User "+message.author.name+" attempted to interact with bot")
                    return
            if settings.doProfanityCheck and pfilter.isProfane(message.content):
                print("Filter went off by "+message.author.name+": "+message.content) #Log the user and message that triggered the profanity filter
                return
            theusername = message.author.name
            themessage = message.content
            print(f'Redemption by {message.author.name}: {message.content}')
            # Check if the message is too long or short for the AI to handle
            if len(message.content) > 500 or len(message.content) < abs(int(settings.globalminimumLength)):
                return
            
            print('------------------------------------------------------')


            if message.author.name not in Bot.conversations:
                Bot.conversations[message.author.name] = []
                user_context = Bot.conversations[message.author.name]
                if settings.useUserPrompt:
                    #Runs only if Per User Prompt setting enabled in settings.py
                    usernamefield = message.author.name
                    userpromptsfolder = os.path.join(os.path.dirname(__file__), "userprompts")
                    thisUserPrompt = os.path.join(userpromptsfolder, f"{usernamefield}_prompt.txt")
                    print("Expecting User File @ "+thisUserPrompt+"\n")
                    if os.path.exists(thisUserPrompt):
                        #File found case (User Prompt Mode)
                        print("File found. Using "+thisUserPrompt+" context\n")
                        thisUserString = open_file(thisUserPrompt)
                        user_context.append({ 'role': 'system', 'content': thisUserString })
                    else:
                        #File not found case (Default context)
                        print("File not found. Using default user context instead.")
                        user_context.append({ 'role': 'system', 'content': self.context_string })
                else:
                    #Runs if Per User Prompt Mode is disabled in settings.py
                    user_context.append({ 'role': 'system', 'content': self.context_string })
            user_context = Bot.conversations[message.author.name]
            
            print(user_context)
    
            content = message.content.encode(encoding='ASCII',errors='ignore').decode()
            user_context.append({ 'role': 'user', 'content': theusername+" said: "+content })
            
            try:
                response = gpt3_completion(user_context)
            except openai.error.InvalidRequestError as e:
                errormsg = str(e)
                if "tokens" in errormsg:
                    Bot.conversations[message.author.name] = [] #Wipe User Messages if token limit reached
                    user_context = Bot.conversations[message.author.name] #Redeclare user context
                    if settings.useUserPrompt:
                        usernamefield = message.author.name
                        userpromptsfolder = os.path.join(os.path.dirname(__file__), "userprompts")
                        thisUserPrompt = os.path.join(userpromptsfolder, f"{usernamefield}_prompt.txt")
                        if os.path.exists(thisUserPrompt):
                            thisUserString = open_file(thisUserPrompt)
                            user_context.append({ 'role': 'system', 'content': thisUserString }) #Readd context string from file
                        else:
                            user_context.append({ 'role': 'system', 'content': self.context_string }) #Readd context string from default
                    else:
                        user_context.append({ 'role': 'system', 'content': self.context_string }) #Readd context string from default
                    user_context.append({ 'role': 'user', 'content': theusername+" said: "+content })
                    response = gpt3_completion(user_context) #Retry the question after readding context

            print(AINAME_FIXED , response)
            
            # Copied for text chat response reasons below
            textresponse = response
 
            await self.run_methods_concurrently(textresponse, response, user_context, CONVERSATION_LIMIT, copiedmessage, message.author.name)
            last_message_time_bitsMessages = currentTimeBits
            last_message_time_RawMessages = currentTimeMsg
            last_message_time_keywords = currentTimeKeywords

            
            # Since we have commands and are overriding the default `event_message`
            # We must let the bot know we want to handle and invoke our commands...
            await self.handle_commands(message)
 
    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.
 
        # Send a hello back!
        # Sending a reply back to  the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')
 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds.GOOGLE_JSON_PATH
elevenlabs.set_api_key(os.getenv("ELEVENLABS_API_KEY"))
bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
