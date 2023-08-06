# interstitial_API:

interstitial_API is a tiny relay API script powered by FastAPI, with a few nifty use cases:

1. To apply custom prompt formatting (prefix, suffix, special tokens, etc.) on messages, or inject additional messages, before they are provided to the local model. This is particularly useful when chatting with models that require specific character escape sequences to demarcate user from assistant messages, without which they tend to auto-complete user input or carry on conversations with themselves. By default the will prefixes all user messages with ### Instruction: and every assistant response with ### Response: but these can be readily changed to suit a given model's requirements.

2. For remote API access over. Most LLM platforms allow http://localhost access only. Interstitial_API can be configured to allow external access with a command flag (caution, this is not recommended unless you understand the risks). More importantly, it is a great solution for remote API calls over https without increasing WAN security threats or local attack surface, via zero-trust platforms like Cloudflare, remote proxies like Nginx, and virtual local area networks like Tailscale and Zerotier. Doing so protects your API calls from snooping eyes, enables granular remote user access control, and allows untethering models from webservers and WAN exposure, or theoretically tethering models together, integrating with webhooks and whatnot.

3. To extend the API endpoints of existing Alarge language model tools--either to bolster compatibility with UIs and other tools that were designed for other platforms (e.g. third party ChatGPT web interfaces)--or to link multiple offsite models through a single API domain (e.g. /v1/chat goes to one model, /v1/chat/completions goes to another, and so on).

Interstitial_API is quite lightweight and should not add any measurable load to your workstation, while its nimble asynchronous backbone should keep up with whatever you throw at it. Under continual use (granted by a single client querying one endpoint at a time, but ), I never saw it exceed 1.5% of a single CPU thread, or ~300MB memory, on an M1 Max during testing with or more than 65MB of total RAM use while relaying continuous API calls to an LM Studio server. If you're in a position to really stress test it, please do and report back.


## CONFIGURATION AND USE

Note these instructions are generally for MacOS but can be adapted to your OS... just ask your model to translate them for you :)

### 1. **Install the prerequisites**

