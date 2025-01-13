import conversationalspacemapapp.App.TogaApp.app as togaApp


def main(toga=True):
    if toga:
        togaApp.main().main_loop()
    else:
        NotImplemented("No other GUI implementation available.")


if __name__ == "__main__":
    main()
