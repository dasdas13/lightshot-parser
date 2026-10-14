# Lightshot Parser

Скачивает случайные скриншоты с Lightshot (prnt.sc). Простое окно на tkinter, без внешних зависимостей. Работает на Windows и Linux (Linux Mint).

- **Скриншотов за раз** — программа сама остановится, когда сохранит столько картинок (`0` — пока не нажмёте «Стоп»).
- **Задержка** — пауза после каждого запроса, по умолчанию 250 мс.
- **Сохранять в** — папка для скриншотов, выбирается кнопкой «Обзор…». По умолчанию `shots/Lightshot/` рядом с программой.
- **Без повторов** — коды скачанных скриншотов записываются в `downloaded.txt` рядом с программой, и скачанный скриншот не качается повторно: ни в другой сессии, ни в другую папку, ни после того, как вы удалили файл. Если скриншота не нашлось, это в историю **не** пишется (он мог появиться позже). Чтобы скачать скриншот заново, удалите его код из `downloaded.txt`.

## Linux Mint

```bash
sudo apt install python3 python3-tk git
git clone https://github.com/dasdas13/lightshot-parser.git
cd lightshot-parser
python3 lightshot.pyw
```

Чтобы программа появилась в меню приложений с иконкой:

```bash
./install-linux.sh
```

## Windows

Нужен Python 3.8+ (tkinter идёт в комплекте).

```bat
git clone https://github.com/dasdas13/lightshot-parser.git
cd lightshot-parser
pythonw lightshot.pyw
```

Или просто скачайте `lightshot.pyw` и `icon.png` в одну папку и запустите `lightshot.pyw` двойным кликом.

### Собрать exe с иконкой

```bat
pip install pyinstaller
pyinstaller --onefile --windowed --name LightshotParser --icon icon.ico --add-data "icon.png;." lightshot.pyw
```

Готовый `dist\LightshotParser.exe` сохраняет скриншоты в `shots\Lightshot\` рядом с самим exe.

## Проверка парсера

```bash
python3 lightshot.pyw --check
```

## Важно

Скриншоты случайные и чужие, в них могут быть пароли и личные данные. Не публикуйте и не используйте их.
Если системный DNS не находит `prnt.sc`, программа сама спросит адрес у `dns.google` (DNS-over-HTTPS).
