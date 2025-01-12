import os
import logging
from dotenv import load_dotenv
from zyjj_open_sdk import Client, FileObject

# 加载 .env 文件
load_dotenv()
client = Client(os.getenv('sk'))


def test_article_framework_analysis():
    res = client.text.article_framework_analysis(user="爱，是人间最美好的字眼，它象征着浪漫，象征着温馨，象征着永恒……可是生活中，爱究竟在哪里呢？我一直苦苦寻觅着……\n\n电梯的一角，一对母女迎面而来，看起来只有五六岁的小女孩站在电梯前迟迟不敢向前迈一步。这时，母亲看着女儿笑了笑，说：“宝贝，别怕，向前迈。”小女孩紧皱着眉头，寒颤颤地迈上去了。\n\n电梯上的女孩还是颤抖得厉害，仿佛一只刚经历过风浪的胆怯的小燕子。电梯很快就到了，小女孩又是不敢迈，于是母亲面带微笑，温和地说：“宝贝，抬起脚，往前走，快！”小女孩抬头看了看母亲，这时的小女孩仿佛浑身充满了神奇的力量：一跨，下来了。\n\n“真勇敢！”母女俩相视而笑。\n\n——我的心一怔，原来爱是如此平凡的鼓励！\n\n拥挤的公交车上。衣着光鲜的年轻男女们正在津津有味地谈论着，车里一片喧哗。公交车的角落坐着一位长相平凡、衣着朴素的妇女。\n\n“吱”的一声，车子停了。一个拄着拐杖，头发花白的老婆婆提着一大袋的东西步履蹒跚地走上去，年轻男女们不俏一顾地瞥了一眼又继续着他们的“热门”话题。老婆婆缓缓地伸出青筋绽出的双手吃力地抓住车上的柱子，好像布满青苔的老藤，紧紧地缠在树上。瘦弱的身躯跟着车子有节奏地晃着。\n\n“大娘，来，您坐下吧！”妇女毅然站了起来，扶着老婆婆一步一步走向座位，“谢谢！”老婆婆欣慰地笑了。\n\n——我心弦一动，原来爱也是如此平淡的关怀。如果我是坐着的，我能做到吗？我问我自己。\n\n灯光柔和的餐厅。父亲煮了香喷喷的饭菜，红的是虾，绿的是菲菜，香的是汤，辣的萝卜丝，在我面前排成一排。满屋子洋溢着幸福的味道，又累又饿的我放下书包，立刻埋头狼吞虎咽起来。一碗汤下肚，整个人暖洋洋的，我这才端起父亲已盛的饭，慢慢享受。父亲在旁边看着我，微笑着。\n\n我由得停住了正要夹菜的筷子，在父亲面前一晃，“老爸，笑啥呢？”看你吃饭的馋样，也是种享受呀！“\n\n——我的心一暖，原来爱更是如此简单的守候。\n\n好像刹那间，我懂得了爱。\n\n哪怕是一句平凡的鼓励，一份平淡的关怀，一次简单的守候，只要发自内心的真情流露，就是一份珍贵的爱。\n").execute()
    print(res.text)

