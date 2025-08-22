# processor.py
import re
import pandas as pd

CN_DIGIT = {"零":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}

def cn_num_to_int(token: str) -> int:
    token = token.strip()
    if token.isdigit():
        return int(token)
    if token == "十":
        return 10
    if len(token) == 2 and token[0] in CN_DIGIT and token[1] == "十":
        return CN_DIGIT[token[0]] * 10
    if len(token) == 2 and token[0] == "十" and token[1] in CN_DIGIT:
        return 10 + CN_DIGIT[token[1]]
    if len(token) == 3 and token[0] in CN_DIGIT and token[1] == "十" and token[2] in CN_DIGIT:
        return CN_DIGIT[token[0]] * 10 + CN_DIGIT[token[2]]
    if len(token) == 1 and token in CN_DIGIT:
        return CN_DIGIT[token]
    s = 0
    for ch in token:
        if ch in CN_DIGIT:
            s = s * 10 + CN_DIGIT[ch]
    return s

def extract_period_range(row_label: str) -> tuple[int,int]:
    text = str(row_label)
    arabics = re.findall(r'\d+', text)
    if arabics:
        nums = list(map(int, arabics))
        return (min(nums), max(nums))
    tokens = re.findall(r'十[一二三四五六七八九]?|[一二两三四五六七八九]', text)
    if tokens:
        nums = [cn_num_to_int(tok) for tok in tokens]
        return (min(nums), max(nums))
    return (1,1)

def parse_cell_text(cell_text: str, weekday: int, period_range: tuple[int,int]) -> list[dict]:
    if cell_text is None:
        return []
    text = str(cell_text).strip()
    if not text or text.lower() == "nan":
        return []

    parts = [p.strip() for p in text.split("——————") if p.strip()]
    results = []
    for part in parts:
        loc_matches = list(re.finditer(r"\(([^()]*教[^()]*)\)", part))
        location = ""
        name_part = part
        if loc_matches:
            last = loc_matches[-1]
            location = last.group(1).strip()
            name_part = part[:last.span()[0]].strip()
        remark = ""
        m_remark = re.search(r"\((备注[^)]*)\)", part)
        if m_remark:
            remark = m_remark.group(1).strip()
        rule = "weekly"
        weeks = None
        if "单周" in part:
            rule = "odd"
        elif "双周" in part:
            rule = "even"
        else:
            m_weeks = re.search(r"(\d+)\s*[-–~至到]\s*(\d+)\s*周", part)
            if m_weeks:
                rule = "weeks"
                weeks = [int(m_weeks.group(1)), int(m_weeks.group(2))]
        exam_time = None
        m_exam = re.search(r"考试时间[:：]\s*(\d+)\s*(上午|下午|晚上)?", part)
        if m_exam:
            exam_time = m_exam.group(1) + (m_exam.group(2) or "")
        name = name_part.rstrip("；;，, ").strip()
        item = {
            "name": name,
            "location": location,
            "weekday": weekday,
            "periods": [period_range[0], period_range[1]],
            "rule": rule
        }
        if weeks: item["weeks"] = weeks
        if remark: item["remark"] = remark
        if exam_time: item["exam_time"] = exam_time
        results.append(item)
    return results

def merge_courses(courses: list[dict]) -> list[dict]:
    """合并同一天、同课、连续节次的课程"""
    grouped = {}
    for c in courses:
        key = (
            c["name"], c.get("location",""), c["weekday"],
            c["rule"], tuple(c.get("weeks",[])),
            c.get("remark",""), c.get("exam_time","")
        )
        grouped.setdefault(key, []).append(c["periods"])
    merged = []
    for key, plist in grouped.items():
        plist = sorted(plist, key=lambda x: x[0])
        cur_start, cur_end = plist[0]
        for (s,e) in plist[1:]:
            if s == cur_end + 1:
                cur_end = e
            else:
                merged.append(make_course_from_key(key, [cur_start, cur_end]))
                cur_start, cur_end = s, e
        merged.append(make_course_from_key(key, [cur_start, cur_end]))
    return merged

def make_course_from_key(key, periods):
    name, location, weekday, rule, weeks, remark, exam_time = key
    course = {
        "name": name,
        "location": location,
        "weekday": weekday,
        "periods": periods,
        "rule": rule
    }
    if weeks: course["weeks"] = list(weeks)
    if remark: course["remark"] = remark
    if exam_time: course["exam_time"] = exam_time
    return course

def df_to_courses(df) -> list[dict]:
    courses = []
    weekday_map = {i+1: col for i, col in enumerate(df.columns)}
    for weekday, col in weekday_map.items():
        for row_label, cell in df[col].items():
            if pd.isna(cell) or not str(cell).strip() or str(cell).lower()=="nan":
                continue
            p_start, p_end = extract_period_range(str(row_label))
            courses.extend(parse_cell_text(str(cell), weekday, (p_start, p_end)))
    return merge_courses(courses)