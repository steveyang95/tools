import requests


def send_to_engineering(info=None):
    """
    Send a slack message to engineering bearing the debugging info for the test that was just run. This wraps the real
    work we do into a nice dictionary to send to slack, and does error handling for the code.
    """
    message_contents = "*Users Statistics* :tada:"
    if info:
        for item, value in info:
            message_contents += "\n{}: {}".format(item, value)
    params = {
        "fallback": "Fallback?",
        "color": "#3AA3E3",
        "pretext": "Pretext",
        "title": "Title",
        "text": message_contents,
        "attachments": [
            {
                "title": "New Users",
                "text": "Something",
                "color": "#3AA3E3"
            }
        ]
    }

    session = requests.Session()
    url = "https://hooks.slack.com/services/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"

    _out("curl -X POST {} -H 'application/json' -d {}".format(url, params), title="CURL")
    r = session.post(url, json=params)

    print(r)
    print(r.status_code)


def _out(msg, title=None):
    title = title if title else "MESSAGE"
    print("\n[{}] {}".format(title, msg))


send_to_engineering()
