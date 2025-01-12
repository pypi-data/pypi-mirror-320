import os
import logging
from dotenv import load_dotenv
from zyjj_open_sdk import Client, FileObject

# 加载 .env 文件
load_dotenv()
client = Client(os.getenv('sk'))


def test_bili_video_parse():
    res = client.tool.bili_video_parse(url="https://www.bilibili.com/video/BV1PJiQYUEhr", quality=116).execute()
    print(res)

def test_bili_pic_parse():
    res = client.tool.bili_pic_parse(url="https://www.bilibili.com/video/BV1PJiQYUEhr").execute()
    print(res.img_url)

def test_bili_subtitle_download():
    res = client.tool.bili_subtitle_download(url="https://www.bilibili.com/video/BV1L4znYWECG").execute()
    print(res.subtitle)

def test_bili_danmu_download():
    res = client.tool.bili_danmu_download(url="https://www.bilibili.com/video/BV1L4znYWECG", ext="xml").execute()
    print(res.danmu)

def test_bili_video_summary():
    res = client.tool.bili_video_summary(url="https://www.bilibili.com/video/BV1L4znYWECG").execute()
    print(res.text)

def test_bili_comment_cloud():
    res = client.tool.bili_comment_cloud(url="https://www.bilibili.com/video/BV1L4znYWECG").execute()
    print(res.img_url)

def test_ncm_to_mp3():
    res = client.tool.ncm_to_mp3(ncm=FileObject.from_path("test.ncm")).execute()
    print(res.mp3)

def test_music_163_parse():
    res = client.tool.music_163_parse(url="https://music.163.com/#/song?id=2003496380").execute()
    print(res.mp3)

def test_xhs_pic_download():
    res = client.tool.xhs_pic_download(url="https://www.xiaohongshu.com/explore/6642a47e000000001e0329c9?xsec_token=AB2UJgUw5K_csa1ZUnSfqD63YqMQtmMfZKoRqYBsXW2sc=&xsec_source=pc_search&source=web_explore_feed").execute()
    print(res.img_list)

def test_text_cloud_generate():
    res = client.tool.text_cloud_generate(text="给大家分享一下我的个人真实经历，与君共勉。\n我出生在一个很普通的农村家庭，有点小聪明，但是贪玩，高中三年基本都是看电子书度过，天天上课把手机放在书下面，装作看书，实际上都是在看小说，现在回想起来，想不通老师为啥重来没有发现过。\n开始决定好好学习是高三上学期，有次上课和同桌说话，被老师说你自己不学，不要影响别人学习，还说了一些很难听的话（当时我在班里大概倒数10几名的样子，同桌10几名左右。），虽然我贪玩，但是我自尊心比较强，我就不服气，然后上课开始好好听课，后面一次月考竟然考到了10几名，和同桌成绩差不多，然后就开始飘了，上课又开始看小说，下次月考又考的很差，然后难受，又开始好好听课，就这样成绩一会好一会坏，不过拿了几次进步奖，同学笑话我是不是为了拿进去奖，故意退步的。\n真正让我决定好好学习的是高三下学期开学的前一天晚上，我家庭条件不是特别好，而我当时因为中考考的很差，只能上一个学费比较贵的私立高中，高三下学期开学前一天晚上我爸还在为我筹学费（家里没有穷到付不起学费的地步，只是当前家里钱被其他地方占用了，拿不出来。），最终从亲戚那里借了点钱，然后我爸把钱交到我手里，让我明天交学费，看着我爸粗糙的手（我爸是干工地的），这一刻我决定好好学习，不然都对不起这学费。高三下学期上课就没看过手机了，由于底子太差，高考离二本线差了几分，最终上了个三本。\n高考结束，暑假期间迷上了英雄联盟。大学的时候，室友也玩，经常和室友一块包夜，第二天要么旷课在宿舍睡觉，要么在教室最后一排睡觉，导致第一学期就挂了三科，不过后面补考都过了。后面还是继续玩，大二下学期突然觉得不能这样浑浑噩噩了，还不如出去打工，给家里省点学费还能挣点钱（不知道当时为啥有这想法），然后就和父母说了一下，不上学了出去打工，当时是想退学的，还好我好朋友和我说先休学吧，以后后悔还有机会。\n在苏州找了一个工厂，干了一个星期干不下去了，身体上的劳累倒是其次，主要是看不到生活的希望，每天就像一个机器一样，后面就回去上学了，然后学习非常努力，后面还得了奖学金，毕业论文也被评上了优秀论文，也是优秀毕业生，但是毕业学校没有给学位证，只给了毕业证，因为挂科超过5门（补考过了也没用，只要挂科超过5门，就完了，我们那一届有不少没有学位证的。），这个政策最开始都不知道，没有学位证后问学校，学校才说的，也不能怨学校，算是自食其果吧。没有学位证对找工作还是有很大影响的，后面有几次面试通过大厂了，因为没有学位证而被拒。\n实习的时候，实习单位和学校是有合作的，学校知道我的事迹也知道我在实习单位表现的不错，所以就邀请我回去给学弟学妹们分享我的经历。当时分享完后，有几个学弟加我微信说，他们现在也是这个状态，我的经历让他们有了重新开始的信心。\n后面的工作之旅也是一路坎坷，不过最后的结果是好的，目前在公司里做前端负责人，收入还不错。工作之旅明年年终总结再和大家分享吧。\n和大家分享我的经历，就是想告诉大家永远不要放弃，只要坚持，就会有希望，同时也想告诉大家每个人都要为自己做过的事负责，因为贪玩我没考上好一点的大学，因为贪玩我没有学位证，但是我后面迷途知返，通过自己的努力，还是得到了一份不错的工作，一个美满的家庭。").execute()
    print(res.img_url)

def test_douyin_video_download():
    res = client.tool.douyin_video_download(url="8.92 复制打开抖音，看看【吴亚钓鱼的作品】奔袭1500公里 花1500的钓费 只钓1个小时 ... https://v.douyin.com/CeiJDLMMD/ NJV:/ 09/12 w@f.bN").execute()
    print(res.video)

def test_web_content_get():
    res = client.tool.web_content_get(url="https://juejin.cn/post/7310549035965890614").execute()
    print(res.content)

def test_animate_recognize():
    res = client.tool.animate_recognize(img=FileObject.from_path("face1.jpg")).execute_async().wait(lambda i: logging.info(f"progres: {i}"))
    print(res)





