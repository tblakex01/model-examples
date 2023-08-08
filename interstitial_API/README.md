# interstitial_API

interstitial_API is a tiny relay API script powered by FastAPI, with a few nifty use cases:

1. To apply custom prompt formatting (prefix, suffix, special tokens, etc.) on messages, or inject additional messages, before they are provided to the local model. This is particularly useful when chatting with models that require specific character escape sequences to demarcate user from assistant messages, without which they tend to auto-complete user input or carry on conversations with themselves. By default the will prefixes all user messages with ### Instruction: and every assistant response with ### Response: but these can be readily changed to suit a given model's requirements.

2. For remote API access. Most LLM platforms allow http://localhost access only. Interstitial_API can be configured to allow external access with a command flag (caution, this is not recommended unless you understand the risks discussed below enough to accept them). More importantly, it is a great solution for remote API calls over https without increasing WAN security threats or local attack surface, via zero-trust platforms like Cloudflare, remote proxies like Nginx, and virtual local area networks like Tailscale and Zerotier. Doing so protects your API calls from snooping eyes, enables granular remote user access control, and allows untethering models from webservers and WAN exposure, or theoretically tethering models together, integrating with webhooks and whatnot.

3. To extend the API endpoints of existing large language model tools--either to bolster compatibility with UIs and other tools that were designed for other platforms (e.g. third party ChatGPT web interfaces), or to link multiple offsite models through a single API domain (e.g. /v1/chat goes to one model, /v1/chat/completions goes to another, and so on).

Interstitial_API is quite lightweight and should not add measurable load to your workstation, while its asynchronous backbone should nimbly keep up with whatever you send it. Under continual use (admittedly by a single client querying one endpoint at a time), I never saw it exceed 1.5% of a single CPU thread, or ~300MB memory, on an M1 Max during testing or more than 65MB of total RAM use while relaying continuous API calls to an LM Studio server. If you're in a position to really stress test it, please do and report back.


# I. INSTALLATION

## A. Install the prerequisites

You should have Python 3.7 or higher installed on your system. Linux users should have it already or else know how to get it, Mac and Windows users can download Python from [the official website](https://www.python.org/downloads/). Mac users can also get it using Homebrew if they prefer:

```bash
brew install python
```


## B. Create a folder and a virtual Python3 environment.

Create a folder just for the relay server and associated scripts. A subfolder within your home folder is advised. 

Navigate your way to your new folder (e.g. using `cd` in the Terminal). 

```bash
python3 -m venv llamapen (choose your own name)
```

Now activate it.
```bash
(MacOS/Linux) source llamapen/bin/activate
(Windows) llamapen\Scripts\activate
```

	*Note: Creating a virtual environment isn’t strictly speaking necessary, but is recommended to save potential future headaches when two or more Python apps have mutually exclusive dependencies. Alternatively you could use Docker, but that’s beyond the scope of this readme.*


## C. Install the dependencies.

```bash
pip install -r requirements.txt
```

*** (or) ***

```bash
pip install fastapi uvicorn httpx
```

	*Note: here and throughout, Mac users may have to use pip3 instead of pip, depending on how they installed Python. Also note, if you didn’t create a virtual environment, you might have to use `pipx` if you are getting OS warnings about systemwide pip.*

## D. Download and prepare the folder and scripts.

Download the scripts, e.g. using `git clone`, to the folder you selected.

The folder should contain: 
	interstitial_API.py, 
	start.sh, 
	requirements.txt
	stop.sh, 
	.env

From within this folder, run `chmod +x` on interstitial_API.py, start.sh, and stop.sh:

```bash
    chmod +x interstitial_API.py && chmod +x start.sh && chmod +x stop.sh
```


# II. VALIDATION

## A. Launch the relay.

```bash
./start.sh
```

Without specifying command line arguments or defining environment variables in the .env file (more on that below), running start.sh will start an asynchronous API server at http://localhost:3456 that relays any endpoint queries except GET / (root) to the corresponding endpoints at http://localhost:6789 (i.e. the default configuration on LM Studio).

*Note: The server will stop when the terminal window in which it is running is closed (or when you terminate it manually, e.g. by pressing [ctrl]+[c])*


## B. Test the / endpoint.

```
curl http://localhost:3456/
```

If the server is loaded you should see: {"message":"This relay is powered by interstitial_API"}


## C. Test the /chat/completions endpoint.

```
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is 1 divided by 0?"}],
    "temperature": 0.7,
    "max_tokens": -1
  }'
```


## D. Test the /models endpoint.

```
curl http://localhost:3456/v1/models
```

# III. SHUTTING IT DOWN

To immediately shut down the server (and all instances when running more than one at a time), run:

```bash
./stop.sh
```

Stop.sh is just the following terminal command packaged up:

```bash
kill -9 $(ps aux | grep '[i]nterstitial_API:app' | awk '{print $2}')
```

To parse that:
 - ps aux gets a list of all current processes.
 - | grep '[i]interstitial_API:app filters that list down to the name of our process. The [i] is necessary to exclude the grep filter function itself as a result.
 - awk '{print $2}') returns just the process identifier (PID) for the responsive processes.
 - given a PID, the 'kill' command terminates it. The -9 argument essentially force quits the process.