def test_article_scoring():
    res = client.text.article_scoring(user="爱，是人间最美好的字眼，它象征着浪漫，象征着温馨，象征着永恒……可是生活中，爱究竟在哪里呢？我一直苦苦寻觅着……\n\n电梯的一角，一对母女迎面而来，看起来只有五六岁的小女孩站在电梯前迟迟不敢向前迈一步。这时，母亲看着女儿笑了笑，说：“宝贝，别怕，向前迈。”小女孩紧皱着眉头，寒颤颤地迈上去了。\n\n电梯上的女孩还是颤抖得厉害，仿佛一只刚经历过风浪的胆怯的小燕子。电梯很快就到了，小女孩又是不敢迈，于是母亲面带微笑，温和地说：“宝贝，抬起脚，往前走，快！”小女孩抬头看了看母亲，这时的小女孩仿佛浑身充满了神奇的力量：一跨，下来了。\n\n“真勇敢！”母女俩相视而笑。\n\n——我的心一怔，原来爱是如此平凡的鼓励！\n\n拥挤的公交车上。衣着光鲜的年轻男女们正在津津有味地谈论着，车里一片喧哗。公交车的角落坐着一位长相平凡、衣着朴素的妇女。\n\n“吱”的一声，车子停了。一个拄着拐杖，头发花白的老婆婆提着一大袋的东西步履蹒跚地走上去，年轻男女们不俏一顾地瞥了一眼又继续着他们的“热门”话题。老婆婆缓缓地伸出青筋绽出的双手吃力地抓住车上的柱子，好像布满青苔的老藤，紧紧地缠在树上。瘦弱的身躯跟着车子有节奏地晃着。\n\n“大娘，来，您坐下吧！”妇女毅然站了起来，扶着老婆婆一步一步走向座位，“谢谢！”老婆婆欣慰地笑了。\n\n——我心弦一动，原来爱也是如此平淡的关怀。如果我是坐着的，我能做到吗？我问我自己。\n\n灯光柔和的餐厅。父亲煮了香喷喷的饭菜，红的是虾，绿的是菲菜，香的是汤，辣的萝卜丝，在我面前排成一排。满屋子洋溢着幸福的味道，又累又饿的我放下书包，立刻埋头狼吞虎咽起来。一碗汤下肚，整个人暖洋洋的，我这才端起父亲已盛的饭，慢慢享受。父亲在旁边看着我，微笑着。\n\n我由得停住了正要夹菜的筷子，在父亲面前一晃，“老爸，笑啥呢？”看你吃饭的馋样，也是种享受呀！“\n\n——我的心一暖，原来爱更是如此简单的守候。\n\n好像刹那间，我懂得了爱。\n\n哪怕是一句平凡的鼓励，一份平淡的关怀，一次简单的守候，只要发自内心的真情流露，就是一份珍贵的爱。\n").execute()
    print(res.text)

def test_article_enhance():
    res = client.text.article_enhance(user="爱，是人间最美好的字眼，它象征着浪漫，象征着温馨，象征着永恒……可是生活中，爱究竟在哪里呢？我一直苦苦寻觅着……\n\n电梯的一角，一对母女迎面而来，看起来只有五六岁的小女孩站在电梯前迟迟不敢向前迈一步。这时，母亲看着女儿笑了笑，说：“宝贝，别怕，向前迈。”小女孩紧皱着眉头，寒颤颤地迈上去了。\n\n电梯上的女孩还是颤抖得厉害，仿佛一只刚经历过风浪的胆怯的小燕子。电梯很快就到了，小女孩又是不敢迈，于是母亲面带微笑，温和地说：“宝贝，抬起脚，往前走，快！”小女孩抬头看了看母亲，这时的小女孩仿佛浑身充满了神奇的力量：一跨，下来了。\n\n“真勇敢！”母女俩相视而笑。\n\n——我的心一怔，原来爱是如此平凡的鼓励！\n\n拥挤的公交车上。衣着光鲜的年轻男女们正在津津有味地谈论着，车里一片喧哗。公交车的角落坐着一位长相平凡、衣着朴素的妇女。\n\n“吱”的一声，车子停了。一个拄着拐杖，头发花白的老婆婆提着一大袋的东西步履蹒跚地走上去，年轻男女们不俏一顾地瞥了一眼又继续着他们的“热门”话题。老婆婆缓缓地伸出青筋绽出的双手吃力地抓住车上的柱子，好像布满青苔的老藤，紧紧地缠在树上。瘦弱的身躯跟着车子有节奏地晃着。\n\n“大娘，来，您坐下吧！”妇女毅然站了起来，扶着老婆婆一步一步走向座位，“谢谢！”老婆婆欣慰地笑了。\n\n——我心弦一动，原来爱也是如此平淡的关怀。如果我是坐着的，我能做到吗？我问我自己。\n\n灯光柔和的餐厅。父亲煮了香喷喷的饭菜，红的是虾，绿的是菲菜，香的是汤，辣的萝卜丝，在我面前排成一排。满屋子洋溢着幸福的味道，又累又饿的我放下书包，立刻埋头狼吞虎咽起来。一碗汤下肚，整个人暖洋洋的，我这才端起父亲已盛的饭，慢慢享受。父亲在旁边看着我，微笑着。\n\n我由得停住了正要夹菜的筷子，在父亲面前一晃，“老爸，笑啥呢？”看你吃饭的馋样，也是种享受呀！“\n\n——我的心一暖，原来爱更是如此简单的守候。\n\n好像刹那间，我懂得了爱。\n\n哪怕是一句平凡的鼓励，一份平淡的关怀，一次简单的守候，只要发自内心的真情流露，就是一份珍贵的爱。\n").execute()
    print(res.text)

def test_article_translate():
    res = client.text.article_translate(user="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.\n", language="中文").execute()
    print(res.text)

def test_article_summary():
    res = client.text.article_summary(user="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.\n").execute()
    print(res.text)

