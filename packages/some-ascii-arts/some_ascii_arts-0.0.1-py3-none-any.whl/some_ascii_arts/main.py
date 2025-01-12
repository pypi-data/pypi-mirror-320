from some_ascii_arts.utils import BANANA_ASCII, CHOCOLATE_ASCII, MOON_ASCII
import argparse


def main():
    parser = argparse.ArgumentParser(
                        prog='asciiart',
                        description='Draws some ASCII art')

    parser.add_argument('art_type', help='Enter b, c, or m to print a banana, chocolate, or moon, respectively.')

    args = parser.parse_args()

    if args.art_type == 'b':
        print(BANANA_ASCII)
    elif args.art_type == 'c':
        print(CHOCOLATE_ASCII)
    elif args.art_type == 'm':
        print(MOON_ASCII)