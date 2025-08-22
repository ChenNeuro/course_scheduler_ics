# 📚 课程表导入日历工具（离线版）

一个本地运行的 Python 工具，可以将教学网下载的 **Excel 课表** 转换为 `.ics` 日历文件，方便导入 Apple Calendar / Google Calendar。

---

## 📸 使用流程示意图

### 1. 下载 Excel 课表
从教学网导出 Excel 文件（一般是 `.xls` 格式）。

![Screenshot 2025-08-22 at 13.15.50](https://raw.githubusercontent.com/ChenNeuro/img/master/img/Screenshot%202025-08-22%20at%2013.15.50.png)



---

### 2. 安装依赖环境
请确保你已经安装 **Python 3.9+**，然后在项目目录执行：

```
pip install -r requirements.txt
```



------

### **3. 运行程序**

把下载的 schedule.xls 放到项目目录下，然后运行：

```
python main.py
```

程序会自动解析课表并生成 `schedule_2025.ics` 文件。



------

### **4. 导入到日历**



#### **Apple Calendar（Mac / iPhone）**



-   打开日历 → 文件 → 导入
-   选择生成的 courses.ics
-   确认后课程就会出现在日历中



#### **Google Calendar**



-   打开 Google Calendar（网页版）
-   左下角 → “其他日历” → “导入”
-   选择 courses.ics，确认导入





------





## **🛠 技术栈**



-   Python pandas → 解析 Excel
-   ics.py → 生成 .ics 文件
-   支持单双周、周数范围、考试时间解析



------





## **📄 License**



MIT License
