from .constants import DIR, META_JSON_FRAME

def main():
    with (DIR / "meta.json").open("w") as file:
        file.write(META_JSON_FRAME)
    print("meta.json reset was successful")

if __name__ == "__main__":
    main()