You should have Python 3.7 or higher installed on your system. Linux users should have it already or else know how to get it, Mac and Windows users can download Python from [the official website](https://www.python.org/downloads/). Mac users can also get it using Homebrew if they prefer:

```bash
brew install python
```

Download and save interstitial_API.py, start_interstitial_API.sh, and requirements.txt to a local folder.

Navigate your way to this folder, (e.g. using `cd` in the Terminal). 

You'll need to `chmod` interstitial_API.py on MacOS, as well as interstitial_API.sh if you intend to run it without keeping Terminal open (see #5)--may as well do that now:

```bash
    chmod +x interstitial_API.py && chmod +x start_interstitial_API.sh
```

Optional step but recommended if you have multiple Python projects: create a Python virtual environment with the following:

```bash
python3 -m venv llamapen (choose your own name)
(on MacOS or Linux:) source llamapen/bin/activate
(on Windows:) llamapen\Scripts\activate
```

Whether or not you created a virtual environment, to install the necessary dependencies run one of the following pip commands:

```bash
pip install -r requirements.txt

*** or ***

pip install fastapi uvicorn httpx
```

Note: here and throughout, Mac users may have to use pip3 instead of pip, depending on how they installed Python.



### 4.     **(Test) Run the API server**

You should be able to now run the relay API using `uvicorn`:

```bash
uvicorn interstitial_API:app --port 3456
```

This will start an API at localhost:3456 that by default relays queries it receives at /v1/favicon, /v1/models, and /v1/chat/completions to the corresponding endpoints at localhost:6789 (i.e. the default configuration on LM Studio).

If your destination API is on a different port and/or not http://localhost, these changes are readily made within the .py file in your preferred code editor.

*A note of caution: by adding `--host 0.0.0.0` to the end of the uvicorn command, you not only open the relay API to queries originating from elsewhere including potentially from WAN depending on your router's configuration, you also open the port you've specified on your computer itself, including potentially to WAN security threats. Use this command only with extreme caution if you know exactly what you are doing, the risks, and your network configuration. The vast majority of people who might want remote API access will have a much better time using any of a number of free tools like Cloudflare Zero Trust, Tailscale, ZeroTier, Netmaker, Yggdrasil, WireGuard, a local VPN server, etc.

To test the relay, try calling it from your UI of choice. (I personally like the features and UIs of ChatWizard, slickgpt, chat-with-gpt, chatbot-ui, and big-agi, but as of this writing all except ChatWizard require some minor changes to their code). 

If you're looking to dabble in more complex API configurations and develop this yourself, I highly recommend getting an API testing app. 

For a quick and dirty connectivity test you could also simply curl the API from Terminal, but note it won't stream responses:

```bash
curl http://localhost:6789/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Why is \"What Is To Be Done?\" by V.I. Lenin still worth reading today?"}],
    "temperature": 0.7,
    "max_tokens": -1
  }'
```

### 5.   **(Optional) Keep interstitial_API running without Terminal open**

If you don't want to have to keep a terminal window open in order to run uvicorn, here are some quick optional additional steps you can take: download `start_interstitial_API.sh` from git hub if you haven't already, or recreate its two lines of code yourself using text editor of choice, or the following Terminal commands (after `cd` navigating to your folder with `interstitial_API.py`):

```bash
    sudo touch start_insterstitial_API.sh

    nano start_interstitial_API.sh
        *or*
    vim start_interstitial_API.sh

```

start_insterstitial_API.sh should contain two lines of text:
```
    #!/bin/bash
    nohup python /path_to_your_script.sh/interstitial_API.py > /dev/null 2>&1 &
 ```

*Note, if you create this script using a text editing app, make sure it's actually saved as a .sh file and doesn't end with, for example, .sh.txt. If your OS hides file extensions, the easiest way to know it saved correctly is when it doesn't want to open in text editors anymore.*

Once you have the .sh script file in your folder, chmod it in Terminal if you haven't already and run it:

```bash
    chmod +x start_interstitial_API.sh
    ./start_interstitial_API.sh
```

Once you run the script, the relay should run quietly in the background even after you've closed Terminal until you either reboot your computer or manually kill the uvicorn process (see #7 for instructions).


### 6.     **(Optional) Keep interstitial_API running through MacOS reboots**
   
If you really want to "set it and forget it" (see another note of caution below) you can also have MacOS load the .sh script silently whenever you log on:

a. Open "System Preferences" and find "Login Items" within "General" (or within "Users & Groups, then your user account, on older MacOS versions).

b. Click on the '+' button to add a new login launch item.

c. Navigate to your script folder and select `start_interstitial_API.sh` and to add it.

Now your script should run each time you log into your macOS user account.

*It's worth noting how easy it actually is to "set and forget" a lightweight niche purpose script like this—-with no UI to remind you of its presence--only to forget all about it someday. That itself *hopefully* wouldn't become a security liabiliy over time, but it's never a great idea to run outdated software if you're not using it.... unless you *also* chose to open a port on your computer for the API, in which case there's a high likelihood of it becoming a very big problem for you it's all but certain to become a big problem for you. For the love of all that is good, do not combine these two options. You've been warned.*

### 7. Kill interstitial_API

To stop interstitial_API, enter the following in Terminal:

```bash
kill -9 $(ps aux | grep '[i]nterstitial_API:app' | awk '{print $2}')
```

If that for whatever reason doesn't work, you can find the PID number yourself in the second column of ps aux | grep 'interstitial_API' or otherwise uvicorn if you renamed the script, and `kill [PID]`

## **MODIFICATIONS**

As noted you can simply edit your local `interstitial_API.py` to change the server or port of the destination API, at line 23.

To edit system messages injected before after assistant and user messages, edit the text on lines 54 and 55, respectively. 

I have them set to ### Instruction: and ### Response:  which are common on llama models, but check your model's card on HuggingFace if it isn't behaving as expected.

Next up for this script are to add environment variables (server, port, system prompt messages) for faster customization without opening the scripts themselves.
