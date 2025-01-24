import os
from dotenv import load_dotenv

ENVS = ['dev', 'test', 'prod']


def setup_env(argv):
    if len(argv) != 2 or argv[1] not in ENVS:
        raise ValueError(
            'Please provide an environment: '
            f'{ENVS}. E.g. run_etl dev'
        )

    env = argv[1]

    cleanup_previous_env()
    os.environ['ENV'] = env

    # Throw an error or load the appropriate .env file
    if env is None:
        raise KeyError('ENV variable not set')

    env_file = '.env' if env == 'prod' else f'.env.{env}'
    print(f"Loading environment variables from: {env_file}")

    load_dotenv(env_file, override=True)

    # Print environment variables for debugging
    # print(f"SOURCE_DB_NAME: {os.getenv('SOURCE_DB_NAME')}")
    # print(f"SOURCE_DB_USER: {os.getenv('SOURCE_DB_USER')}")
    # print(f"SOURCE_DB_PASSWORD: {os.getenv('SOURCE_DB_PASSWORD')}")
    # print(f"SOURCE_DB_HOST: {os.getenv('SOURCE_DB_HOST')}")
    # print(f"SOURCE_DB_PORT: {os.getenv('SOURCE_DB_PORT')}")


def cleanup_previous_env():
    # Clear relevant environment variables
    keys_to_clear = [
        'SOURCE_DB_NAME', 'SOURCE_DB_USER', 'SOURCE_DB_PASSWORD',
        'SOURCE_DB_HOST', 'SOURCE_DB_PORT',
        'TARGET_DB_NAME', 'TARGET_DB_USER', 'TARGET_DB_PASSWORD',
        'TARGET_DB_HOST', 'TARGET_DB_PORT'
    ]
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]
