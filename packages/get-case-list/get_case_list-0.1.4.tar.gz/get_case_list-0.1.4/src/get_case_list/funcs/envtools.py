import os

VALID_KEYS = [
    "INSPECTOR_PREFIX",
    "INSPECTOR_FULLNAME",
    "INSPECTOR_POSITION",
    "SUB_INSPECTOR_PREFIX",
    "SUB_INSPECTOR_FULLNAME",
    "SUB_INSPECTOR_POSITION",
    "SUPER_INTENDENT_PREFIX",
    "SUPER_INTENDENT_FULLNAME",
    "SUPER_INTENDENT_POSITION",
    "TEAMNO",
]


def check_env():
    env_file_path = ".env"

    if os.path.exists(env_file_path):
        with open(env_file_path, "r", encoding="utf-8") as file:
            existing_keys = [line.split("=")[0].strip() for line in file.readlines()]

        if set(existing_keys) == set(VALID_KEYS):
            print(f"{env_file_path} already exists with valid keys.")
        else:
            print(f"Keys in {env_file_path} do not match the expected keys.")
            print("Regenerating the .env file with valid keys.")
            os.remove(env_file_path)
            regenerate_env_file()

    else:
        regenerate_env_file()


def regenerate_env_file():
    user_inputs = {}

    for key in VALID_KEYS:
        value = input(f"Please enter {key} value: ")

        if not value.strip():
            print(f"Invalid input for {key}. Please provide a valid value.")
            return

        user_inputs[key] = value

    with open(".env", "w+", encoding="utf-8") as file:
        for key, value in user_inputs.items():
            file.write(f"{key}={value}\n")

    print(f"Data saved to .env")
