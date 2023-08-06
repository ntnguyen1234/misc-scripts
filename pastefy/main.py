from pastefy_app import Pastefy


def main():
    text_id = 'G1Txv5su'

    app = Pastefy()
    # app.edit(text_id)
    # app.youtube_polymer(text_id)
    app.add_polymer(text_id)


if __name__ == "__main__":
    main()