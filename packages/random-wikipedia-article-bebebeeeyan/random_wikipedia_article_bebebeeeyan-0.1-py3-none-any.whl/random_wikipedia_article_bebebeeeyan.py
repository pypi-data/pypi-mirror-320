import json
import textwrap
import urllib.request

API_URL = "https://en.wikipedia.org/api/rest_v1/page/random/summary"


def main():
    raise Exception("Boom!")
    with urllib.request.urlopen(API_URL) as responce:
        data = json.load(responce)

    print(data["title"], end="\n\n")
    print(textwrap.fill(data["extract"]))


if __name__ == "__main__":
    main()
