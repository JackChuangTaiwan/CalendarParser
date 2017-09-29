from __future__ import absolute_import, print_function, division
import pandas as pd
import re
from datetime import datetime as dt
from datetime import timedelta as td

from config import ConverterConfig
 
__all__ = []

# TODO: set `datetime_format` by reading from config file
DT_FMT = 'yyyy/MM/dd'   # datetime_format
UT_FACTOR = 1000000000
DT_FMT_YMD = '%Y/%m/%d'
DT_FMT_YMDHM = '%Y/%m/%d %H:%M'
DT_DELTA_DAY = 'days'
DT_DELTA_HOUR = 'hours'
DT_FMT_HM = '%H:%M'

class XlsxFile(object):
    def __init__(self):
        self.df = None

    @classmethod
    def from_excel(clz, fpath, header=None):
        try:
            xlsx = clz()
            xlsx.df = pd.read_excel(fpath, header=header)
        except:
            raise
        return xlsx

    def to_excel(self, opath, header=None):
        """
        Parameters
        ----------
        opath : string
            Output path.
        header : array_like
            Column names to be written.

        Note
        ----
        Some of `df.columns` might be appended with suffixes if there are 
        duplicate names.
        If users don't want the modified column names, they can overwrite 
        them by giving `header`.
        """
        writer = pd.ExcelWriter(opath, datetime_format=DT_FMT)
        self.df.to_excel(writer, index=False)
        if header is not None:
            pd.DataFrame(header).transpose().to_excel(writer, index=False, 
                header=False, startrow=0)
        writer.save()


ue = lambda x: x.encode('utf-8')
ud = lambda x: x.decode('utf-8')

class EventWriter(object):
    def __init__(self):
        self.config = ConverterConfig().CsvWriterConfig
        self.km_sec = self.config.km_sec

    def write(self, f, obj):
        km = self.config.km
        events = obj.events

        # write header
        header = [k for k in km]
        f.write(','.join(header) + '\n')

        # work-around: insert section name into title
        # step01: find the index of the header `Subject`
        idx = header.index(u'Subject')

        # write content
        for i in range(len(events)):
            # replace all `None` by empty string
            temp = [events[i][km[k]] if events[i][km[k]] is not None else ''
                    for k in km]
            temp[idx] = u'{0}:{1}'.format(self.km_sec[obj.__class__.__name__], 
                        temp[idx])
            # encode utf-8 into unicode
            temp = [ue(val) if type(val) is unicode else val for val in temp]
            

            for i, val in enumerate(temp):
                if type(val) is dt:
                    temp[i] = val.strftime(DT_FMT_YMD)
            content = map(str, temp)
            line = ','.join(content)
            f.write(line + '\n')


class Calendar(XlsxFile):
    def __init__(self):
        super(Calendar, self).__init__()
        self.lh = None  # left side header
        self.df = None
        self.config = ConverterConfig().CalendarConfig

    @classmethod
    def from_excel(clz, fpath):
        obj = super(Calendar, clz).from_excel(fpath)
        obj.lh = obj.df[0]
        obj.df.drop(obj.df.columns[0], axis=1, inplace=True)
        return obj

    def to_week_schedules(self):
        res = []
        self._fill_na_theme()
        for col in self.df.columns:
            ws = WeekSchedule.parse(self.df[col], self.lh)
            res.append(ws)
        return res

    # Helper method, not a generic method
    def _fill_na_theme(self):
        idx_theme = self.lh.index[self.lh == self.config.km['theme']]
        target = self.df.ix[idx_theme].squeeze().tolist()
        length = len(target)

        # Fill fields in even number by the value of fields in odd number.
        target[1::2] = target[:length-length%2:2]
        # Re-assign value back to the target
        self.df.iloc[idx_theme] = target


