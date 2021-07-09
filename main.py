# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows,
# actions, and settings.
import lxml
import os
import re
import requests
import shutil
from bs4 import BeautifulSoup

from constants import TITLE_DICT

title_page_url = 'https://www.expecthim.com/online-bible'


class Scripture:
    def __init__(self, index, name, first_link):
        try:
            # Create target Directory
            if os.path.isdir('./scripture/') is False:
                os.mkdir(f'./scripture')
            dir_name = f'{str(index).zfill(2)}-{name}'
            os.mkdir(f'./scripture/{dir_name}')
            print("Directory ", dir_name, " Created ")
            pre_f = open(f'./scripture/{dir_name}/{name}.md', 'w')
            pre_f.write(f'''# {name}\n\n[[{name}-01|開始閱讀 →]]\n''')
            pre_f.close()
            Chapter(dir_name, name, first_link)
        except FileExistsError:
            print("Directory ", dir_name, " already exists")


class Chapter:
    def __init__(self, dir_name, name, link):
        # get chapter
        result = re.match(r'.+com/(?P<chapter>.+)-(?P<verse>\d+).html', link)
        self.chapter = str(result['verse']).zfill(2)

        # get content
        response = requests.get(link)
        self.soup = BeautifulSoup(response.text, 'lxml')
        self.name = name
        # next chapter handle
        self.next_chapter_link = self.soup.select('.next-chapter')[0]['href']
        self.next_chapter = None
        if self.next_chapter_link:
            next_result = re.match(
                r'.+com/(?P<chapter>.+)-(?P<verse>\d+).html',
                self.next_chapter_link)
            self.next_chapter = str(next_result['verse']).zfill(2)
        # write file
        f = open(f'./scripture/{dir_name}/{name}-{self.chapter}.md', 'w')
        f.write(self.get_content())
        f.close()
        if not self.next_chapter_link:
            return
        if result['chapter'] != next_result['chapter']:
            return
        Chapter(dir_name, name, self.next_chapter_link)

    def get_content(self) -> str:
        # get title
        title = self.soup.select('.bible-title h1')[0]
        content = f'# {title.text}\n\n'
        connect_link = f'[[{self.name}]]'
        separate_line = '***\n'
        if self.next_chapter:
            connect_link += f' | [[{self.name}-{self.next_chapter}|' \
                            f'{self.name} {self.next_chapter} →]]'
        connect_link += '\n'
        content += connect_link
        content += separate_line
        content += '\n'
        for verse_obj in self.soup.select('.the-post-cont p'):
            content += self.get_verse(verse_obj)
        content += separate_line
        content += connect_link
        return content

    def get_verse(self, verse_obj):
        try:
            verse = re.match(r'(?P<key>\d+)(?P<body>.+)', verse_obj.text)
            verse_md = f'###### v{verse["key"]}\n{verse["body"]}\n\n'
        except Exception:
            print(verse_obj.text)
            return ''
        else:
            return verse_md


def handle_title_page(page):
    soup = BeautifulSoup(page, 'lxml')
    a_list = soup.select('.bible-list .bible-list-chapter a')
    f = open('./constants.py', 'w')
    title_dict = {i + 1: {
        'name': a_obj.text,
        'link': a_obj['href']
    } for i, a_obj in enumerate(a_list)}
    f.write(f''' TITLE_DICT = {title_dict}''')
    f.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # response = requests.get(title_page_url)
    # handle_title_page(response.text)
    # handle_scripture()
    for key, data in TITLE_DICT.items():
        Scripture(key, data.get('name'), data.get('link'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
