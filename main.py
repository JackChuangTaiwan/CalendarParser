from __future__ import absolute_import, print_function, division
from argparse import ArgumentParser
import os
import traceback

from core import Calendar, EventWriter

CHECK_BIG5 = ['ifile', 'odir']


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-f', dest='ifile', metavar='input_file')
    parser.add_argument('-o', dest='odir', metavar='out_dir')
    try:    
        args = parser.parse_args()
    except:
        raise
    return args


def parse_calendar(ipath, opath):
    cld = Calendar.from_excel(ipath)
    wss = cld.to_week_schedules()
    for i, ws in enumerate(wss):
        fname_serial = 'WeekSchedule_{0}.csv'.format(i)
        fname = os.path.join(opath, fname_serial)
        ws.to_csv(EventWriter(), fname)


def main():
    args = parse_args()
    arg_dict = vars(args)
    try:
        if os.name == 'nt':
            for k in CHECK_BIG5:
                if arg_dict[k] != None:
                    arg_dict[k] = unicode(arg_dict[k], 'big5')
    except Exception as ex:
        print(ex.message)

    try:
        parse_calendar(args.ifile, args.odir)
    except:
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex.message)
        traceback.print_exc()
