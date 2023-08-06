# interstitial_API:
**A RELAY FOR LM STUDIO API CALLS WITH PROMPT INJECTION**

interstitial_API allows two things:

1. inject system prompts in between user and assistant messages, to stop the AI from auto-completing user messages or carrying on a conversation with itself.

2. the use of partially-OpenAI-compatible APIs that do not have fully defined endpoints (e.g. they are missing /v1/models).

It is lightweight and designed to be run on the same system where the models are actually run. On my MacBook M1 Max it uses ~1.5% of a single CPU thread under load and never has used more than 0.1% of my 64GB of system memory.

To set it up on your machine, read on. Note these instructions are generally for Mac but can be adapted to your OS... just ask your model to translate it for you :)


## STEPS

### 1. **Install the prerequisites**

You should have Python 3.7 or higher installed on your system. Linux users should have it already or else know how to get it, Mac and Windows users can download Python from [the official website](https://www.python.org/downloads/). Mac users can also get it using Homebrew if they prefer:

```bash
    brew install python
```

`cd` to the folder containing interstitial_API.py, and run 

```bash
pip install -r requirements.txt
```

(here and throughout, you may need to use pip3 on MacOS depending on how you installed Python).


### 2.     **Install the required packages**

You can install the necessary Python packages using pip, the Python package installer. Run the following command to install the requirements:

```bash
    pip install fastapi uvicorn httpx
```


### 3.     **chmod +x interstitial_API.py .**

Locate/store interstitial_API in a sensible folder on your computer (somewhere within your home folder).

You'll need to `chmod` interstitial_API.py on MacOS, as well as interstitial_API.sh if you intend to run it without keeping Terminal open (see #5)

```bash
    chmod +x interstitial_API.py && chmod +x start_interstitial_API.sh
```


### 4.     **(Test) Run the API server**

You can now run the relay server using `uvicorn` with the following command:

    ```bash
    uvicorn interstitial_API:app --port 3456
    ```

*Note: you can add `--host 0.0.0.0` to allow other machines / IPs access, but be careful with this function especially if your router exposes your machine to incoming WAN traffic. Consider using Tailscale or Cloudflare Zero Trust for safe(r) remote access.*

If you rename the file, modify the command but omit the .py for purposes of uvicorn.

You should now be able to access the API at `localhost:3456`, and it will relay to `localhost:6789` (e.g. the port used by LM Studio). 

If you need to use a different port, or an address other than localhost, simply edit the relevant lines in the .py file.

To test the relay, try calling it from your UI of choice (I recommend ChatWizard, slickgpt, chat-with-gpt, or big-agi, personally, but all of these except ChatWizard require some code hacks, a subject of a future addtion to this repo). Or use a free API testing app. Or you simply curl it from the command line, but note it won't stream:

```bash
curl http://localhost:6789/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Why is \"What Is To Be Done?\" by V.I. Lenin still worth reading today?"}],
    "temperature": 0.7,
    "max_tokens": -1
  }'
```

### 5.     **Make it run without a terminal open**

If you don't want to have to keep a terminal open running uvicorn, grab `start_interstitial_API.sh` or recreate it yourself with the following: 

```bash
    #!/bin/bash
    nohup python /path_to_your_script/interstitial_API.py > /dev/null 2>&1 &
 ```

*MacOS users may need to use python3 instead of python*

Once you've saved your script in your home folder, chmod it in Terminal if you haven't already:

```bash
    chmod +x start_interstitial_API.sh
```

Now you can run that script once in Terminal with `./start_interstitial_API.sh` and the relay should remain alive after you close Terminal until you reboot or otherwise kill it (see #7)


### 6.     **(Optional) Start the relay when you log into your Mac**
   
To further reduce friction with the script you can set your Mac to quietly load it on login, ensuring the API is always up unless you manually kill it:

a. Open "System Preferences" and find "Login Items" within "General" (or within "Users & Groups" > your user account on older versions of MacOS).

b. Click on the '+' button to add a new login item.

c. Navigate to `start_interstitial_API.sh` and select it and click "Add".

Now your script should run each time you log into your macOS user account.


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
