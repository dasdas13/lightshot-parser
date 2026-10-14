#!/usr/bin/env python3
"""Парсер случайных скриншотов Lightshot (prnt.sc) с простым GUI. Только stdlib. Windows и Linux.
Запуск: python3 lightshot.pyw   |   проверка парсера: python3 lightshot.pyw --check"""
import json, os, queue, random, re, socket, string, subprocess, sys, threading, urllib.request

# Рядом со скриптом, а у собранного exe — рядом с exe (onefile распаковывается во временную папку, там всё бы пропало).
BASE = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(BASE, "shots", "Lightshot")  # можно сменить в окне кнопкой «Обзор…»
HISTORY = os.path.join(BASE, "downloaded.txt")  # коды скачанных скриншотов, по одному в строке; живёт отдельно от папки со скриншотами
ALPHABET = string.ascii_lowercase + string.digits
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
OG = re.compile(r'<meta property="og:image" content="([^"]+)"')
UI, MONO = ("Segoe UI", "Consolas") if sys.platform == "win32" else ("DejaVu Sans", "DejaVu Sans Mono")

# Если системный DNS не резолвит prnt.sc -> запасной вариант через DNS-over-HTTPS.
# ponytail: только A-записи и без TTL-кэша; если IP сменится, перезапустить программу.
_gai, _doh = socket.getaddrinfo, {}
def _getaddrinfo(host, *a, **k):
    try:
        return _gai(host, *a, **k)
    except socket.gaierror:
        if host == "dns.google":
            raise
        if host not in _doh:
            with urllib.request.urlopen(f"https://dns.google/resolve?name={host}&type=A", timeout=15) as r:
                _doh[host] = next(x["data"] for x in json.load(r)["Answer"] if x["type"] == 1)
        return _gai(_doh[host], *a, **k)
socket.getaddrinfo = _getaddrinfo


def parse(html):
    """URL картинки живого скриншота или None (у удалённых og:image — заглушка //st.prntscr.com/...)."""
    m = OG.search(html)
    return m.group(1) if m and m.group(1).startswith("http") else None


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
        return r.read(), r.geturl()


def load_seen(out):
    """Коды уже скачанных скриншотов: downloaded.txt + имена файлов в папке (скачанные до появления истории).
    Историю не чистим при удалении файлов — иначе удалённый скриншот скачался бы заново."""
    seen = set()
    if os.path.exists(HISTORY):
        with open(HISTORY, encoding="utf-8") as f:
            seen = {line.strip() for line in f if line.strip()}
    return seen | {os.path.splitext(n)[0] for n in os.listdir(out)}


def open_folder(path):
    os.startfile(path) if sys.platform == "win32" else subprocess.Popen(["xdg-open", path])


def worker(out, count, delay, q, stop):
    """Одна итерация = случайный код -> страница -> картинка. Пауза delay после КАЖДОГО запроса.
    Сама останавливается, когда сохранено count скриншотов (0 — без ограничений). Папка out уже создана."""
    saved = 0
    seen = load_seen(out)
    q.put(("info", f"ℹ  В истории {len(seen)} скриншотов — повторно они скачиваться не будут"))
    while not stop.is_set() and (not count or saved < count):
        code = "".join(random.choices(ALPHABET, k=6))
        if code in seen:  # уже скачан (в этой или прошлой сессии) — без запроса и без паузы
            continue
        try:
            url = parse(get(f"https://prnt.sc/{code}")[0].decode("utf-8", "ignore"))
            stop.wait(delay)
            data, final = get(url) if url else (None, "")
            if not data or "removed" in final:  # imgur отдаёт removed.png для удалённых
                q.put(("skip", f"·  {code}  — нет скриншота"))
            else:
                name = code + (os.path.splitext(url.split("?")[0])[1] or ".png")
                with open(os.path.join(out, name), "wb") as f:
                    f.write(data)
                seen.add(code)  # в историю только УСПЕШНО скачанные: «нет скриншота» не пишем, он мог появиться позже
                with open(HISTORY, "a", encoding="utf-8") as h:
                    h.write(code + "\n")
                saved += 1
                q.put(("ok", f"✔  {name}  ({len(data) // 1024} КБ)"))
        except Exception as e:
            gone = getattr(e, "code", None) == 404  # Lightshot отвечает 404 на несуществующие коды
            q.put(("skip", f"·  {code}  — нет скриншота") if gone else ("err", f"✖  {code}  — {e}"))
        stop.wait(delay)
    if not stop.is_set():
        q.put(("done", f"■  Готово: сохранено {saved}"))


