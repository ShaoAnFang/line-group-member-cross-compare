from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import json
import itertools
from pprint import pprint

class Line:

    def __init__(self):
        #需要cd到 selenium chrome瀏覽器 chromedriver與2.1.5_0.crx的地方
        os.chdir(r'C:\Users\xxx\')
        #輸入line帳號與密碼
        self.account = ''
        self.password = ''

        #需事先查好該群組html裡的chatid
        self.chatID_Dict = {'群1': '', 
                            '群2': '',
                            '群3': '',
                            '群4': ''}

        self.main_group_member_list = []
        self.group_one_member_list = []
        self.corss_group_members = []
        self.whiteMemberList = []
    
    def Check_Mobile_Captcha_Screen(self):
        Stat = 1
        while Stat == 1:
            Captcha_Ele = self.driver.find_element_by_css_selector("#login_area")
            if Captcha_Ele.is_displayed() == 0:
                Stat = 0

            time.sleep(0.1)

    def init_selenium_chrome_driver(self):

        chrome_options = Options()
        #extension_path=r'.\2.1.5_0.crx'
        #executable_path=r'.\chromedriver.exe'
        #給絕對路徑
        extension_path=r'C:\Users\xxx\2.1.5_0.crx'
        executable_path= r'C:\Users\xxx\chromedriver.exe'
        #r'C:\Users\Clark\Dropbox\WinPython\SeleniumChromeLine\chromedriver.exe'
        
        chrome_options.add_extension(extension_path)
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--mute-audio")

        #chrome瀏覽器需安裝Line的擴充功能
        self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
        self.driver.get('chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc/index.html')

        time.sleep(1)
        email_input = self.driver.find_element_by_css_selector("#line_login_email")
        email_input.send_keys(self.account)

        pwd_input = self.driver.find_element_by_css_selector("#line_login_pwd")
        pwd_input.send_keys(self.password)

        login_btn = self.driver.find_element_by_css_selector("#login_btn")
        login_btn.click()

        #判斷手機驗証碼是否通過了
        self.Check_Mobile_Captcha_Screen()
        print("驗証碼通過了哦")

        groups_btn = self.driver.find_element_by_xpath('//li[@data-type="groups_list"]')
        groups_btn.click()
        print("點擊 群組頁籤")
        time.sleep(2)

    def select_group(self,groupName,chatid):
        group_input = self.driver.find_element_by_css_selector("#select_group_search_input")
        for i in range(5):
            #要輸入群組前 先清空一下placeholder再輸入
            group_input.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)

        group_input = self.driver.find_element_by_css_selector("#select_group_search_input")
        group_input.send_keys(groupName)
        print('搜尋 {}'.format(groupName))
        time.sleep(2)
        
        self.get_group_members_list(groupName,chatid)
    # element = driver.find_element_by_id('some_id')
    # element.location_once_scrolled_into_view


    def get_group_members_list(self,groupName,chatid):
        group1_ele = self.driver.find_element_by_xpath('//li[@data-chatid="'+format(chatid)+'"]')
        group1_ele.click()
        print("選擇該群組中")
        time.sleep(2)

        #_chat_moremenu
        more_btn = self.driver.find_element_by_css_selector("#_chat_moremenu")
        more_btn.click()
        print("點擊'更多'選項")
        time.sleep(1)

        #chat_more_info
        member_btn = self.driver.find_element_by_css_selector("#chat_more_info")
        member_btn.click()
        print("讀取該群組所有成員中 請稍後")
        time.sleep(1)

        #需要點一下右邊成員列表 不然會抓不到全部人
        scroll = self.driver.find_element_by_class_name('mdRGT13Img')
        scroll.click()
        time.sleep(1)

        #定位到成員列表ul class <ul class="mdRGT13Ul">
        Positioning_ul_list = self.driver.find_element_by_class_name("mdRGT13Ul")

        group_members_list = Positioning_ul_list.find_elements_by_css_selector(".mdMN02Li")
        # <li class="mdMN02Li" data-mid="ub2117cb3b4b13fb01d16d8cf23907caf" data-pressed-class="ExTap"></div>
        #     <div class="mdRGT13Ttl">名子</div>
        # </li>
        groupInfo = []

        for member in group_members_list:
            info = {}
            info['name'] = member.find_element_by_class_name("mdRGT13Ttl").text
            info['mid'] = member.get_attribute("data-mid")
            groupInfo.append(info)
            
        print('讀取完成')
        print('{} 目前 {}人'.format(groupName,len(groupInfo)))
        print('')
        #print(group1Info)

        if chatid == 'c1f079dbbef32b39d348bd700b399c177':
            self.main_group_member_list = groupInfo
        else:
            self.group_one_member_list = groupInfo

        #return groupInfo
        with open('{}.json'.format(groupName),'w', encoding='utf-8') as file:
            file.write(json.dumps(groupInfo,ensure_ascii=False))
        #pprint(groupInfo)



    def compare_member_list(self,file1,file2):
        self.corss_group_members = []
        with open('{}.json'.format(file1), 'r', encoding ='utf-8') as file:
            list1 = json.loads(file.read())
        
        with open('{}.json'.format(file2),'r', encoding = 'utf-8') as file:
            list2 = json.loads(file.read())

        set_list1 = set(tuple(sorted(d.items())) for d in list1)
        set_list2 = set(tuple(sorted(d.items())) for d in list2)
        #兩個set取聯集,找出相同
        set_overlapping = set_list1.intersection(set_list2)
        #list_dicts_overlapping = []
        for tuple_element in set_overlapping:
            #如果要mid 和 name的dict [{'mid': '', 'name': ''},{}]
            #self.corss_group_members.append(dict((x, y) for x, y in tuple_element))

            #目前只顯示出名子
            tupleToDict = dict((x, y) for x, y in tuple_element)
            #print(tupleToDict['name'])

            #如果沒有在白名單 就append in list
            if tupleToDict['name'] not in self.whiteMemberList:
                self.corss_group_members.append(tupleToDict['name'])


        #print(type(self.corss_group_members))
        return self.corss_group_members

    def compareAllGroupsCorssMember(self,groupList):
        for group1, group2 in itertools.combinations(groupList, 2):
            #print(group1,group1)
            result = self.compare_member_list(group1, group2)
            print('比對{},{} 跨群人數:{}, 以下為跨群名單'.format(group1, group2, len(result)))
            print(result)
            print("")

    def select_groups(self,groupList):
        for group in groupList:
            self.chatID_Dict[group]
            self.select_group(group, self.chatID_Dict[group])

        print('各群組成員已讀取完成 比對中..')


if __name__ == '__main__':
    obj = Line()
    obj.init_selenium_chrome_driver()
    
    #要比對的群名
    groups = ['群1','群2','群3','群4']

    #白名單(能跨群)
    whiteMemberList = ['Oscar', '鴨']
    #obj.select_group('禁言',obj.chatid_main)
    obj.whiteMemberList = whiteMemberList
    #print(obj.whiteMemberList)

    obj.select_groups(groups)
    obj.compareAllGroupsCorssMember(groups)

    obj.driver.stop_client()
    obj.driver.close()