class WeekSchedule(object):
    def __init__(self):
        self.week = ''
        self.date = None
        self.theme = ''
        self.tg = ''    # trafic guard
        self.admin = None
        self.academic = None
        self.student = None
        self.hygiene = None
        self.general = None
        self.kingdergarten = None
        self.config = ConverterConfig().CalendarConfig
        self.hidx = lambda k: self.config.ho[self.config.km[k]]

    def keys(self):
        return ['week', 'date', 'theme', 'tg', 'admin', 'academic', 'student', 
                'hygiene', 'general', 'kingdergarten']

    def sections(self):
        return ['admin', 'academic', 'student', 'hygiene', 'general', 
                'kingdergarten']

    @classmethod
    def parse(clz, col, lh, reset_lh=False):
        """
        Parameters
        ----------
        col : pandas.Series
            Single column of schedule to be parsed.
        lh : pandas.Series
            Left side header of schedule.
        reset_lh : bool
            Reset left side header everytime a new object is created by 
            this method.

        Returns
        -------
        ws : WeekSchedule
        """
        ws = WeekSchedule()

        # TODO: try to do this automatically
        # get the order (index) of left side header
        if ws.config.ho is None or reset_lh:
            ws.config.set_header_order(lh)

        ws.week = col[ws.hidx('week')]
        ws.date = EventDate.strptime(col[ws.hidx('date')])

        # TODO: theme in even weeks is empty, fill them
        ws.theme = col[ws.hidx('theme')] 
        ws.tg = col[ws.hidx('tg')]

        ws.admin = AdminAffair.parse(col[ws.hidx('admin')], ws.date)
        ws.academic = AcademicSection.parse(col[ws.hidx('academic')], ws.date)
        ws.student = StudentSection.parse(col[ws.hidx('student')], ws.date)
        ws.hygiene = HygieneSection.parse(col[ws.hidx('hygiene')], ws.date)
        ws.general = GeneralAffair.parse(col[ws.hidx('general')], ws.date)
        ws.kingdergarten = Kingdergarten.parse(col[ws.hidx('kingdergarten')], 
                                               ws.date)
        return ws

    def __getitem__(self, key):
        return self.__dict__[key]

    def to_csv(self, writer, path, mode='w'):
        if mode.lower() not in ['w', 'a']:
            raise ValueError('Mode can only be `w`(write) or `a`(append).')
        # TODO: export to csv using utf-8 coding
        with open(path, mode) as f:
            for sec in self.sections():
                writer.write(f, self[sec])


class EventDate(object):
    def __init__(self):
        self.begin = None
        self.end = None
        self.fmt = None

    def __repr__(self):
        return self.strftime()

    @classmethod
    def last_day_of_month(clz, date):
        next_month = date.replace(day=28) + td(days=4)
        return (next_month - td(days=next_month.day)).day

    @classmethod
    def get_timedelta(clz, ref_date, src):
        num = int(src)
        if num < ref_date.day:
            num += clz.last_day_of_month(ref_date)
        delta = {'days': num - ref_date.day}
        return td(**delta)

    @classmethod
    def strptime(clz, src, fmt=None):
        wd = clz()
        if fmt is None:
            fmt = DT_FMT_YMD
        wd.fmt = fmt

        temp = src.split('~')
        wd.begin = dt.strptime(temp[0].strip(), fmt)
        if len(temp) == 2:
            wd.end = dt.strptime(temp[1].strip(), fmt)
        return wd

    @classmethod
    def parse(clz, ref_date, src_begin, src_end=None):
        """
        An week-based datetime parser.
        """
        obj = clz()
        obj.begin = ref_date + clz.get_timedelta(ref_date, src_begin)

        if src_end is not None:
            obj.end = ref_date + clz.get_timedelta(ref_date, src_end)
        return obj

    def strftime(self, fmt=None):
        if fmt is None:
            fmt = self.fmt if self.fmt is not None else DT_FMT_YMD
        if self.end is not None:
            return '{0} ~ {1}'.format(self.begin.strftime(fmt), 
                                      self.end.strftime(fmt))
        else:
            return self.begin.strftime(fmt)


class EventTime(object):
    def __init__(self, **kwargs):
        self.begin = None
        self.end = None

    @classmethod
    def parse(clz, src, fmt=DT_FMT_HM):
        temp = src.split('~')
        ct = clz()
        t = dt.strptime(temp[0].strip(), fmt)
        ct.begin = td(hours=t.hour, minutes=t.minute)
        if len(temp) == 2:
            t = dt.strptime(temp[1].strip(), fmt)
            ct.end = td(hours=t.hour, minutes=t.minute)
        return ct


class EventDateTime(object):
    def __init__(self):
        self.bdate = None
        self.edate = None
        self.btime = None
        self.etime = None

    @classmethod
    def parse(clz, ref_date, src_date, src_time=None, fmt_date=None, 
              fmt_time=None):
        obj = clz()
        ed = EventDate.parse(src_date)
        obj.bdate, obj.edate = ed.begin, ed.end
        if src_time is not None:
            et = EventTime.parse(src_time)
            obj.btime, obj.etime = et.begin, et.end
        return obj


