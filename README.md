# 🍜 MakanBot — Singapore Hawker Food Recommendation Chatbot

MakanBot is an AI-powered chat assistant that recommends Singapore hawker
dishes based on what you're craving, your MRT location, and any dietary
preferences. Built for locals, expats, and visitors who want a friendly
guide to hawker food without trawling through review sites.

> 🎓 Built for the DigiPen AI Application Development Bootcamp 2026 Capstone.

---

## Problem Statement

Singapore has hundreds of hawker centres and thousands of stalls, which is
overwhelming when you just want a good meal nearby. Existing review sites
are great for digging deep, but slow for casual "what should I eat?"
decisions. MakanBot turns that question into a quick, conversational
recommendation — accounting for cravings, location, and dietary needs in
the same chat.

---

## Technology Stack

- **Language:** Python 3.10+
- **UI Framework:** Streamlit
- **AI Provider:** OpenAI API (`gpt-4o-mini` model)
- **Key Libraries:**
  - `openai` — official OpenAI Python SDK
  - `python-dotenv` — loads environment variables from `.env`
  - `streamlit` — web UI framework
- **Data Storage:** Local JSON file (`bookmarks.json`) for bookmark persistence
- **Version Control:** Git + GitHub

---

## Setup Instructions

These steps take about 5 minutes if you already have Python and Git
installed.

### Prerequisites
- Python 3.10 or newer ([download](https://www.python.org/downloads/))
- Git ([download](https://git-scm.com/downloads))
- An OpenAI API key with billing enabled
  ([get one here](https://platform.openai.com/api-keys))

### Step 1 — Clone the repository
```bash
git clone https://github.com/irrfaanshaik97-commits/Hawker_Chatbot
cd hawker-chatbot
```

### Step 2 — Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure your API key
```bash
cp .env.example .env       # macOS / Linux
copy .env.example .env     # Windows
```

Open the new `.env` file and replace `your_openai_api_key_here` with
your actual OpenAI API key.

### Step 5 — Run the app
```bash
streamlit run app.py
```

Your browser should open automatically at
[http://localhost:8501](http://localhost:8501).
If it doesn't, open that URL manually.

---

## Usage Examples

### Example 1 — Spicy food near Bugis MRT

**User:** *I want something spicy near Bugis MRT.*

**MakanBot:**
> **Mee Goreng**
> - 📍 Where: Albert Centre Hawker, near Bugis MRT
> - 💡 Why it matches: A bold, spicy stir-fried noodle dish — perfect when you want heat.
>
> **Sambal Stingray**
> - 📍 Where: Albert Centre Hawker, near Bugis MRT
> - 💡 Why it matches: Grilled with spicy sambal — punchy flavor in every bite.

### Example 2 — Vegetarian and dietary-aware

**User:** *I'm vegetarian and looking for soupy noodles around Chinatown.*

**MakanBot:**
> **Vegetarian Laksa**
> - 📍 Where: Chinatown Complex Food Centre, near Chinatown MRT
> - 💡 Why it matches: A creamy, coconut-based soup noodle — fully vegetarian if you confirm with the stall.
>
> Tip: Look for stalls marked "素食" (vegetarian) at the second-floor food centre.

### Bonus — Bookmarking a Recommendation

After the bot replies, a 🔖 button appears below each dish. Clicking it
saves the dish to the **Bookmarks** sidebar, labelled with an
AI-generated tag line like *"Bugis, spicy, non-halal"* so you can find
it again later.

---
```
## Project Structure
hawker-chatbot/
├── app.py                  # Streamlit UI and session state
├── openai_service.py       # OpenAI API calls, chat memory, tagline generation
├── prompts.py              # System prompt (named constant)
├── storage.py              # JSON persistence for bookmarks
├── config.py               # Loads environment variables
├── requirements.txt        # Python dependencies
├── .env.example            # Template for required environment variables
├── .gitignore              # Protects secrets and local data
└── README.md               # This file
```
---

## Known Limitations

- **Knowledge cutoff and accuracy:** Recommendations come from the AI
  model's training data. Specific stall opening hours, unit numbers, or
  prices may be outdated or imprecise. The bot is told to recommend
  hawker centres + dishes rather than specific stalls when unsure.
- **No live availability or pricing:** The bot does not connect to any
  real-time food directory. If a stall has closed permanently, the bot
  may still suggest it.
- **Local-only bookmarks:** Bookmarks are stored in `bookmarks.json` on
  the user's local machine. They are not synced across devices and will
  not persist if deployed to an ephemeral cloud platform.
- **Single-language:** Currently optimized for English input. Mixed
  Singlish works in practice but is not deliberately tested.

---

## Future Improvements

- **Real hawker stall database:** Integrate with a public dataset (e.g.,
  data.gov.sg hawker centre listings) so the bot can cross-check its
  recommendations against current operating stalls.
- **Cloud-synced bookmarks:** Move bookmark storage from local JSON to a
  hosted database (Supabase or Firebase) so users can access their
  saved dishes across devices.
- **Streamlit Cloud deployment:** Host the app publicly via Streamlit
  Cloud so the live demo URL can be shared during the presentation.

---

## Acknowledgements

Built for the DigiPen Institute of Technology Singapore — AI Application
Development Bootcamp 2026 Capstone. Inspired by the suggested project
idea *"Singapore Hawker Food Recommendation Chatbot"* from the capstone
requirements brief.
