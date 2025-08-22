# output_writer.py
from pathlib import Path
from datetime import datetime, date, timedelta
import uuid

# 这里放上之前写的 generate_ics 函数和工具函数
# 省略，直接复用# -*- coding: utf-8 -*-

# ===== 1) 节次时间（按你给的标准） =====
PERIODS = {
    1: ("08:00", "08:50"),
    2: ("09:00", "09:50"),
    3: ("10:10", "11:00"),
    4: ("11:10", "12:00"),
    5: ("13:00", "13:50"),
    6: ("14:00", "14:50"),
    7: ("15:10", "16:00"),
    8: ("16:10", "17:00"),
    9: ("17:10", "18:00"),
    10: ("18:40", "19:30"),
    11: ("19:40", "20:30"),
    12: ("20:40", "21:30"),
}

# ===== 2) 学期边界 =====
SEMESTER_START = date(2025, 9, 8)   # 开始（week1 所在周）
SEMESTER_END   = date(2025, 12, 29) # 结束（含）

# ===== 工具函数 =====
def to_dt(d: date, hm: str) -> datetime:
    hh, mm = map(int, hm.split(":"))
    return datetime(d.year, d.month, d.day, hh, mm)

def week1_monday(start: date) -> date:
    # 找到第1周的周一（周一=0）
    return start - timedelta(days=start.weekday())

def week_number(d: date, w1_mon: date) -> int:
    return ((d - w1_mon).days // 7) + 1

def week_range_to_dates(w_start: int, w_end: int, w1_mon: date, weekday: int):
    res = []
    for w in range(w_start, w_end + 1):
        day = w1_mon + timedelta(days=(w - 1) * 7 + (weekday - 1))
        if SEMESTER_START <= day <= SEMESTER_END:
            res.append(day)
    return res

def periods_to_times(periods):
    if isinstance(periods, list) and len(periods) == 2 and periods[1] >= periods[0]:
        p_start, p_end = periods[0], periods[1]
    else:
        arr = []
        for p in (periods if isinstance(periods, list) else [periods]):
            if isinstance(p, int):
                arr.append(p)
            elif isinstance(p, (list, tuple)) and len(p) == 2:
                arr.extend(range(p[0], p[1] + 1))
        arr = sorted(set(arr))
        p_start, p_end = arr[0], arr[-1]
    return PERIODS[p_start][0], PERIODS[p_end][1]

def make_rrule(first_date: date, rule: str, until_date: date):
    w1_mon = week1_monday(SEMESTER_START)
    d = first_date
    if rule == "weekly":
        interval = 1
    elif rule in ("odd", "even"):
        interval = 2
        w = week_number(d, w1_mon)
        if (rule == "odd" and w % 2 == 0) or (rule == "even" and w % 2 == 1):
            d += timedelta(days=7)
    else:
        interval = 1
    rrule = f"FREQ=WEEKLY;INTERVAL={interval};UNTIL={until_date.strftime('%Y%m%d')}T235959Z"
    return d, rrule

def ics_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

def build_event(name, location, start_dt: datetime, end_dt: datetime, rrule: str):
    uid = f"{uuid.uuid4()}@local"
    return "\n".join([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART;TZID=Asia/Shanghai:{start_dt.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND;TZID=Asia/Shanghai:{end_dt.strftime('%Y%m%dT%H%M%S')}",
        f"RRULE:{rrule}",
        f"SUMMARY:{ics_escape(name)}",
        f"LOCATION:{ics_escape(location)}",
        "END:VEVENT",
    ])

def generate_ics(courses, out_path: str):
    w1_mon = week1_monday(SEMESTER_START)
    events = []
    for c in courses:
        name = c["name"]
        loc  = c.get("location", "")
        wd   = c["weekday"]  # 1-7, 周一=1
        periods = c["periods"]
        rule = c["rule"]

        start_hm, end_hm = periods_to_times(periods)

        # week1 对应的星期几
        first_day = w1_mon + timedelta(days=(wd - 1))
        if first_day < SEMESTER_START:
            first_day = SEMESTER_START + timedelta(days=(wd - SEMESTER_START.isoweekday()))

        if rule == "weeks":
            w_start, w_end = c["weeks"]
            dates = week_range_to_dates(w_start, w_end, w1_mon, wd)
            if not dates:
                continue
            first = dates[0]
            last  = dates[-1]
            rrule = f"FREQ=WEEKLY;INTERVAL=1;UNTIL={last.strftime('%Y%m%d')}T235959Z"
            events.append(build_event(name, loc, to_dt(first, start_hm), to_dt(first, end_hm), rrule))
        else:
            start_date, rrule = make_rrule(first_day, rule, SEMESTER_END)
            events.append(build_event(name, loc, to_dt(start_date, start_hm), to_dt(start_date, end_hm), rrule))

    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\nPRODID:-//Course2ICS//CN//EN\n" + "\n".join(events) + "\nEND:VCALENDAR\n"
    Path(out_path).write_text(ics, encoding="utf-8")
    print(f"已生成：{out_path}")

