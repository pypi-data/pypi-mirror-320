import os
try:
    import emoji
    import os

    def Main():
        os.system("cls")
        print("Emoji Converter\n")
        print("Enter Emoji to convert")
        emojiinput=input(">")
        print(f"\nEmoji >> {emojiinput}")
        print(f"Emoji text >> {emoji.demojize(emojiinput)}")
except (Exception,KeyboardInterrupt,ModuleNotFoundError):
    os.system("cls")
    print("Couldn't convert emoji.")
    exit()