def main():
    import tkinter as tk
    from tkinter import filedialog, ttk
    try:  # чёткий текст на HiDPI (только Windows)
        import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    BG, CARD, FG, DIM, ACCENT = "#1b1d26", "#272a37", "#e8e9f0", "#8b8fa3", "#6c8cff"
    root = tk.Tk()
    root.title("Lightshot Parser"); root.geometry("600x570"); root.minsize(560, 450); root.configure(bg=BG)
    try:  # иконка окна (Windows и Linux); в exe icon.png лежит во внутренней папке _MEIPASS
        root.iconphoto(True, tk.PhotoImage(file=os.path.join(getattr(sys, "_MEIPASS", BASE), "icon.png")))
    except Exception:
        pass
    s = ttk.Style(root); s.theme_use("clam")
    s.configure("TFrame", background=BG)
    s.configure("TLabel", background=BG, foreground=FG, font=(UI, 10))
    s.configure("TButton", background=CARD, foreground=FG, borderwidth=0, padding=(14, 8), font=(UI, 10, "bold"))
    s.map("TButton", background=[("active", "#363a4b")])
    s.configure("Go.TButton", background=ACCENT, foreground="#ffffff")
    s.map("Go.TButton", background=[("active", "#869fff")])

    ttk.Label(root, text="Lightshot Parser", font=(UI, 20, "bold")).pack(anchor="w", padx=18, pady=(16, 0))
    ttk.Label(root, text="Случайные скриншоты с prnt.sc", foreground=DIM).pack(anchor="w", padx=18)

    top = ttk.Frame(root); top.pack(fill="x", padx=18, pady=14)
    form = ttk.Frame(top); form.pack(side="left")
    btn = ttk.Button(top, text="▶  Старт", style="Go.TButton"); btn.pack(side="right")
    ttk.Button(top, text="Папка", command=lambda: open_out()).pack(side="right", padx=8)

    def field(row, label, value, to, step):
        var = tk.IntVar(value=value)
        ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
        tk.Spinbox(form, from_=0, to=to, increment=step, width=7, textvariable=var, font=(UI, 10), bg=CARD, fg=FG,
                   insertbackground=FG, buttonbackground=CARD, relief="flat", highlightthickness=0).grid(row=row, column=1, padx=10)
        return var
    count = field(0, "Скриншотов за раз (0 — без лимита)", 100, 1000000, 10)
    delay = field(1, "Задержка, мс", 250, 5000, 50)

    row = ttk.Frame(root); row.pack(fill="x", padx=18, pady=(0, 12))
    ttk.Label(row, text="Сохранять в").pack(side="left")
    outdir = tk.StringVar(value=DEFAULT_OUT)
    ttk.Button(row, text="Обзор…", command=lambda: browse()).pack(side="right")
    tk.Entry(row, textvariable=outdir, font=(UI, 10), bg=CARD, fg=FG, insertbackground=FG, relief="flat",
             highlightthickness=0).pack(side="left", fill="x", expand=True, padx=10, ipady=6)

    stats = ttk.Label(root, font=(UI, 11, "bold")); stats.pack(anchor="w", padx=18, pady=(0, 8))
    log = tk.Text(root, bg=CARD, fg=FG, bd=0, highlightthickness=0, state="disabled", font=(MONO, 10), padx=12, pady=10)
    log.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    for tag, color in (("ok", "#4cd38b"), ("skip", DIM), ("err", "#ff6b6b"), ("done", ACCENT), ("info", DIM)):
        log.tag_config(tag, foreground=color)

    st = {"ok": 0, "skip": 0, "err": 0, "total": 0, "stop": None}
    q = queue.Queue()

    def num(var, default):  # пустое/кривое поле -> значение по умолчанию
        try:
            return max(0, var.get())
        except tk.TclError:
            return default

    def prepare():  # путь из поля -> созданная папка (или None, а ошибка уходит в лог)
        out = os.path.abspath(os.path.expanduser(outdir.get().strip() or DEFAULT_OUT))
        try:
            os.makedirs(out, exist_ok=True)
            return out
        except OSError as e:
            q.put(("err", f"✖  папка «{out}»: {e}"))

    def open_out():
        out = prepare()
        if out:
            open_folder(out)

    def browse():
        cur = outdir.get().strip()
        d = filedialog.askdirectory(initialdir=cur if os.path.isdir(cur) else os.path.expanduser("~"),
                                    title="Куда сохранять скриншоты")
        if d:  # при отмене приходит '' (или пустой кортеж)
            outdir.set(os.path.normpath(d))

    def toggle():
        if st["stop"] and not st["stop"].is_set():
            st["stop"].set(); btn.config(text="▶  Старт")
            return
        out = prepare()
        if not out:
            return
        # новый Event на каждый запуск: старый поток доживает свой запрос и выходит
        st.update(ok=0, skip=0, err=0, total=num(count, 100), stop=threading.Event())
        threading.Thread(target=worker, args=(out, st["total"], num(delay, 250) / 1000, q, st["stop"]), daemon=True).start()
        btn.config(text="■  Стоп")

    def poll():
        try:
            while True:
                kind, msg = q.get_nowait()
                if kind == "done":
                    st["stop"].set(); btn.config(text="▶  Старт")
                elif kind != "info":
                    st[kind] += 1
                log.config(state="normal"); log.insert("end", msg + "\n", kind)
                if int(log.index("end-1c").split(".")[0]) > 300:
                    log.delete("1.0", "2.0")
                log.config(state="disabled"); log.see("end")
        except queue.Empty:
            pass
        of = f" / {st['total']}" if st["total"] else ""
        stats.config(text=f"Сохранено: {st['ok']}{of}     Пусто: {st['skip']}     Ошибок: {st['err']}")
        root.after(100, poll)

    btn.config(command=toggle)
    poll()
    root.mainloop()


if __name__ == "__main__":
    if "--check" in sys.argv:
        assert parse('<meta property="og:image" content="https://image.prntscr.com/image/x.png">') == "https://image.prntscr.com/image/x.png"
        assert parse('<meta property="og:image" content="//st.prntscr.com/2025/img/0_173a7b_211be8ff.png">') is None
        assert parse("<html></html>") is None
        import tempfile
        with tempfile.TemporaryDirectory() as t:  # история = downloaded.txt + файлы в папке; пустые строки игнорируются
            HISTORY, out = os.path.join(t, "h.txt"), os.path.join(t, "out")
            os.mkdir(out)
            assert load_seen(out) == set()
            open(os.path.join(out, "abc123.png"), "w").close()
            open(HISTORY, "w").write("zzz999\n\n")
            assert load_seen(out) == {"abc123", "zzz999"}
        print("ok")
    else:
        main()
