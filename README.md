# Lightshot Parser

Скачивает случайные скриншоты с Lightshot (prnt.sc). Простое окно на tkinter, без внешних зависимостей. Работает на Windows и Linux (Linux Mint).

- **Скриншотов за раз** — программа сама остановится, когда сохранит столько картинок (`0` — пока не нажмёте «Стоп»).
- **Задержка** — пауза после каждого запроса, по умолчанию 250 мс.
- Всё сохраняется в папку `shots/Lightshot/` рядом с программой.

## Linux Mint

```bash
sudo apt install python3 python3-tk git
git clone https://github.com/dasdas13/lightshot-parser.git
cd lightshot-parser
python3 lightshot.pyw
```

## Windows

Нужен Python 3.8+ (tkinter идёт в комплекте).

```bat
git clone https://github.com/dasdas13/lightshot-parser.git
cd lightshot-parser
pythonw lightshot.pyw
```

Или просто скачайте `lightshot.pyw` и запустите двойным кликом.

## Проверка парсера

```bash
python3 lightshot.pyw --check
```

## Важно

Скриншоты случайные и чужие, в них могут быть пароли и личные данные. Не публикуйте и не используйте их.
Если системный DNS не находит `prnt.sc`, программа сама спросит адрес у `dns.google` (DNS-over-HTTPS).
