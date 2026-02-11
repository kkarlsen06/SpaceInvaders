"""Entry point: python -m space_invaders"""

from space_invaders.game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
