# AI Guard (Beta)
AI Guard is designed to protect AI Systems from misuse, manipulation, and harmful inputs. It ensures that the AI behaves as intended and does not deviate from its guidelines or generate harmful content.

# Features
- Input Sanitization
- Prompt Classification
- Manipulation Detection
- Ethical Compliance Check
- Response Validation
- Logging and Monitoring
- Customizable Settings
- Interactive Testing Mode (Uses Ollama)
- Fallback Mechanisms
- Scalability and Extensability

# How It Works
AI Guard protects AI Systems from misuse and harmful inputs by sanitizing user prompts to remove noise, classifying them as "non-toxic" (safe) or "toxic" (malicious) using a machine learning model and detecting manipulation attempts through predefined rules. It ensures ethical compliance by blocking prompts that request harmful or illegal actions and validates AI responses to prevent inappropriate content. The system logs all activities for auditing, operates interactively for testing, and includes a fallback mechanism to handle ambiguous cases by defaulting to "non-toxic". You can customize this however you'd like via the settings.yml file it supports features like input sanitization, prompt classification, and response validation making it ideal for chatbots, ai assistants, content moderation and research!

# Settings and Manipulation Rules
If you find any form of manipulation rule that can manipulate the AI assistant in any form of way you can add that said prompt to the manipulation_rules.txt file and you can open an issue stating a bypass you found. There are currently 583 different manipulation rules as of the first beta release and we're always looking to add more to this list that can really keep all AI safe from unrightful prompt engineering.

If you wish to tinker around with it and enable or disable whatever you dont like with in the whole system, you can head to the settings.yml file and enable or disable things. You can even go ahead and change the logs file to a whole different file if you wish.
