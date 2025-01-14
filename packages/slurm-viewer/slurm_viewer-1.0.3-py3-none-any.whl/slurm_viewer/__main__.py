import rich.traceback

from slurm_viewer.app import SlurmViewer


def main() -> None:
    rich.traceback.install(width=200)
    SlurmViewer().run()


if __name__ == "__main__":
    main()