The script should always work unless interstitial_API.py is renamed, in which case the script can be easily edited, or 


# III. CONFIGURATION

The default configuration is designed to work for a typical installation but there are also many reasons it might not, and functionality not present by default, so read on.

Before diving in, note there are two main ways to configure the server:

* With command line arguments, as in `./start.sh --message-prefix "### Instructions:\n"`)
* Or by modifying variables in the .env file,[*] as in `MESSAGE_PREFIX="### Instructions:\n"`

It’s mostly a matter of personal preference and you can mix approaches: define more static variables (destination API, local port) in the .env file so you don’t have to always enter it on launch, while passing model-dependent variables like the prefix and suffix via command line argument. The only thing important to note is that command line arguments *always* take precedence over definitions in .env.

	*Note for Mac users, if you don’t see the .env file, that’s because the leading ‘.’ hides it from you until you show hidden files, i.e. by pressing [cmd] + [shift] + [.]*

	*[+] For completeness, there are technically other ways, such as defining the environment variables from the .env file directly in the terminalc ommand, the `export` (Mac/Linux only), or the `set` command (Windows only).*
		

## A. Server Configuration

### 1. `nohup` keeps the llamas frolicking.

Without the command line argument `--nohup`, the server will stop when you close the terminal window in which the script is running. Thus, --nohup allows running the server headlessly.

Conversely, with --nohup should be disabled when troubleshooting or debugging.

*Note: for compatibility and user experience, the script is not designed to allow enabling nohup by a durable variable i.e. in .env. It must be toggled via command line argument on each run.*

### 2. custom local ports, destination APIs, and WAN access.

By default the relay server:
* runs on internal port 3456, 
* relays to and from http://localhost:6789, and 
* does not accept queries from outside of http://localhost

#### To specify the local port to use…
`./start.sh  --port 3030`

#### To specify a different destination API…
 `./start.sh  --api-url "https://api.openai.com"

#### To accept queries from outside http://localhost…
… don’t even think about doing it with a command line argument through uvicorn. Instead, try Cloudflare, where a free account gets you SSL-encrypted tunnels for API queries from anywhere (e.g. via https://api.yourdomain.com), best-in-class DDoS protection, and robust access control. Or great alternative options from Tailscale, Zerotier, Netmaker, and Yggdrasil. None require you to open a port on your system to WAN. Reverse proxies are another alternative means for this.

For those who truly need the function and understand the risks, it is possible to open the relay server to external/WAN traffic by running the server through uvicorn with the --host 0.0.0.0 argument, bypassing our bundled shell script:

`uvicorn interstitial_API:app --port 3456 --host 0.0.0.0`

The `--host 0.0.0.0` argument works by opening the same port uvicorn talks with other internal processes through to external traffic including WAN.

*Note: you lose command line access to the server variables when launching via uvicorn, because start.sh handles the server variable argument translation. When launching via uvicorn in this manner, any server configuraton must be made to the .env file.*


#### 3.  (Optional) Keep the server running through MacOS reboots

To avoid having to restart the server on each SO   
Nohup obviates the need to keep a terminal open while the relay is running, but it still has to be manually launched each time.

For a lower friction server environment on Mac, you can have MacOS load the start.sh script silently on log in:

	a. Open "System Preferences" and find "Login Items" within "General" (or within "Users & Groups, then your user account, on older MacOS versions).

	b. Click on the '+' button to add a new login launch item.

	c. Navigate to your script folder and select `start.sh` to add it.

Now your script should run each time you log into your macOS user account.

To remove this configuration, remove start.sh from the list of login launch items.



## B. API Configuration.

### PROMPT_INJECTOR / --prompter
- Type: string
- Default value: null (off)
- Recognized values: “”, “system”, “user”
- Command line syntax: 
```bash 
	./start.sh --prompter "user"
