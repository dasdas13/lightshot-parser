#!/bin/sh
# Добавляет Lightshot Parser в меню приложений (Linux Mint и др.) с иконкой.
# Запускать из скачанной папки: ./install-linux.sh   Удалить: rm ~/.local/share/applications/lightshot-parser.desktop
d="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/lightshot-parser.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Lightshot Parser
Comment=Парсер случайных скриншотов Lightshot
Exec=python3 "$d/lightshot.pyw"
Icon=$d/icon.png
Terminal=false
Categories=Utility;Network;
EOF
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
echo "Готово: Lightshot Parser теперь в меню приложений (раздел «Стандартные» / «Интернет»)."
