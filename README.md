# ReelAccX

ReelAccX is a versatile Discord bot designed to send Instagram Reels across various servers. It allows you to manage Instagram accounts, add or remove channels, and back up important files, among other functionalities. With ReelAccX, you can share engaging Reels on a wide range of topics.

## Table of Contents
1. [Features](#features)
2. [Perks of installing ReelAccX] (#Popular Reels Topics)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Commands](#commands)
7. [Contributing](#contributing)
8. [License](#license)
9. [Contact](#contact)

## Features
- **Temperature Monitoring:** Check the bot's CPU temperature.
- **Uptime Tracking:** Retrieve the bot's uptime.
- **Backup Management:** Create backups of essential files and send them to a designated user.
- **Storage Information:** Get information about the bot's storage usage.
- **Account Management:** Add or remove Instagram accounts and manage their associated servers and channels.
- **File Uploads:** Upload videos to specified channels and servers.

## Popular Reels Topics

ReelAccX supports sharing Instagram Reels on various popular topics, including but not limited to:

1. **Memes:** Humorous and viral content.
2. **Informational Videos:** Educational and how-to content.
3. **Fitness Tips:** Workout routines and fitness advice.
4. **Food Recipes:** Cooking demonstrations and recipe ideas.
5. **Travel Adventures:** Destination highlights and travel tips.
6. **Fashion Trends:** Outfit ideas and fashion advice.
7. **DIY Projects:** Creative and craft-based tutorials.

## Installation

To set up ReelAccX, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ReelAccX.git
   cd ReelAccX
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory with the following content:

   ```
   KEY=your_discord_bot_token
   MEMBER_ID=your_verified_member_id
   LOGCHANNEL=your_log_channel_id
   APP_ID=your_application_id
   UID=your_user_id
   ```

5. **Run the bot:**

   ```bash
   python bot.py
   ```

## Configuration

Ensure your `.env` file contains the correct values for `KEY`, `MEMBER_ID`, `LOGCHANNEL`, `APP_ID`, and `UID`. These values are crucial for the bot to function correctly.

## Usage

Once the bot is running, you can interact with it using the following commands. 

### Commands

- **`/temprature`**: Returns the current CPU temperature of the bot.
- **`/uptime`**: Shows the bot's uptime.
- **`/backup`**: Creates a backup of important files (requires verified member ID).
- **`/storage`**: Provides storage information of the bot.
- **`/adduser <username> <member_id>`**: Adds an Instagram account to the bot (requires verified member ID).
- **`/rmuser <username> <member_id>`**: Removes an Instagram account from the bot (requires verified member ID).
- **`/addchannel <username> <server_name> <channel_id> <member_id>`**: Adds a channel for an Instagram account (requires verified member ID).
- **`/rmchannel <username> <server_name> <channel_id> <member_id>`**: Removes a channel from the bot (requires verified member ID).
- **`/lsaccounts <member_id>`**: Lists all Instagram accounts and their associated servers (requires verified member ID).
- **`/hlp <member_id>`**: Provides a description of available commands (requires verified member ID).

## Contributing

Contributions to ReelAccX are welcome! If you have suggestions, bug reports, or enhancements, please submit a pull request or open an issue. For substantial changes, please discuss your ideas in an issue before implementing them.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

ReelAccX is licensed under the [GNU General Public License v3.0 (GPL-3.0)](https://opensource.org/licenses/GPL-3.0). See the [LICENSE](LICENSE) file for more details.

## Contact

For further assistance, you can reach out via:

- **Email:** shaur.codes@gmail.com
- **GitHub Issues:** [ReelAccX Issues](https://github.com/shaur-codes/reelaccx/issues)