```


#### Purpose
Many models struggle distinguishing user inputs from its own outputs, and consequently devolve into autocompleting the user, or pretending to be the user and carrying on extended conversations without actual user input.

This can be solved to varying degrees, depending on how well a model handles its escape sequences, by injecting prompts as prefixes and suffixes to the most recent user message.

Unfortunately there’s no universal standard for what form or placement the prefixes and suffixes should take, so this API is designed to be interoperable with different conventions.

#### [null]

Witthout a --prompter argument, or if it is set to “” or null, the relay API will not insert message prefixes or suffixes at all.

#### --prompter “system”
If --prompter is set to “system”, the relay API will add the MESSAGE_PREFIX and MESSAGE_SUFFIX as two separate message entries within the messages JSON, before and after the most recent user message respectively.

```Example of a modified JSON when prompter is system: 
{
      "content": “<last assistant message>",
      "role": "assistant"
    },
    {
      "content": "\n\n### Instructions:\n",
      "role": "system"
    },
    {
      "content": “<last user message>”,
      "role": "user"
    },
    {
      "content": "\n\n### Response:\n",
      "role": "system"
    }
}
```


#### --prompter “user”

If --prompter is set to “user”, the relay API will insert the MESSAGE_PREFIX and MESSAGE_SUFFIX at the beginning and end, respectively, of the most recent user message.

```Example of a modified JSON when prompter is user: 
    {
      "content": “<last assistant message>",
      "role": "assistant"
    },
    {
      "content": “\n\n### Instructions:\n<last user message>\n\n### Response:\n”,
      "role": "user"
    },
}
```


### MESSAGE_PREFIX / --message-prefix
- Type: string
- Default value: "\n\n### Instruction:\n"
- Recognized values: any (be sure to use \n to add new lines as needed)
- Command line syntax: 
```bash 
	./start.sh --message-prefix "\n\n### Instruction:\n"
```

This defines the prefix to be inserted into the messages on their way into the model, provided the prompter is enabled.




### MESSAGE_SUFFIX / --message-suffix
- Type: string
- Default value: "\n\n### Response:\n"
- Recognized values: any (be sure to use \n to add new lines as needed)
- Command line syntax: 
```bash 
	./start.sh --message-suffix "\n\n### Response:\n"
```

As noted you can simply edit your local `interstitial_API.py` to change the server or port of the destination API, at line 23.

To edit system messages injected before after assistant and user messages, edit the text on lines 54 and 55, respectively. 



### ENDPOINT_COMPLETIONS

- This allows relaying /chat/completions requests to destination API endpoints that do not follow OpenAI naming conventions. 
- This is an unusual use case and there is not presently a command line argument for editing it.

### ENDPOINT_MODELS

- This allows relaying /models/ requests to destination endpoints that do not follow OpenAI naming conventions. 
- This is an unusual use case and there is not presently a command line argument for editing it.

### MISCELLANEOUS FUNCTIONS

#### Model name reducer

The API automatically reduces model names received from the /v1/models/ and /v1/chat/completions/ endpoints names to their UNIX basenames and removes their extensions, for better compatibility and aesthetics with ChatGPT UIs that aren’t designed to handle long model names.

Example model name before the reduction: “/Users/REDACTED/AIPlayground/Models/TheBloke/Wizard-Vicuna-30B-Uncensored-GGML/Wizard-Vicuna-30B-Uncensored.ggmlv3.q5_K_M.bin"

Example model name after the reduction: “Wizard-Vicuna-30B-Uncensored.ggmlv3.q5_K_M”

#### Model name override

To patch compatibility between client and server apps that insist on different models, defining the MODEL_OVERRIDE variable will always tell the server that the client is requesting that model.

#### Missing favicon patcher

If the destination API doesn’t serve up a favicon, have no fear 🤠
