# LeoDownloadBot

## Overview

**LeoDownloadBot** is a Python script that automates downloading images from the **Leonardo.Ai API**. It allows users to retrieve images generated on their Leonardo.Ai account, including those created via the Leonardo.Ai web app, using their API subscription.

## Features
- Automated image downloading from the **Leonardo.Ai API**.
- Error handling for failed downloads.
- Logging system for tracking download activity.
- Minimal dependencies for lightweight execution.
- Executable as a standalone script (`chmod +x`).

## Requirements

### **Leonardo.Ai API Subscription**
To use this bot, you need a **Leonardo.Ai API subscription** (separate from a regular user subscription). API plans start at **$9/month**. Check out the [Getting Started Guide](https://docs.leonardo.ai/docs/getting-started) for more details.

You'll also need to **provision an API key**. Follow the steps outlined in [this guide](https://docs.leonardo.ai/docs/create-your-api-key).

### **Python Dependencies**
Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pookah-bot/leodownloadbot.git
   cd leodownloadbot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make the script executable:
   ```bash
   chmod +x download_bot.py
   ```
4. Run the script:
   ```bash
   ./download_bot.py
   ```

## Configuration

Modify the script settings to customize:
- **API Key** (required to authenticate with Leonardo.Ai API).
- **File storage location**.
- **Retry attempts**.
- **Logging preferences**.

## Optional Parameters
The script supports the following optional command-line arguments:

| Argument       | Description |
|---------------|-------------|
| `--api_key`   | Manually specify the Leonardo.Ai API key (if not using an environment variable). |
| `--download_dir` | Define the directory where downloaded files will be stored. |
| `--rebuild`   | Force a rebuild of the download directory. |
| `--verbose`   | Enable verbose logging for debugging. |

## Environment Variables
Instead of passing arguments every time, users can set environment variables for convenience:

| Environment Variable       | Description |
|----------------------------|-------------|
| `LEONARDO_API_KEY`        | Your Leonardo.Ai API key for authentication. |
| `LEONARDO_DOWNLOAD_DIR`   | The directory where downloaded images will be stored. |

To set an environment variable in your shell session:

```bash
export LEONARDO_API_KEY="your-api-key"
export LEONARDO_DOWNLOAD_DIR="/path/to/downloads"
```

Or permanently add them to your `.bashrc`, `.zshrc`, or `.profile`.

## Usage

Run the bot using:
```bash
./download_bot.py
```

Or specify optional parameters:
```bash
./download_bot.py --api_key your-api-key --download_dir /path/to/save --verbose
```

Ensure necessary permissions are granted if downloading from restricted sources.

## Repository
GitHub: [LeoDownloadBot](https://github.com/pookah-bot/leodownloadbot)

## License

This software is proprietary and confidential. Unauthorized copying, sharing, or distribution is strictly prohibited.

## Disclaimer

This software is provided "AS IS," without any warranties, express or implied. The author is not liable for any claims, damages, or liabilities arising from the use of this software.

