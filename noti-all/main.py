#!/Users/Administrator/venv/misc/Scripts/python
from multiprocessing import Process

from notifications import Notifications


def main():
    noti_app = Notifications()
    functions = [
        noti_app.reddit_notify,
        noti_app.github_notify,
        noti_app.add_polymer
    ]

    processes: list[Process] = []
    for f in functions:
        proc = Process(target=f)
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()


if __name__ == "__main__":
    main()