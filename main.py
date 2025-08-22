# main.py
from input_reader import read_schedule_xls
from processor import df_to_courses
from output_writer import generate_ics

def main():
    # 1. 读取 Excel
    df = read_schedule_xls("schedule.xls")

    # 2. 转换为 COURSES
    courses = df_to_courses(df)
    print("已解析课程数量:", len(courses))

    # 3. 生成 ICS
    generate_ics(courses, "schedule_2025.ics")

if __name__ == "__main__":
    main()