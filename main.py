from __future__ import absolute_import, print_function, division
from argparse import ArgumentParser
import os
import traceback

from core import Calendar, EventWriter

CHECK_BIG5 = ['ifile', 'odir']


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('ifile', metavar='input_file',
                        help='path of input file')
    parser.add_argument('-o', nargs='?', dest='odir', metavar='out_dir', 
                        default='',
                        help=('output directory, if not specified, output files'
                        'will be generated at the working directory'))
    parser.add_argument('-m', '--mode', nargs='?', dest='mode', metavar='mode',
                        default='single',
                        help=('output mode:\n`single`: content of all weeks '
                        'will be saved in one file.\n`splitted`: content will'
                        'be splitted into several files according to weeks'))
    try:
        args = parser.parse_args()
    except:
        raise
    return args


def parse_calendar(ipath, opath, output_mode='single'):
    if output_mode.lower() not in ['single', 'multiple']:
        raise ValueError('`output_mode` can only be `single` or `multiple`.')
    cld = Calendar.from_excel(ipath)
    wss = cld.to_week_schedules()

    bname, ext = os.path.basename(ipath).split('.')
    for i, ws in enumerate(wss):
        if output_mode == 'single':
            fname = 'cnv_{0}.csv'.format(bname)
            mode = 'w' if i == 0 else 'a'
        elif output_mode == 'multiple':
            fname = 'cnv_{0}_{1}.csv'.format(bname, i)
            mode = 'w'
        fname = os.path.join(opath, fname)
        ws.to_csv(EventWriter(), fname, mode=mode)

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
        parse_calendar(args.ifile, args.odir, output_mode=args.mode)
    except:
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex.message)
        traceback.print_exc()
