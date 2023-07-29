from icecream import ic

from notification import Notification

from utils_reddit import load_json


def main():
    config = load_json('config.json')
    
    noti_app = Notification(config)
    noti_app.get_noti()
    # noti_app.notify()


if __name__ == "__main__":
    main()