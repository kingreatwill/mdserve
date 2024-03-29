import threading
from apscheduler.schedulers.background  import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from git import Repo
import os

class ScheduleServer(threading.Thread):
    def __init__(self, directory, crontab):
        super().__init__()
        self.directory = directory
        self.repo = None
        if os.path.exists(os.path.join(self.directory,".git")):
            self.repo = Repo(self.directory)
        # 默认整点执行一次
        self.crontab = crontab
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.sync, CronTrigger.from_crontab(self.crontab))

    def sync(self):
        if self.repo:
            g = self.repo.git
            print(g.pull())

    def run(self):
        self.scheduler.start()