class Event(object):
    """
    Note
    ----
    pattern of src:
        1. Date is specified
            [date] - [title] @[location]? ([description])?
        2. No date is specified
            *title @[location]? ([description])?
    pattern:
        \u4e00-\u9fcc : 
            chinese characters
        \uff0c\u3001 :
            full word of comma
        (^(\d+)\s*\^(\d+\:\d+(\~\d+\:\d+)?)) :
            `date ^ HH:mm ~ HH:mm`
        (^(\d+)(\s*\~\s*(\d+))?) :
            `date_1 ~ date_2`
        (\s*\@([\w\u4e00-\u9fcc\uff0c\u3001\,]+))? :
            `@[location]`, optional
        (\s*\(([\w\u4e00-\u9fcc\uff0c\u3001\,]+)\))? :
            `([description])`, optional
    """
    pat_time1 = '(^(\d+)\s*\^(\d+\:\d+(\~\d+\:\d+)?))'
    pat_time2 = '(^(\d+)(\s*\~\s*(\d+))?)'
    pat_time3 = '(^\*)'
    pat_title = '([\w\u4e00-\u9fcc\uff0c\u3001\,]+)'
    pat_loc = '(\s*\@([\w\u4e00-\u9fcc\uff0c\u3001\,]+))?'
    pat_des = '(\s*\(([\w\u4e00-\u9fcc\uff0c\u3001\,]+)\))?'
    regex = re.compile(r'({0}|{1}|{2})\s*\-\s*{3}{4}{5}'.format(pat_time1,
            pat_time2, pat_time3, pat_title, pat_loc, pat_des), re.UNICODE)

    def __init__(self):
        self.bdate = None
        self.edate = None
        self.btime = None
        self.etime = None
        self.title = None
        self.location = None
        self.description = None

    def __repr__(self):
        res = (
        u'Event: {0}; bdate: {1}; btime: {2}; edate: {3}; etime: {4}; '
        'loc: {5}; des: {6}\n'
        ).format(
        self.title, 
        self.bdate.strftime(DT_FMT_YMD) if self.bdate is not None else None, 
        self.btime, 
        self.edate.strftime(DT_FMT_YMD) if self.edate is not None else None, 
        self.etime, 
        self.location,
        self.description
        )
        return res.encode('utf-8')

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, key):
        return self.__dict__[key]

    def keys(self):
        return self.__dict__.keys()

    @classmethod
    def parse(clz, src, ref_date=None, failed_value=None):
        """
        Parameters
        ----------
        src : string
            String to be parsed.
        ref_date : datetime
            Beginning date of a week.
        failed_value : object
            Value to be returned if regex parser failed.
        """
        parts = clz.regex.split(src)

        if len(parts) < 15:
            return failed_value

        obj = Event()
        if parts[10] == u'*':
            # if there is no specified date, use ref_date as its date
            obj.bdate = ref_date
        elif parts[7] is not None:
            # date
            ed = EventDate.parse(ref_date, parts[7], parts[9])
            obj.bdate = ed.begin
            obj.edate = ed.end

            # work-around: multiple day event can not be set by only two `date`,
            # it need additional `time` info. 
            # (This bug only occurs when events are imported to Google calendar 
            #  by .csv files)
            if ed.end is not None:
                et = EventTime.parse('8:00~17:00')
                obj.btime = et.begin
                obj.etime = et.end
        elif parts[3] is not None:
            # time
            ed = EventDate.parse(ref_date, parts[3])
            obj.bdate = ed.begin

            et = EventTime.parse(parts[4])
            if et.end is not None:
                obj.edate = ed.begin
            obj.btime = et.begin
            obj.etime = et.end
        else:
            raise Exception('Cannot parse string correctly.')

        # those content which may contains commas should be enclosed by `""`
        obj.title = (u'\"{0}\"'.format(parts[11]) 
            if parts[11] is not None else '')
        obj.location = parts[13]
        obj.description = (u'\"{0}\"'.format(parts[15]) 
            if parts[15] is not None else '')
        return obj


class AffairBase(object):
    def __init__(self):
        self.events = None

    def __repr__(self):
        evnt_content = ';'.join(map(str, self.events))
        res = '{0}:\n {1}'.format(self.__class__.__name__, evnt_content)
        return res

    @classmethod
    def parse(clz, src, weekdate):
        obj = clz()
        content = src.split('\n')
        temp = [Event.parse(val, ref_date=weekdate.begin) for val in content]
        obj.events = [val for val in temp if val is not None]
        return obj


class AdminAffair(AffairBase):
    def __init__(self):
        super(AdminAffair, self).__init__()


class AcademicSection(AffairBase):
    def __init__(self):
        super(AcademicSection, self).__init__()


class StudentSection(AffairBase):
    def __init__(self):
        super(StudentSection, self).__init__()


class HygieneSection(AffairBase):
    def __init__(self):
        super(HygieneSection, self).__init__()


class GeneralAffair(AffairBase):
    def __init__(self):
        super(GeneralAffair, self).__init__()


class Kingdergarten(AffairBase):
    def __init__(self):
        super(Kingdergarten, self).__init__()
