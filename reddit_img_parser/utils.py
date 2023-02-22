from datetime import datetime


def log(text, noprint=False, **kwargs):
    # Usage:
    # a = "world"
    # log("hello {a}", a=a)
    now = datetime.now()
    timestamp = now.strftime("[%Y-%m-%d %H:%M:%S]")
    message = text.format(**kwargs)
    log_message = f"{timestamp} {message}\n"
    with open('parser.log', 'a') as f:
        f.write(log_message)
    if not noprint:
        print(message)
