import logging

import expect


def main():
    logging.info(__file__)
    logging.info(expect)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
