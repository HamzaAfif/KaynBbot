# KaynBot README

## Overview
KaynBot is an AI-powered e-commerce assistant designed to empower small businesses, particularly in regions with limited technological infrastructure, by enabling them to manage and sell products through a conversational Telegram interface. Leveraging natural language processing (NLP) via OpenAI's GPT models and a robust SQLite database, KaynBot simplifies product and store management for non-tech-savvy users while offering buyers a location-aware product discovery experience. The platform prioritizes accessibility, scalability, and community-driven commerce.

## Features
- **Conversational Interface**: Manage products and stores via Telegram using natural language.
- **AI-Driven Processing**: Validates and processes product/store data with OpenAI's GPT-4o-mini model.
- **Location-Based Services**: Prioritizes local sellers for buyers and supports GPS coordinates for stores.
- **Image Processing**: Automatically removes backgrounds and categorizes product images.
- **Session Management**: Tracks user progress and conversation history for seamless interactions.
- **Modular Architecture**: Organized subprocesses for product addition, store creation, and data validation.

## Project Structure
- `.env`: Stores API keys (OpenAI, Telegram).
- `.venv/`: Python virtual environment for dependencies.
- `classes/`: Defines `User`, `Product`, `Store`, and `Session` classes.
- `data/`: Stores user data, images, videos, audios, and JSON metadata.
- `easyfind.db`: SQLite database for user, product, and store data.
- `subProc/`: Modular scripts for tasks like `addProduct.py`, `addStore.py`, and `jsonProc.py`.
- `telegramBot/`: Telegram bot implementation, including `textMessage.py` for message handling.
- `easyfind-web/`: Web interface with server-side logic and frontend views.
- `langChain.py`: Integrates LangChain for NLP and SQL query generation.
- `logs/`: Contains `ai_debug.log` and `logs.py` for debugging and logging.
- `requirements.txt`: Lists Python dependencies.

## Prerequisites
- Python 3.8+
- Telegram account and bot token (via [BotFather](https://core.telegram.org/bots))
- OpenAI API key
- SQLite

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/kaynbot.git
   cd kaynbot
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

5. **Initialize Database**:
   Ensure `easyfind.db` is set up using `db.py` or initialize it manually with the required schema (Users, Products, Stores, Sessions).

## Usage
1. **Run the Telegram Bot**:
   ```bash
   python telegramBot/textMessage.py
   ```

2. **Interact via Telegram**:
   - Start a chat with your bot (created via BotFather).
   - Create a store: e.g., "I want to add a store named Casablanca Boutique in Casablanca."
   - Add products: e.g., "Add a T-shirt, price 20, quantity 100."
   - Discover products: e.g., "Find dresses in Rabat."

## Key Implementation Details
- **Message Handling**: `textMessage.py` uses `python-telegram-bot` to handle text, images, voice, and location inputs, with AI-driven responses via OpenAI's GPT-4o-mini.
- **Session Management**: The `Session` class tracks user progress and conversation history, stored in JSON files under `data/users/`.
- **AI Integration**: LangChain and OpenAI APIs validate inputs (e.g., `makeSureitsProduct`, `makeSureitsStore`) and generate SQL queries for database operations.
- **Error Handling**: Robust JSON parsing and state management ensure reliable interactions.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For questions or support, contact the KaynBot Development Team at [your-email@example.com].

---
*Last Updated: May 24, 2025*