def test_article_layout():
    res = client.text.article_layout(user="在电商平台，家用灭火产品五花八门，不少网红灭火产品的宣传词十分夸张，其性能真有其广告说得那么厉害吗？据《北京晚报》报道，24日，北京市大兴区消防部门针对5款网红灭火产品开展实验。实验显示，有的灭火产品不仅没效果还助燃，有的虽具备一定的灭火效果，但存在伤及使用者的风险。\n\n水火无情，人命关天，在家里或者是其他有需要的场所，配备一些灭火器材，这绝对是一件值得肯定的事情。尤其是配备灭火器材背后所折射出的消防安全意识，更是值得大力倡导。或许正是看到了这种消防安全意识背后所蕴藏的市场需求，网络上出现了各种各样的网红灭火产品。\n\n这些网红灭火产品，一方面外形设计小巧可爱，一些灭火产品更像是一种玩具；另一方面，商家极尽宣传之能事，纷纷标榜自己的产品使用起来多么方便，灭火能力多么强大，灭火效果多么好，等等。问题是，这些网红灭火产品在实际使用过程中，效果真的有商家宣传的那么好吗？\n\n日前，北京市大兴区消防部门，对这些网络上热销的网红灭火产品进行的现场测试，结果令人大跌眼镜。有的灭火产品几乎看不到什么灭火效果；有的灭火产品不但没有灭火效果，反而带来助燃作用，导致火势更大了；还有的灭火产品，虽然能将测试用火熄灭，但其本身爆炸所产生的碎片以及盆内的可燃物却四处飞溅，这意味着周围如果有可燃物品，极有可能会引发新的火情。\n\n由此可见，对于这些网红灭火产品来说，商家的宣传是一回事，它们能够达到的灭火效果却是另外一回事。灭火产品作为一种特殊的商品，其质量、效果和公众的生命财产安全息息相关，容不得半点马虎大意。\n\n公众具备消防安全意识是好事，但是一定不要被一些网络商家轻易带了“节奏”。在选择灭火产品的时候，既不要管它是不是网红产品，也不要片面相信网络商家的一面之词，而是尽量到正规商家选择合格产品。除了多关注商家的资质、诚信状况之外，还要关注产品本身是否为符合国家相关标准和要求的合格产品，避免买到“三无”产品\n").execute()
    print(res.text)

def test_article_key_summary():
    res = client.text.article_key_summary(user="4月26日，中国海油发布消息，由我国自主设计建造的亚洲首艘圆筒型浮式生产储卸油装置（FPSO）——“海葵一号”在山东青岛完工交付，标志着我国深水油气装备自主设计建造关键技术取得重大突破。\n\n这艘圆筒型“海上油气加工厂”，由近60万个零部件组成，最大储油量达6万吨，相当于一个“超级能源碗”，最大直径约90米，主甲板面积相当于13个标准篮球场，高度接近30层楼，总重约3.7万吨，相当于3万辆小汽车的重量。\n\n“相较于常规的船型结构，圆筒型FPSO体型更小，空间更紧凑，储油效率更高，并且具有钢材用量少、稳定性好、抵御恶劣海况能力强等优点，可有效降低油田开发与运营成本。”中国海油深圳分公司深水工程建设中心总经理刘华祥介绍，“海葵一号”实现了海陆一体化智能中控系统等15项关键技术设备自主化应用，并在国内海洋平台首次采用新型天然气脱硫装置和双燃料发电机，能够充分利用油田伴生气，有效提升海上油田的绿色节能水平。\n\n“海葵一号”设计寿命30年，可连续在海上运行15年不回坞。由于生产工艺复杂，设备设施集成程度高，对设计建造技术能力提出极大挑战。项目团队攻克圆筒型浮式生产装备一体化系统设计、高精度建造集成、全流程数字化调试等系列技术难题，建造周期较国际同类型装备缩短近50%，精度控制均达到毫米级，一次质量合格率超过99.8%。\n\n作为全球深水海洋油气开发的主流生产装置，浮式生产储卸油装置是集原油生产、存储、外输等功能于一体的高端海洋工程装备。近年来，我国先后完成世界最大吨位级FPSO巴油P67和P70“姊妹船”、我国最大作业水深FPSO“海洋石油119”、首个智能化FPSO“海洋石油123”等一批深水浮式生产储卸油装置，大型深水油气装备制造能力实现全面突破。\n\n据了解，“海葵一号”每天可处理原油约5600吨，交付后将拖航至水深达324米的深海进行回接，与亚洲第一深水导管架平台“海基二号”共同服役于我国第一个深水油田——流花11-1油田，创新形成国内首次“深水导管架平台+圆筒型FPSO”开发模式，为我国深水油气田高效开发提供全新方案。\n").execute()
    print(res.text)

