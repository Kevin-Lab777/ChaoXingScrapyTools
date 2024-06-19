import scrapy
from scrapy.http import Request, FormRequest
from fake_useragent import UserAgent
import re

class ChaoxingSpider(scrapy.Spider):
    name = "chaoxing"
    allowed_domains = ["chaoxing.com"]
    login_url = "https://passport2.chaoxing.com/fanyalogin"
    start_url = "https://mooc1.chaoxing.com/mycourse/studentcourse?courseId=240821064&clazzid=92272541&cpi=198360568&enc=a11512d4dc0e9223812f52e317f00d47"

    def __init__(self, *args, **kwargs):
        self.ua = UserAgent()
        self.catalog = []  # 用于存储目录结构
        self.cookies = None  # 用于保存登录后的 cookies
        super().__init__(*args, **kwargs)

    def start_requests(self):
        headers = {
            "User-Agent": self.ua.random,
        }
        formdata = {
            "fid": "-1",
            "uname": "F%2F0HCD0PNlRN0O7gmDlqyQ%3D%3D",
            "password": "vy%2FaxDEDq6mdvgnoQCpoag%3D%3D",
            "refer": "https%253A%252F%252Fi.chaoxing.com",
            "t": "true",
            "forbidotherlogin": "0",
            "validate": "",
            "doubleFactorLogin": "0",
            "independentId": "0",
            "independentNameId": "0"
        }
        yield Request(
            self.login_url,
            method='POST',
            headers=headers,
            body=self.urlencode(formdata),
            callback=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        if "登录成功" in response.text:  # 检查登录是否成功
            self.cookies = response.headers.getlist('Set-Cookie')  # 保存 cookies
            headers = {
                "User-Agent": self.ua.random,
            }
            yield Request(self.start_url, headers=headers, cookies=self.cookies, callback=self.parse)
        else:
            self.log("登录失败")

    def parse(self, response):
        i = 1
        while True:
            # 尝试获取每个一级标题的节点
            first_level_title_xpath = f'/html/body/div[5]/div[1]/div[2]/div[3]/div[{i}]/h2/span/a'
            first_level_title = response.xpath(first_level_title_xpath)

            if not first_level_title:
                break

            title_text = first_level_title.xpath('@title').get()
            if title_text:
                title_text = title_text.strip()
            title_link = first_level_title.xpath('@href').get()
            self.log(f'一级标题: {title_text} - 链接: {title_link}')

            chapter = {
                'title': title_text,
                'link': title_link,
                'subtitles': []
            }

            # 遍历二级标题
            j = 1
            while True:
                second_level_title_xpath = f'/html/body/div[5]/div[1]/div[2]/div[3]/div[{i}]/div[{j}]/h3/a'
                second_level_title = response.xpath(second_level_title_xpath)

                if not second_level_title:
                    break

                sub_title_text = second_level_title.xpath('@aria-label').get()
                if sub_title_text:
                    sub_title_text = sub_title_text.strip()
                sub_title_link = second_level_title.xpath('@href').get()

                chapter['subtitles'].append({
                    'title': sub_title_text,
                    'link': sub_title_link
                })

                j += 1
            self.catalog.append(chapter)
            i += 1

        self.print_catalog()

        # 用户选择【1】进行筛选
        user_input = input("选择【1】爬取课程题目并筛选包含'Quiz'和'Test'的章节: ")
        if user_input == '1':
            self.filter_catalog()

    def print_catalog(self):
        print("\n原课程目录：")
        for chapter in self.catalog:
            print(f"--: {chapter['title']} ")
            for subtitle in chapter['subtitles']:
                print(f"    ----: {subtitle['title']} ")

    def filter_catalog(self):
        filtered_catalog = []
        for chapter in self.catalog:
            filtered_chapter = {
                'title': chapter['title'],
                'link': chapter['link'],
                'subtitles': []
            }
            for subtitle in chapter['subtitles']:
                if re.search(r'quiz|test', subtitle['title'], re.IGNORECASE):
                    filtered_chapter['subtitles'].append(subtitle)
            if filtered_chapter['subtitles']:
                filtered_catalog.append(filtered_chapter)

        self.print_filtered_catalog(filtered_catalog)

    def print_filtered_catalog(self, filtered_catalog):
        print("\n筛选后的课程目录：")
        for chapter in filtered_catalog:
            print(f"--: {chapter['title']} ")
            for subtitle in chapter['subtitles']:
                print(f"    ----: {subtitle['title']} ")

    def urlencode(self, formdata):
        from urllib.parse import urlencode
        return urlencode(formdata)

