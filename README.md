# ReelAccX

ReelAccX is a Discord bot designed to send Short videos or memes across various servers to prevent your server from going inactive by increasing user engagement, when my friend was in need of such a bot and he could not find one I had to develop this bot well, it has the potential to be a renowned discord bot if developed further. It allows you to manage accounts from where you want to get videos, add or remove channels, and back up its database, among other functionalities. With ReelAccX, you can receive engaging short videos on a wide range of topics.

## Table of Contents
1. [Features](#features)
2. [Perks of installing ReelAccX](#Perks)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Commands](#commands)
7. [Our own RPI Server](#server)
8. [Contributing](#contributing)
9. [License](#license)
10. [Contact](#contact)

## Features
- **Temperature Monitoring:** Check the bot's CPU temperature.
- **Uptime Tracking:** Retrieve the bot's uptime.
- **Backup Management:** Create backups of essential files and send them to a designated user.
- **Storage Information:** Get information about the bot's storage usage.
- **Account Management:** Add or remove Instagram accounts and manage their associated servers and channels.
- **File Uploads:** Upload videos to specified channels and servers.

## Perks

ReelAccX supports sharing short videos on various popular topics, including but not limited to:

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
## server
We are using A Raspberry-Pi 5 server for deployment.
![rpi](https://github.com/user-attachments/assets/3b59ae7a-25d9-4e9b-bbda-3435b62e2f4b)

# here is how our server exaclty looks like
![headquarter](https://github.com/user-attachments/assets/8912f2a6-c64a-4238-9171-6c44a670b2db)

it has an active cooler installed inside the case itself but i use it as a backup.
As an active cooler i use this Fan that's visible in the image.
yeah the server is floating and it receives videos out of thin air!!


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