def test_article_rewrite():
    res = client.text.article_rewrite(user="只需一段文字指令就能生成一段逼真视频，今年初，文生视频大模型Sora在全球人工智能业内外引发广泛关注。27日，2024中关村论坛年会上首次发布我国自研的具“长时长、高一致性、高动态性”特点的文生视频大模型Vidu。\n\n记者从会上获悉，这一视频大模型由清华大学联合北京生数科技有限公司共同研发，可根据文本描述直接生成长达16秒、分辨率高达1080P的高清视频内容，不仅能模拟真实物理世界，还拥有丰富想象力。\n\n清华大学人工智能研究院副院长、生数科技首席科学家朱军说，当前国内视频大模型的生成视频时长大多为4秒左右，Vidu则可实现一次性生成16秒的视频时长。同时，视频画面能保持连贯流畅，随着镜头移动，人物和场景在时间、空间中能保持高一致性。\n\n在动态性方面，Vidu能生成复杂的动态镜头，不再局限于简单的推、拉、移等固定镜头，而是能在一段画面里实现远景、近景、中景、特写等不同镜头的切换，包括能直接生成长镜头、追焦、转场等效果。\n\n“Vidu能模拟真实物理世界，生成细节复杂且符合物理规律的场景，例如合理的光影效果、细腻的人物表情等，还能创造出具有深度和复杂性的超现实主义内容。”朱军介绍，由于采用“一步到位”的生成方式，视频片段从头到尾连续生成，没有明显的插帧现象。\n\n此外，Vidu还可生成如熊猫、龙等形象。\n\n据悉，Vidu的技术突破源于团队在机器学习和多模态大模型方面的长期积累，其核心技术架构由团队早在2022年就提出并持续开展自主研发。“作为一款通用视觉模型，我们相信，Vidu未来能支持生成更加多样化、更长时长的视频内容，探索不同的生成任务，其灵活架构也将兼容更广泛的模态，进一步拓展多模态通用能力的边界。”朱军说。\n", style="1.要保证文章采用正式的语言和格式，避免使用口语化的表达方式，注重准确、严谨的表达\n2.以客观、中立的态度陈述事实和观点，避免主观情感色彩的插入\n3.需要使用行业术语和专业名词，确保准确传达信息").execute()
    print(res.text)

def test_article_expansion():
    res = client.text.article_expansion(user="我要写个检讨，内容是我上课看小说的做法是不对的，需要改正", num="1千字").execute()
    print(res.text)

def test_xhs_title():
    res = client.text.xhs_title(user="一款香水，目标是大学生").execute()
    print(res.text)

def test_xhs_artitle():
    res = client.text.xhs_artitle(user="杭州西湖").execute()
    print(res.text)

def test_douyin_script():
    res = client.text.douyin_script(user="如何赚钱").execute()
    print(res.text)

def test_poem_generate():
    res = client.text.poem_generate(user="51周末还要加班非常累，希望可以早点下班").execute()
    print(res.text)

def test_novel_generate():
    res = client.text.novel_generate(user="我去学校的路上父亲叫住了我，然后去水果店给我买了几个橘子塞给了我").execute()
    print(res.text)

def test_movie_review_generate():
    res = client.text.movie_review_generate(user="阿甘正传").execute()
    print(res.text)

def test_joke_generate():
    res = client.text.joke_generate(user="51调休还要加班，相当于只多休了两天").execute()
    print(res.text)

def test_slogan_generate():
    res = client.text.slogan_generate(user="一款智能剪辑工具，使用人工智能技术帮助用进行视频剪辑").execute()
    print(res.text)

def test_novel_science_generate():
    res = client.text.novel_science_generate(user="2050年，人工智能已经全方位超过人类，人类完全由人工智能接管，有一天人工智能决定毁灭人类，有几个从来不用人工智能的人类意识到了这一点，他们开始踏上拯救人类之旅").execute()
    print(res.text)

def test_novel_gouxue_generate():
    res = client.text.novel_gouxue_generate(user="丈夫背着妻子半夜去网吧打游戏").execute()
    print(res.text)

def test_speech_leijun_generate():
    res = client.text.speech_leijun_generate(user="智游剪辑，一款智能剪辑小工具").execute()
    print(res.text)





