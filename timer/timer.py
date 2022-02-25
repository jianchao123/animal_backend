# coding:utf-8
from apscheduler.schedulers.gevent import GeventScheduler

from ssc_timer import SscTimer
from robot_timer import RobotTimer
from new_period_timer import NewPeriodTimer
from open_lottery_timer import OpenLotteryTimer
from cache_timer import CacheTimer
from utils import get_logger
import conf


if __name__ == "__main__":
    sched = GeventScheduler()

    newperiodtimer = NewPeriodTimer(get_logger(conf.log_path))
    sched.add_job(newperiodtimer.start_period, 'interval', seconds=2)

    openlotterytimer = OpenLotteryTimer(get_logger(conf.log_path))
    sched.add_job(openlotterytimer.participate_finish, 'interval', seconds=1)
    sched.add_job(openlotterytimer.set_countdown_key, 'interval', seconds=1)
    sched.add_job(openlotterytimer.calculate_result, 'interval', seconds=1)
    sched.add_job(openlotterytimer.open_lottery, 'interval', seconds=1)

    # cq_ssc = SscTimer(get_logger(conf.log_path))
    # sched.add_job(cq_ssc.cq_ssc_number, 'interval', seconds=30)

    robot = RobotTimer(conf.url, get_logger(conf.log_path))
    sched.add_job(robot.robot_buy, 'interval', seconds=10)

    cache_time = CacheTimer(get_logger(conf.log_path))
    sched.add_job(cache_time.homepage_rest_cache, 'interval', seconds=10)

    g = sched.start()
    g.join()
