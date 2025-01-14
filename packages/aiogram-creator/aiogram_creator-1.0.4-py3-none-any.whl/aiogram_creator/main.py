import argparse
import shutil
import os

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('command', choices=['create'])
    # parser.add_argument('--token', required=False, help='Telegram token')

    args = parser.parse_args()

    if args.command == 'create':
        create_object()

def create_object():
    print(f'Creating...')
    shutil.copytree('./template', os.getcwd())
    print('Done')


if __name__ == '__main__':
    main()
