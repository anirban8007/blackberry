#!/bin/bash
# BLACKBERRY — Phase 1 Setup Script
# Run: bash setup.sh

echo "🫐 Setting up Blackberry..."

# 1. Create folder
mkdir -p ~/.blackberry
cp *.py ~/.blackberry/

# 2. Install Python packages
echo "📦 Installing Python packages..."
pip install sounddevice pyaudio faster-whisper openwakeword \
            edge-tts numpy scipy google-generativeai \
            chromadb python-dotenv

# 3. Install audio player (for TTS output)
echo "🔊 Installing audio player..."
sudo apt install -y mpv

# 4. Create .env file if it doesn't exist
ENV_FILE=~/.blackberry/.env
if [ ! -f "$ENV_FILE" ]; then
    echo "🔑 Creating .env file..."
    echo "GEMINI_API_KEY=paste_your_key_here" > "$ENV_FILE"
    echo ""
    echo "⚠️  IMPORTANT: Open ~/.blackberry/.env and paste your Gemini API key"
    echo "   Get it free from: https://aistudio.google.com"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add your Gemini API key to ~/.blackberry/.env"
echo "  2. Run: cd ~/.blackberry && python3 blackberry.py"
