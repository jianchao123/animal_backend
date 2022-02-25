# coding:utf-8
import json
import unittest
from tests import common
# from gevent import monkey; monkey.patch_socket()
# import gevent


class TestAll(unittest.TestCase):

    headers_w = {
        "Content-Type": "application/json",
        "Cookie": "sessionid=47i8scnbyyi24d460rinsvh34ue1mg86; "
                  "csrftoken=GRquxsNhbNBQVrJNSXAC1WtslxdE7KDw13nCQEQqQW0vbZyE9tnpGTnfmKZiArZ7; "
                  "tabstyle=raw-tab",
        "X-CSRFTOKEN": "GRquxsNhbNBQVrJNSXAC1WtslxdE7KDw13nCQEQqQW0vbZyE9tnpGTnfmKZiArZ7"
    }


    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_signin(self):
    #     """登陆"""
    #     params = {
    #         "phone": "18508217537",
    #         "password": "asd123",
    #         #"code": "834934"
    #     }
    #     r = common.post(params, "user/app/signin/",
    #                     headers={"Content-Type": "application/json"})
    #     print r.content
    #     print r.status_code
    #     print r.cookies

    # ################### snatch_treasure #################################
    # def test_homepage(self):
    #     """主页"""
    #     params = {
    #         "page": 1,
    #         "order_type": 1
    #     }
    #     import time
    #     start = time.time()
    #     r = common.get(params, "snatchtreasure/homepage/")
    #     end = time.time()
    #     print end - start
    #     print r.content

    # def test_periodbytag(self):
    #     """根据分类查询周期"""
    #     params = {
    #         "tag_id": 1,
    #     }
    #     r = common.get(params, "snatchtreasure/periodbytag/")
    #     print r.content

    # def test_commodity_detail_page(self):
    #     """
    #     商品详情页
    #     """
    #     import time
    #     start = time.time()
    #     params = {
    #         "period_pk": 20982
    #     }
    #     r = common.get(params, "snatchtreasure/commoditydetailpage/")
    #     end = time.time()
    #     print start
    #     print end
    #     print end - start
    #     print r.content

    # def test_current_period_participate(self):
    #     """本期参与记录"""
    #     params = {
    #         "period_pk": 2659
    #     }
    #     r = common.get(params, "snatchtreasure/currentperiodparticipates/")
    #     print r.content

    # def test_previous_periods(self):
    #     """往期揭晓"""
    #     params = {
    #         "commodity_pk": 5,
    #         "last_pk": 999999999
    #     }
    #     r = common.get(params, "snatchtreasure/previousperiod/")
    #     print r.content

    # def test_new_lottery(self):
    #     """最新揭晓"""
    #     import time
    #     start = time.time()
    #     params = {
    #         "last_pk": 999999999
    #     }
    #     r = common.get(params, "snatchtreasure/newdrawlottery/")
    #     end = time.time()
    #     print(end - start)
    #     print r.content

    # def test_recentlyparticipaterecords(self):
    #     """最近参与记录"""
    #     params = {
    #         "player_pk": 258
    #     }
    #     r = common.get(params, "snatchtreasure/recentlyparticipaterecords/")
    #     print r.content

    # def test_recentlywinprizerecords(self):
    #     """最近中奖记录"""
    #     params = {
    #         "player_pk": 258
    #     }
    #     r = common.get(params, "snatchtreasure/recentlywinprizerecords/")
    #     print r.content

    # def test_order_records(self):
    #     """订单记录"""
    #     params = {
    #         "last_pk": 999999999,
    #         "status": 1
    #     }
    #     r = common.get(params, "snatchtreasure/apporderrecords/",
    #                    headers=self.headers_w)
    #     print r.content

    # def test_prize_records(self):
    #     """中奖记录"""
    #     params = {
    #         "last_pk": 999999999,
    #         "is_accept_prize": 1
    #     }
    #     r = common.get(params, "snatchtreasure/prizerecords/",
    #                    headers=self.headers_w)
    #     print r.content

    # def test_participate(self):
    #     """购买人次"""
    #     params = {
    #
    #         "period_id": 1,
    #         "amounts": 2000
    #
    #     }
    #     r = common.post(params, "snatchtreasure/participate/",
    #                     headers=self.headers_w)
    #     print r.content

    # def test_query_tokens(self):
    #     """查询夺宝号"""
    #     params = {
    #         "period_id": 7,
    #         "text": "123"
    #     }
    #     r = common.get(params, "snatchtreasure/querytokens/",
    #                    headers=self.headers3)
    #     print r.content

    ############################ shopping_usder ############################

    # def test_AcceptPrizeInfo(self):
    #     """领奖信息"""
    #     params = {
    #         "prize_record_pk": 6
    #     }
    #     r = common.get(params, "user/accept/prize/info/",
    #                    headers=self.headers3)
    #     print r.content

    # def test_send_signup_code(self):
    #     """发送注册码"""
    #     params = {
    #         "phone": "15360580821"
    #     }
    #     r = common.get(params, "user/sendsignupcode/")
    #     print r.content

    # def test_send_signin_code(self):
    #     """发送登陆码"""
    #     params = {
    #         "phone": "15360580822"
    #     }
    #     r = common.get(params, "user/sendsignincode/")
    #     print r.content

    # def test_sign_up_player(self):
    #     """注册玩家"""
    #     params = {"phone": "15360580822", "password": "woaini**7799",
    #               "code": "992275",
    #               "invite_code": "60686632"}
    #     r = common.post(params, "user/signup/player/",
    #                     headers={"Content-Type": "application/json"})
    #     print r.content

    # def test_delete_period(self):
    #     """删除周期数据"""
    #     r = common.post({'x': 23000}, "user/test/", headers=self.headers_w)
    #     print r.content

    # def test_accept_prize(self):
    #     """
    #     领奖
    #     accept_prize_type=2 兑换豆或者转到收货人
    #     accept_prize_type=3 领取相应的奖品
    #     """
    #
    #     params = {
    #         "accept_prize_type": 2,
    #         "prize_record_id": 4745,
    #         "phone": "18500000001"
    #         # "shipping_address_pk": 27
    #     }
    #     r = common.post(params, "user/accept/prize/", headers=self.headers_w)
    #     print r.content

    # def test_usercards(self):
    #     """用户卡密"""
    #     params = {
    #     }
    #     r = common.get(params, "user/usercards/",
    #                    headers=self.headers)
    #     print r.content

    # def test_area_list(self):
    #     """区域列表"""
    #     params = {
    #         "pid": 2367,
    #         "level": 2
    #     }
    #     r = common.get(params, "settings/arealist/",
    #                    headers=self.headers)
    #     print r.content

    def test_add_address(self):
        """添加地址
        |recipents_name|true|string|收货名字|
|recipents_phone|true|string|收货号码|
|province|true|int|省pk|
|city|true|int|市pk|
|area|true|int|区pk|
|recipents_address|true|string|收货地址|
|is_default|true|int|取值 1:是 0:否|
        """
        params = {
            "recipents_name": "fdsa",
            "recipents_phone": "13578945612",
            "province": 1,
            "city": 2,
            "area": 3,
            "recipents_address": "<div>XSS</div>",
            "is_default": 1
        }
        r = common.post(params, "settings/shipping/address/",
                        headers=self.headers_w)
        print r.content

    # def test_addresses(self):
    #     """收获地址"""
    #     params = {
    #     }
    #     r = common.get(params, "settings/shipping/address/",
    #                    headers=self.headers3)
    #     print r.content

    # def test_add_consigness(self):
    #     """添加收获人"""
    #     params = {
    #         "phone": "15588880001",
    #         "consignee_name": "兑换号",
    #     }
    #     r = common.post(params, "businessman/userconsignees/",
    #                     headers=self.headers3)
    #     print r.content

    # def test_update_consigness(self):
    #     """更新收货人"""
    #     params = {
    #         "phone": "13544440001",
    #         "consignee_name": "兑换号",
    #         "user_consignee_pk": 9
    #     }
    #     r = common.post(params, "businessman/updateuserconsignees/",
    #                     headers=self.headers3)
    #     print r.content

    # def test_consigness(self):
    #     """收获人"""
    #     params = {
    #     }
    #     r = common.get(params, "businessman/userconsignees/",
    #                    headers=self.headers3)
    #     print r.content

    # def test_test(self):
    #     """test"""
    #     params = {
    #     }
    #     r = common.get(params, "user/test",
    #                    headers=self.headers1)
    #     print r.content

    # def test_area(self):
    #     """省市区查询"""
    #     params = {
    #         "pid": 0,
    #         "level": 1
    #     }
    #     r = common.get(params, "settings/arealist/",
    #                    headers=self.headers3)
    #     print r.content

    # def test_qiniu(self):
    #     """七牛token"""
    #     params = {
    #         "upload_file_name": "/headimg/我的头像.png"
    #     }
    #     r = common.get(params, "user/getqiniutoken/",
    #                    headers=self.headers3)
    #     print r.content

    # def test_update_user(self):
    #     """修改用户信息"""
    #     params = {
    #         #"password": "Qadmin123456",
    #         # "nickname": "哈哈哈哈",
    #         # "sex": 2,
    #         #"headimage": "xxxxxxxx/xxxxxxx.png"
    #         "is_robot": 0
    #     }
    #     r = common.post(params, "user/update/player/",
    #                     headers=self.headers_w)
    #     print r.content

    # def test_query_user(self):
    #     """查询玩家信息"""
    #     params = {
    #        "player_pk": 37
    #     }
    #     r = common.get(params, "user/userinformation/", self.headers3)
    #     print r.content



    # def test_periodquerybypk(self):
    #     """查询周期数据"""
    #     params = {
    #         "period_pk": 34,
    #     }
    #     r = common.get(params, "snatchtreasure/periodquerybypk/")
    #     print r.content

    # def test_finish_period(self):
    #     """完成周期数据"""
    #     params = {
    #         "last_open_index": 999999999,
    #     }
    #     r = common.get(params, "snatchtreasure/finishedperiodquery/")
    #     print r.content

    # def test_popprizedialog(self):
    #     """中奖弹窗"""
    #     params = {
    #     }
    #     r = common.get(params, "snatchtreasure/popprizedialog/",
    #                    headers=self.headers2)
    #     print r.content

    # def test_periodbytag(self):
    #     """周期查询"""
    #     params = {
    #         "tag_id": 1,
    #     }
    #     r = common.get(params, "snatchtreasure/periodbytag/")
    #     print r.content

    # def test_querytag(self):
    #     """tag查询"""
    #     params = {
    #     }
    #     r = common.get(params, "snatchtreasure/commoditytag/")
    #     print r.content

    # def test_get_period_id(self):
    #     """
    #     获取周期id
    #     """
    #     params = {
    #         "commodity_id": 1
    #     }
    #     r = common.get(params, "snatchtreasure/getperiodbycommodityid/",
    #                    )
    #     print r.content

    # def test_queryperiodbyrewardtype(self):
    #     """
    #     根据开奖类型查询周期
    #     """
    #     params = {
    #         "order_type": '6',
    #         "reward_type": '3'
    #     }
    #     r = common.get(params, "snatchtreasure/queryperiodbyrewardtype/",
    #                    )
    #     print r.content

    # def test_participatebyperiod(self):
    #     """
    #     当期参与记录
    #     """
    #     params = {
    #         "period_pk": 165
    #     }
    #     r = common.get(params, "snatchtreasure/participatebyperiod/",
    #                    headers=self.headers2)
    #     print r.content

    # def test_alfnotify(self):
    #     """"""
    #     params = {
    #         "player_pk": 37,
    #         "last_pk": 999999999
    #     }
    #     r = common.post(params, "pay/alfcallback/")
    #     print r.content

    # def test_wx_deposit(self):
    #     """微信充值"""
    #     params = {
    #         "amounts": 0.01
    #     }
    #     r = common.post(params, "pay/wxscancodedepost/", headers=self.headers_w)
    #     print r.content

    # def test_pay_list(self):
    #     """支付金额列表"""
    #     params = {
    #     }
    #     r = common.get(params, "pay/getpaymoney/", headers=self.headers_w)
    #     print r.content

    # def test_conf_basic(self):
    #     """基础配置信息接口"""
    #     r = common.get({}, "settings/basicconf/")
    #     print r.content

    # def test_test(self):
    #     """测试"""
    #     # ####################### 更新以前周期的荣誉榜 ##########################
    #     # 41 - 3
    #     import time
    #     count = 45821
    #     while count > 0:
    #         print count
    #         r = common.post({"start_id": count - 200, "end_id": count},
    #                         "user/test/",
    #                         headers={"Content-Type": "application/json"})
    #         print r.content
    #         count -= 199
