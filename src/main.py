# TODO train new dataset
from modules.tui import TUI


def main():
    tui = TUI()
    tui.start()
    while tui.running:
        tui.take_user_input()
        tui.match_user_input()
        

if __name__ == "__main__":
    main()


# sp yt