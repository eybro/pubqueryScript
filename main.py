from facebook_scraper import get_posts
import dateparser
import pymysql
import datetime
import os

USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
DB = os.environ["DB"]

# List of fb names for all pubs
PAGE_LIST = ['bergsklubbmasteri', 'Klubbmasteriet', 'openklubbmasteri', 'kfkflygsektionen', 'ProgramRadet',
             'BBQlubbmasteri',
             'qbmrosagrisen', 'datasklubbmasteri', 'clubwasteriet', 'fysiksklubbmasteri', 'kemisklubbmasteri',
             'festerietarkitektur', 'IndustriellEkonomiKTH']
# Keywords to look for
WORD_LIST = ['THIS', 'TODAY', 'TOMORROW', 'AT', 'MON,', 'TUE,', 'WED,', 'THU,', 'FRI,', 'SAT,', 'SUN,']
DAY_DICT = {'MONDAY': 0, 'TUESDAY': 1., 'WEDNESDAY': 2, 'THURSDAY': 3, 'FRIDAY': 4, 'SATURDAY': 5, 'SUNDAY': 6}


def get_events(page):
    d = {}
    for post in get_posts(page, pages=2, options={"allow_extra_requests": False}, cookies='cookie-file.txt'):
        post_list = post['text'].split()
        try:
            if post_list[0] in WORD_LIST:
                split = post['text'].split("\n")
                if post_list[0] == 'THIS':
                    today = datetime.date.today()
                    date = today + datetime.timedelta(days=DAY_DICT[post_list[1]] - today.weekday())
                else:
                    split = post['text'].split("\n")
                    date = dateparser.parse(split[0])
                if date >= date.today():
                    if len(split) > 1:
                        month = date.month
                        day = date.day
                        if int(date.month) < 10:
                            month = '0' + str(date.month)
                        if int(date.day) < 10:
                            day = '0' + str(date.day)
                        d[str(date.year) + "-" + str(month) + "-" + str(day)] = [split[1], page]
                    else:
                        d[date] = 'Pub'

        except:
            pass
    return d


def insert(dict):
    for date, list in dict.items():
        title = list[0]
        page = list[1]

        insert_ok = True

        # filter out non pub/club events
        if page == 'IndustriellEkonomiKTH':
            title_s = title.split(' ')
            insert_ok = False
            for word in title_s.capitalize():
                if 'PUB' in word or 'CLUB' in word:
                    insert_ok = True
                    break

        if insert_ok:
            # print(title,page)
            with connection.cursor() as cursor:
                sql = "INSERT IGNORE INTO events (`page`, `title`, `date`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (page, title, date))
            connection.commit()


connection = pymysql.connect(host='mysql115.unoeuro.com', user=USER, password=PASSWORD,
                             db=DB, cursorclass=pymysql.cursors.DictCursor)

for page_name in PAGE_LIST:
    insert(get_events(page_name))
