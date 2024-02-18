#!/Users/Administrator/venv/misc12/Scripts/python
# from multiprocessing import Process
from threading import Thread

from notifications import Notifications


def main():
    noti_app = Notifications()
    functions = [
        # noti_app.test
        # noti_app.reddit_notify,
        # noti_app.github_notify,
        # noti_app.add_polymer,
    ]

    # processes: list[Process] = []
    # for f in functions:
    #     proc = Process(target=f)
    #     proc.start()
    #     processes.append(proc)

    # for proc in processes:
    #     proc.join()

    # noti_threads = [Thread(target=f) for f in functions]
    # for noti_thread in noti_threads:
    #     noti_thread.start()

    # for noti_thread in noti_threads:
    #     noti_thread.join()

    noti_app.add_polymer()


if __name__ == "__main__":
    main()
