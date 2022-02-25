# coding:utf-8
import json
import unittest
from tests import common


class TestAll(unittest.TestCase):
    # # admin02
    headers_admin02_test = {
        "Content-Type": "application/json",
        "Cookie": "sessionid=hv35qi3c8usd6iim3rdplq8vm0a4bmgk; "
                  "csrftoken=WwBn8u4MsR7mwYCCOB36N7Nr0VNE80zdcQfXI0GgXol2VIlluEUzk98w5egexhbV; "
                  "tabstyle=raw-tab",
        "X-CSRFTOKEN": "WwBn8u4MsR7mwYCCOB36N7Nr0VNE80zdcQfXI0GgXol2VIlluEUzk98w5egexhbV"
    }

    headers_admin02_pro = {
        "Content-Type": "application/json",
        "Cookie": "sessionid=y430htq6a3q9rsjfrdh20dis0yzxxv2q; "
                  "csrftoken=i9wYnPY970E4Y0qaMXNDsRUWbSUAxAxosyRB9GkDt8Wrld15HaagrE7OSE7AejOe; "
                  "tabstyle=raw-tab",
        "X-CSRFTOKEN": "i9wYnPY970E4Y0qaMXNDsRUWbSUAxAxosyRB9GkDt8Wrld15HaagrE7OSE7AejOe"
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
    #         "username": "admin02",
    #         "password": "cS1m&IIBJH3YrUE$"
    #     }
    #     r = common.post(params, "user/backend/signin/",
    #                     headers={"Content-Type": "application/json"})
    #     print r.content
    #     print r.headers

    # def test_card_type_list(self):
    #     """卡密种类列表"""
    #     params = {}
    #     r = common.get(params, "inventory/cardinventories/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_commmodity_list(self):
    #     """商品列表"""
    #     params = {}
    #     r = common.get(params, "snatchtreasure/commoditys/",
    #                    headers=self.headers_rb_34)
    #     print r.content

    # def test_a_add_recycle_businessman(self):
    #     """添加回收商"""
    #     params = {
    #         "recycle_phone": "15588880002",
    #         "username": "wuming002",
    #         "nickname": u"wuming002",
    #         "password": "woaini**7799",
    #         "is_recycle": 1,
    #         "is_login": 1,
    #     }
    #     r = common.post(params, "user/recyclebusinessman/", headers=self.headers)
    #     print r.content

    # def test_b_recycle_businessman_list(self):
    #     """回收商列表"""
    #     params = {
    #     }
    #     r = common.get(params, "businessman/recyclebusinessmanlist/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_c_game_player_list(self):
    #     """查询玩家"""
    #     params = {
    #         "balance_user": 0,
    #         "black_list": 1,
    #         "online_user": 0,
    #         "page": 1,
    #         "limit": 10
    #     }
    #     r = common.get(params, "user/players/", headers=self.headers_admin02)
    #     print r.content

    # def test_add_administrator(self):
    #     """添加管理员"""
    #     params = {
    #         "username": "admin02",
    #         "password": "woaini**7799",
    #         "nickname": "兼爱02"
    #     }
    #     r = common.post(params, "user/administrator/")
    #     print r.content

    # def test_signin(self):
    #     """登陆"""
    #     params = {
    #         "username": "admin02",
    #         "password": "woaini**7799"
    #     }
    #     r = common.post(params, "user/backend/signin/",
    #                     headers={"Content-Type": "application/json"})
    #     print r.content

    # def test_query_commodity_type(self):
    #     """查询商品类型"""
    #     params = {
    #         "ordering": "-type_index"
    #     }
    #     r = common.get(params, "settings/commoditytypes/")
    #     print r.content

    # def test_add_commodity_type(self):
    #     """添加商品类型"""
    #     params = {
    #         "type_name": "test7",
    #         "type_code": "CT10007",
    #         "type_index": 7,
    #         "status": 1
    #     }
    #     r = common.post(params, "settings/commoditytypes/?format=json",
    #                     headers=self.headers)
    #     print r.content
    #     print r.status_code

    # def test_add_buschannels(self):
    #     """添加购买渠道"""
    #     params = {}
    #     r = common.post(params, "settings/buychannels/?format=json",
    #                     headers=self.headers)
    #     print r.content
    #     print r.status_code

    # def test_buschannels(self):
    #     """购买渠道列表"""
    #     params = {}
    #     r = common.get(params, "settings/buychannels/",
    #                    headers=self.headers)
    #     print r.content
    #     print r.status_code

    # def test_user_consume_situation(self):
    #     """用户消费情况"""
    #     params = {
    #         "query_date": "2018-11-03",
    #         "query_number": 10
    #     }
    #     r = common.get(params, "statistics/userconsumesituation/",
    #                    headers=self.headers)
    #     print r.content

    # def test_daichong_deposit(self):
    #     """代充"""
    #     params = {
    #         "player_id": 35,
    #         "amounts": 250
    #     }
    #     r = common.post(params, "financial/recyclebusiness/",
    #                     headers=self.headers_rb_34)
    #     print r.content

    # def test_get_qiniu_token(self):
    #     """获取七牛上传token"""
    #     params = {
    #         "upload_file_name": "/headimg/xxxxxxxx.png"
    #     }
    #     r = common.get(params, "user/getqiniutoken/",
    #                     headers=self.headers_admin02)
    #     print r.content

    # def test_deposit_list(self):
    #     """充值列表"""
    #     params = {
    #         "page": 1,
    #         "limit": 2
    #     }
    #     r = common.get(params, "financial/depositlist/",
    #                     headers=self.headers_admin01)
    #     print r.content

    # def test_cardinventoryinfo(self):
    #     """卡密库存信息"""
    #     params = {
    #     }
    #     r = common.get(params, "inventory/cardinventoryinfo/",
    #                     headers=self.headers_admin01)
    #     print r.content

    # def test_pay_typs(self):
    #     """充值类型列表"""
    #     params = {
    #     }
    #     r = common.get(params, "settings/paytypes/",
    #                    headers=self.headers_admin01)
    #     print r.content

    # def test_payaccountsconfs(self):
    #     """支付帐号配置列表"""
    #     params = {
    #     }
    #     r = common.get(params, "settings/payaccountsconfs/",
    #                    headers=self.headers_admin01)
    #     print r.content

    # def test_payaccountsconfs(self):
    #     """支付帐号配置列表"""
    #     params = {
    #     }
    #     r = common.get(params, "settings/payaccountsconfs/",
    #                    headers=self.headers_admin01)
    #     print r.content

    # def test_order_list(self):
    #     """实时购买列表"""
    #     params = {
    #         "page": 1,
    #         "limit": 10
    #     }
    #     r = common.get(params, "snatchtreasure/orderlist/",
    #                    headers=self.headers_admin01)
    #     print r.content

    # def test_token(self):
    #     """实时购买列表"""
    #     params = {
    #         "recycle_phone": "15588880001",
    #         "prize_record_id": 19
    #     }
    #     r = common.post(params, "financial/virtualorderedit/",
    #                     headers=self.headers_admin01)
    #     print r.content

    # def test_user_patch_analysis(self):
    #     """用户批次分析"""
    #     params = {
    #         "page": 1,
    #         "limit": 10,
    #         "query_date": "2018-12-30",
    #         "condition": 3
    #     }
    #     r = common.get(params, "statistics/userconsumesituation/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_win_prize_order(self):
    #     """中奖订单"""
    #     params = {
    #         "page": 1,
    #         "limit": 10
    #     }
    #     r = common.get(params, "snatchtreasure/winprizeorder/",
    #                    headers=self.headers_admin02)
    #     print r.content

    def test_businessman_hp(self):
        """回收商主页"""
        params = {
        }
        r = common.get(params, "businessman/homepage/",
                       headers=self.headers_admin02_test)
        print r.content

    # def test_update_recycle_businessman(self):
    #     """编辑回收商"""
    #     params = {
    #     }
    #     r = common.get(params, "businessman/recyclebusinessmandetail/1/",
    #                    headers=self.headers_rb_32)
    #     print r.content

    # def test_(self):
    #     """回收商每日回收金额"""
    #     params = {
    #         "businessman_pk": 34
    #     }
    #     r = common.get(params, "businessman/everydayrecycleprice/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_card_list(self):
    #     """卡密列表"""
    #     params = {
    #     }
    #     r = common.get(params, "inventory/cards/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_invite_record(self):
    #     """邀请记录"""
    #     params = {
    #         "page": 1,
    #         "limit": 10
    #     }
    #     r = common.get(params, "businessman/inviterecordlist/",
    #                    headers=self.headers_admin02)
    #     print r.content
    #
    # def test_banner_update(self):
    #     """baner更新"""
    #     params = {
    #         "image_path": "http://shopping.strongbug.com//1120%20%281%29.jpg",
    #         "index": 1,
    #         "link": "http://www.baidu.com",
    #         "status": 1,
    #         "title": "11周年庆"
    #     }
    #     r = common.patch(params, "settings/banner/1/",
    #                      headers=self.headers_admin02)
    #     print r.content

    # def test_deposit_statistics(self):
    #     """充值统计"""
    #     r = common.get({}, "statistics/depositstatistics/",
    #                    headers=self.headers_admin02)
    #     print r.content

    # def test_platform_statistics(self):
    #     """平台统计test15天数据"""
    #     r = common.post({}, "statistics/teststatistics/")
    #     print r.content

    # def test_appoint_winner_list(self):
    #     """指定中奖人列表"""
    #     r = common.get({"phone": 18508217537}, "snatchtreasure/countdownandparticipating/",
    #                    headers=self.headers_admin02)
    #     print r.content
    #
    # def test_appoint_winner_post(self):
    #     """指定中奖人post
    #             player_id = int(request.data["player_id"])
    #     period_id = int(request.data["period_id"])
    #     """
    #     params = {
    #         "period_id": 26534,
    #         "phone": '18508217537'
    #     }
    #     r = common.post(params, "snatchtreasure/appointwinnerview/",
    #                     headers=self.headers_admin02)
    #     print r.content

    # def test_appoint_winner_list(self):
    #     """指定中奖人列表"""
    #     d = {"page": 1,
    #          "admin__username": "admin02"
    #          }
    #     r = common.get(d, "snatchtreasure/appointwinnerview/",
    #                    headers=self.headers_admin02)
    #     print r.content
    #     c = json.loads(r.content)
    #     print len(c["data"]["results"])

    # def test_section_record(self):
    #     """金额区间记录"""
    #     p = {
    #         'section_mix': 100000,
    #         'section_max': 500000,
    #         'present_amounts': 1000,
    #         'text': ""
    #     }
    #     r = common.post(p, "settings/sectionmoneyrecordview/", headers=self.headers_admin02)
    #     print r.content
    #
    # def test_section_record_list(self):
    #     """金额区间记录"""
    #     r = common.get({}, "settings/sectionmoneyrecordview/", headers=self.headers_admin02)
    #     print r.content

    # def test_add_robot(self):
    #     """添加机器人"""
    #     r = common.post({}, "user/addrobot/", headers=self.headers_admin02_pro)
    #     print r.content

    # def test_tttttt(self):
    #     """"""
    #     r = common.post({}, "user/test/", headers=self.headers_admin02_pro)
    #     print r.content

    # def test_user_month_data(self):
    #     """用户每月数据"""
    #     r = common.post({}, "statistics/teststatistics/")
    #     print r.content