from __future__ import absolute_import, print_function, division
import os.path
import traceback

import pandas as pd
from core import (Calendar, EventDate, WeekSchedule, Event, 
    EventTime, EventWriter)
from config import ConverterConfig

def main(fpath):
    cld = Calendar.from_excel(fpath)
    for col in cld.df.columns:
        print(cld.df[col])
        print('---')

def ed_test():
    src = '2017/08/26 ~ 2017/09/02'
    ed = EventDate.strptime(src)
    print(ed.begin, ed.end)
    print(ed.strftime())

def config_test():
    cfg = ConverterConfig()
    print(cfg.CalendarConfig.km)
    ws = WeekSchedule()
    print(ws.config.km)

def parse_test(fpath):
    cld = Calendar.from_excel(fpath)
    wss = cld.to_week_schedules()
    for i, ws in enumerate(wss):
        ws.to_csv(EventWriter(), 'test_csv{0}.csv'.format(i))
    # cld.to_excel('test_output.xlsx')

def event_test():
    from datetime import datetime as dt
    src = '*-泰安鄉運 @象鼻國小 (請著學校運動服)'.decode('utf-8')
    evnt = Event.parse(src, dt(2017,9,8))
    print(evnt)
    src = '12-泰安鄉運 @象鼻國小 (請著學校運動服)'.decode('utf-8')
    evnt = Event.parse(src, dt(2017,9,8))
    print(evnt)
    src = '12~18-泰安鄉運 @象鼻國小 (請著學校運動服)'.decode('utf-8')
    evnt = Event.parse(src, dt(2017,9,8))
    print(evnt)
    src = '12^9:00-泰安鄉運 @象鼻國小 (請著學校運動服)'.decode('utf-8')
    evnt = Event.parse(src, dt(2017,9,8))
    print(evnt)
    src = '12^9:00~16:00-泰安鄉運 @象鼻國小 (請著學校運動服)'.decode('utf-8')
    evnt = Event.parse(src, dt(2017,9,8))
    print(evnt)

def eventtime_test():
    src = '9:00 ~ 10:00'
    ct = EventTime.parse(src)
    print(ct.begin, ct.end)
    src = '9:00'
    ct = EventTime.parse(src)
    print(ct.begin, ct.end)


if __name__ == '__main__':
    try:
        fpath = r'data\template3.xlsx'
        # main(fpath)
        # wk_test()
        # config_test()
        parse_test(fpath)
        # event_test()
        # eventtime_test()
    except Exception as ex:
        print(ex)
        print(ex.message)
        # traceback.print_exc()
