[toc]
# APP接口

### 图片和文件前缀
 http://shopping.strongbug.com

---------------------

## 主页
###### 接口功能
> 主页

###### URL
> /snatchtreasure/homepage/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|order_type|false|int|1.推荐 2.最快 3.最新 4.低价 5.高价|

###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"headline": "",
		"commodities": [{
			"commodity_reward_type": 1,
			"commodity_images": "http://shopping.strongbug.com/qr_code/156199756023.jpg",
			"commodity_name": "逢8返  京东E卡 5000面值 ",
			"residue_renci": 2427,
			"rate": 0.6,
			"total_renci": 6000,
			"period_pk": 2448
		}],
		"banner": [{
			"title": "Iphone XsMax 指引",
			"link": "protogenesis:commodity:commodity_pk=18",
			"image_path": "http://shopping.strongbug.com/banner/1557064347317WechatIMG67.jpeg",
			"id": 3
		}],
		"recommend": [{
			"commodity_images": "http://shopping.strongbug.com/commodity/1555949901950875bdc029c02b87c.jpg,http://shopping.strongbug.com/commodity/1c306f16a7eae22a.jpg",
			"status": 1,
			"location": 1,
			"name": "小米空气净化器",
			"commodity_id": 2
		}]
	},
	"detail": ""
}
# banner 广告图
# headline 头条
# commodities 商品

# period_pk 周期主键
# commodity_reward_type 商品开奖类型,1是秒开,2是B值
# commodity_images 商品图片,逗号分割
# residue_renci 剩余人次
# rate 进度条占比
# rotal_renci 总需人次
```
-----------------

## 商品分类
###### 接口功能
> 商品分类

###### URL
> /snatchtreasure/commoditytag/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |

###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"pk": 5,
		"type_name": "零食天地",
		"type_code": "CT10005",
		"type_index": 5,
		"status": 1,
		"status_describe": "启用"
	}, {
		"pk": 4,
		"type_name": "数码科技",
		"type_code": "CT10004",
		"type_index": 4,
		"status": 1,
		"status_describe": "启用"
	}, {
		"pk": 3,
		"type_name": "黄金专区",
		"type_code": "CT10003",
		"type_index": 3,
		"status": 1,
		"status_describe": "启用"
	}, {
		"pk": 2,
		"type_name": "苹果专区",
		"type_code": "CT10002",
		"type_index": 2,
		"status": 2,
		"status_describe": "禁用"
	}, {
		"pk": 1,
		"type_name": "京东E卡",
		"type_code": "CT10001",
		"type_index": 1,
		"status": 1,
		"status_describe": "启用"
	}],
	"detail": ""
}
```
-----------------

## 根据分类查询周期
###### 接口功能
> 根据分类查询周期

###### URL
> /snatchtreasure/periodbytag/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|tag_id|true|int|tag主键

###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"commodity_images": "http://shopping.strongbug.com/qr_code/155723659173.jpg",
		"commodity_name": "京东E卡 100元面值 ",
		"rate": 0.94,
		"period_pk": 2376
	}],
	"detail": ""
}
# commodity_images 商品图片,逗号分割
```
--------------------
## 商品详情页
###### 接口功能
> 商品详情页

###### URL
> /snatchtreasure/commoditydetailpage/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|period_pk|false    |int|周期pk                         
|commodity_pk|false|int|商品pk  当需要获取参与状态中的周期时,直接传递commodity_pk


###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"notice": 7,
		"trend_map_data": {
			"x_axis_data": ["000000428", "000000429", "000000430", "000000431", "000000432", "000000433", "000000434", "000000435", "000000436", "000000437", "000000438", "000000439", "000000440", "000000441", "000000442", "000000443", "000000444", "000000445", "000000446", "000000447"],
			"trend_map_data": [{
				"period_no": "000000428",
				"residue_ren_ci": 1200
			}],
			"y_axis_data": [0, 240, 480, 720, 960, 1200],
			"period_numbers": 20,
			"each_part_data": [1, 1, 5, 3, 1],
			"section": ["1200-960", "959-720", "719-480", "479-240", "239-0"]
		},
		"my_amounts": 0,
		"honor_list_data": [{
			"player_id": 388,
			"pk": 19668,
			"player_headimage": "http://shopping.strongbug.com/headimg/1559659759961532.jpg",
			"player_nickname": "你这个大傻子",
			"participate_renci": 500
		}, {
			"player_id": 604,
			"pk": 19671,
			"player_headimage": "http://shopping.strongbug.com/headimg/1559660855060314.jpg",
			"player_nickname": "二二小二二",
			"participate_renci": 64
		}, {
			"player_id": 604,
			"pk": 19671,
			"player_headimage": "http://shopping.strongbug.com/headimg/1559660855060314.jpg",
			"player_nickname": "二二小二二",
			"participate_renci": 64
		}],
		"luck_player_data": {
			"headimage": "http://shopping.strongbug.com/headimg/1559659759961532.jpg",
			"participate_amounts": 500,
			"luck_token": "10000450",
			"reward_time": "10-31 16:11",
			"pk": 388,
			"nickname": "你这个大傻子"
		},
		"commodity_detail_data": {
			"pk": 2737,
			"period_no": "000000447",
			"commodity_id": 22,
			"commodity_name": "京东E卡 1000元面值 ",
			"target_amounts": 1200,
			"amounts_prepared": 1200,
			"rate": "1.00",
			"luck_token": "10000450",
			"luck_player_id": 388,
			"luck_player_nickname": "你这个大傻子",
			"a_value": 8032664849,
			"b_value": "00000",
			"content": "{\"honor_list\": [{\"player_id\": 388, \"pk\": 19668, \"participate_renci\": 500, \"player_nickname\": \"\\u4f60\\u8fd9\\u4e2a\\u5927\\u50bb\\u5b50\", \"player_headimage\": \"http://shopping.strongbug.com/headimg/1559659759961532.jpg\"}, {\"player_id\": 604, \"pk\": 19671, \"participate_renci\": 64, \"player_nickname\": \"\\u4e8c\\u4e8c\\u5c0f\\u4e8c\\u4e8c\", \"player_headimage\": \"http://shopping.strongbug.com/headimg/1559660855060314.jpg\"}, {\"player_id\": 604, \"pk\": 19671, \"participate_renci\": 64, \"player_nickname\": \"\\u4e8c\\u4e8c\\u5c0f\\u4e8c\\u4e8c\", \"player_headimage\": \"http://shopping.strongbug.com/headimg/1559660855060314.jpg\"}], \"playerids\": {\"388\": 500, \"604\": 64, \"1099\": 500, \"1759\": 136}, \"a_time_list\": [[\"16:10:58.855\", 161058855, \"\\u4e8c\\u4e8c\\u5c0f\\u4e8c\\u4e8c\"], [\"16:10:53.897\", 161053897, \"\\u68a6\\u60f3\\u603b\\u662f\\u8981\\u6709\\u7684\"], [\"16:10:43.848\", 161043848, \"Tel\\u4e3f\\u8001\\u8857\"], [\"16:10:33.864\", 161033864, \"\\u4f60\\u8fd9\\u4e2a\\u5927\\u50bb\\u5b50\"], [\"16:10:23.851\", 161023851, \"\\u5b98\\u65b9\\u6307\\u5b9a\\u5361\\u5546QQ\\uff1a3030543151\"], [\"16:10:18.849\", 161018849, \"DellRank\"], [\"16:10:03.852\", 161003852, \"\\u706b\\u795e\\u6613\\u98ce\"], [\"16:09:48.850\", 160948850, \"159****3257\"], [\"16:09:43.851\", 160943851, \"\\u56e0\\u5e05\\u88ab\\u62d0\\u535627\"], [\"16:09:18.881\", 160918881, \"\\u6d69\\u5357\\u593a\\u5b9d\"], [\"16:09:13.864\", 160913864, \"131****3765\"], [\"16:09:08.852\", 160908852, \"\\u5c71\\u672c\\u4e94\\u5341\\u516d\"], [\"16:08:38.854\", 160838854, \"\\u540c\\u57ce16\"], [\"16:08:33.880\", 160833880, \"\\u679c\\u6d6a\\u6d6a\"], [\"16:08:23.851\", 160823851, \"\\u5085\\u7f62\\u9716\\u85d5\\u66f0\\u6bb5\"], [\"16:08:08.852\", 160808852, \"\\u5348\\u591c\\u7ea2\\u62d6\\u978b\\u4e36\"], [\"16:08:02.837\", 160802837, \"\\u90a3\\u5e74\\u51ac\\u5b63\\u96ea\\u98de\\u821e\"], [\"16:08:02.692\", 160802692, \"\\u6d69\\u5b87\\u54e5\\u54e5449\"], [\"16:08:02.347\", 160802347, \"\\u6d41\\u4e3f\\u55b5\\u55b5\"], [\"16:07:08.847\", 160708847, \"\\u5364\\u7a00\\u996dlucifer\"], [\"16:06:43.852\", 160643852, \"\\u6211\\u6ca1\\u4f60\\u5988\\u90a3\\u4e48\\u575a\\u5f3a\"], [\"16:06:38.856\", 160638856, \"\\u8c1c\\u4e00\\u6837\\u7684\\u4eba\"], [\"16:06:28.856\", 160628856, \"\\u592a\\u9ed1\\u600e\\u4e48\\u73a9\\uff0c\\u957f\\u8fdc\\u5229\\u76ca\\u554a\"], [\"16:06:18.850\", 160618850, \"\\u5fc3\\u673a\\u5a4aCyear\"], [\"16:06:13.885\", 160613885, \"DellRank\"], [\"16:06:08.847\", 160608847, \"\\u84dd\\u8272\\u821e\\u6b65\\u8f89\\u714c\"], [\"16:06:03.868\", 160603868, \"\\u98ce\\u8d77\\u5929\\u5bd2z\"], [\"16:05:53.869\", 160553869, \"\\u5fae\\u5c18H\\u98ce\"], [\"16:05:48.887\", 160548887, \"\\u4e0d\\u6015\\u6b7b\\u7684\\u90fd\\u6765\\u4e0a\\u5427\"], [\"16:05:43.854\", 160543854, \"liangjie_8513\"], [\"16:05:38.849\", 160538849, \"Paladinyo\"], [\"16:05:28.852\", 160528852, \"\\u963f\\u51e1\\u63d0\\u7684\\u5c0f\\u561f\\u561f\"], [\"16:05:18.851\", 160518851, \"fc\\u5c0f\\u6d6a\\u6446\"], [\"16:05:13.884\", 160513884, \"Biu Biu Biu\\u4e2d\\u5956\\u5566\\u2665\"], [\"16:05:08.849\", 160508849, \"\\u8349\\u6c11\\u60f3\\u8981\\u66b4\\u5bcc\"], [\"16:04:58.852\", 160458852, \"\\u5927\\u5730\\u59c6\\u5a87\\u5ffd\\u60a0\\u4f60\"], [\"16:04:53.872\", 160453872, \"yu25918988\"], [\"16:04:43.854\", 160443854, \"\\u66b4\\u529b\\u6076\\u7075\"], [\"16:04:33.875\", 160433875, \"\\u7a7a\\u624b\\u5957\\u767d\\u72fc\"], [\"16:04:28.845\", 160428845, \"\\u8c22\\u8c22\\u4f60\\u62b1\\u6b49\"], [\"16:04:18.853\", 160418853, \"\\u541b\\u541bmr\"], [\"16:04:13.886\", 160413886, \"\\u80fd\\u4e0d\\u80fd\\u8ba9\\u6211\\u6ee1\\u8840\\u590d\\u6d3b\"], [\"16:04:08.847\", 160408847, \"\\u4f60\\u8bf4\\u4e0d\\u559c\\u6b22\"], [\"16:03:58.848\", 160358848, \"\\u6ca1\\u4e2d\\u9000\\u94b1\\u6765\\u554a\\uff01\"], [\"16:03:53.865\", 160353865, \"\\u4e0d\\u6253\\u4e0d\\u9b27\\u6c92\\u60c5\\u8abf\"], [\"16:03:48.861\", 160348861, \"\\u84dd\\u8272\\u821e\\u6b65\\u8f89\\u714c\"], [\"16:03:28.880\", 160328880, \"\\u65cb\\u5f8b\\u7684\\u6cea\\u6b87\"], [\"16:03:03.861\", 160303861, \"zlm1234529\"], [\"16:03:01.728\", 160301728, \"yu25918988\"], [\"16:03:01.539\", 160301539, \"\\u606d\\u559c\\u4f60\\u4e2d\\u5956\\u4e86\"]]}",
			"finish_time": "2019-10-31 16:10:59",
			"open_lottery_time": "2019-10-31 16:11:27",
			"status": 6,
			"create_time": "2019-10-31T16:08:13",
			"commodity_reward_type": 1,
			"commodity_images": "http://shopping.strongbug.com/qr_code/155723656433.jpg",
			"ssc_period_no": 0,
			"is_card": true,
			"show_index": 3,
			"open_index": 2693,
			"countdown_millisecond": null
			"ssc_period_no": "20190325019" # 可选
		}
	},
	"detail": ""
}
# trend_map_data 走势图数据
# honor_list_data 荣誉榜数据(按照数组顺序,依次是 土豪 吃瓜 包尾)
# luck_player_data 幸运用户数据
# commodity_detail_data 商品详情数据 

# period_numbers 实时多少期 
# each_part_data  每部分的多少期,依次对应  头部 前腰 中部 后腰 尾部

# period_no                                         # 周期号
# commodity_id                                      # 商品id
# commodity_name                                    # 商品名字
# target_amounts                                    # 总需人次
# amounts_prepared                                  # 已经购买的人次
# rate                                              # 购买的人次和总需人次占比
# luck_token                                        # 幸运token
# luck_player_id                                    # 幸运玩家id
# luck_player_nickname                              # 幸运玩家昵称
# a_value                                           # a值
# b_value                                           # b值
# content                                           # content字段为计算详情的50条时间
# finish_time                                       # 购买完成时间
# open_lottery_time                                 # 揭晓时间
# status                                            # 状态(见周期状态码)
# create_time
# commodity_reward_type                             #  开奖类型 (见开奖类型码)
# commodity_images                                  # 商品图片
# ssc_period_no                                     # 时时彩期次
# is_card                                           # 是否卡券
# show_index                                 
# open_index                                        # 开奖顺序
# countdown_millisecond                             # 倒计时字段


# notice取值
 1 : "您尚未参与,快去参与吧！"     (注:1表示未开奖未参与,需要弹出底部参与框)
 2 : "您已参与,可继续参与!"      (注:2表示未开奖已参与)
 3 : "正在开奖中,请等待！"       (注:3表示开奖中)
 4 : "很遗憾,您没有中奖!"        (注:4表示已开奖已参与未中奖)
 5 : "恭喜您中奖了!"             (注:5表示已开奖已参与已中奖)
 6 : "您尚未参与,快去参与吧！"     (注:6表示已开奖未参与,需要跳到最新一期)
 7 : "您尚未登陆,请登录后参与！"    (注:7表示未登陆, 需要先登陆获取商品详情页数据,再根据1或者6来进行跳转)
```
---------------------

## 本期参与记录
###### 接口功能
> 本期参与记录

###### URL
> /snatchtreasure/currentperiodparticipates/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|period_pk|true|int|周期pk


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"pk": 19039,
		"participate_renci": 204,
		"player_id": 646,
		"player_nickname": "老用户",
		"player_ip": "***.***.63.239",
		"player_ip_address": "海南",
		"player_headimage": "http://shopping.strongbug.com/headimg/1559660906339063.jpg",
		"period_id": 2659,
		"participate_time": "2019-10-31 14:21:04"
	}],
	"detail": ""
}

# participate_renci     参与人次
# period_id             周期id
# participate_time     参与时间
```
-----------------

## 往期揭晓 
###### 接口功能
> 往期揭晓

###### URL
> /snatchtreasure/previousperiod/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|commodity_pk|true|int|商品pk|
|last_pk|true|int|每次请求的最后一条记录pk, 进入请求页面第一次请求,该值使用999999999


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"luck_player_nickname": "偷鸡一把好手",
		"luck_player_headimage": "http://shopping.strongbug.com/headimg/1559661252846431.jpg",
		"luck_player_id": 1263,
		"luck_token": "10004930",
		"period_no": "000000011",
		"open_lottery_time": "2019-10-31 14:12:54",
		"period_pk": 2415,
		"participate_renci": null
	}],
	"detail": ""
}

# open_lottery_time 开奖时间
# participate_renci 中奖者参与人次
```
---------------------
## 最新揭晓
###### 接口功能
> 最新揭晓

###### URL
> /snatchtreasure/newdrawlottery/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|last_pk|true|int|每次请求的最后一条记录pk, 进入请求页面第一次请求,该值使用999999999|


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"commodity_reward_type": 2,
		"commodity_images": "http://shopping.strongbug.com/qr_code/155730135639.jpg,http://shopping.strongbug.com/qr_code/155730136043.jpg,http://shopping.strongbug.com/qr_code/155730136719.jpg",
		"commodity_name": "冈本避孕套SKIN安全套男用超薄TOUCH套套超薄尽享装30片情趣 计生 成人用品 原装 进口 产品 okamoto",
		"countdown_millisecond": 835775,
		"period_status": 3,
		"open_index": 9999999,
		"period_pk": 2729
	}, {
	    "luck_player_headimage": "http://img-shopping-test.xhty.site/headimg/default1.jpg", # 幸运用户的头像
		"commodity_reward_type": 1,
		"luck_player_nickname": "被窝青春de坟墓",
		"commodity_images": "http://img-shopping-test.xhty.site/qr_code/155723656433.jpg",
		"commodity_name": "京东E卡 1000元面值 ",
		"open_lottery_time": "2019-11-20 14:36:49",
		"period_status": 6,
		"open_index": 16623,
		"market_price_cny": 1000.0,     # 商品市场价值
		"period_pk": 16665,             # 周期pk
		"participate_renci": 754        # 幸运用户的参与人次
	}],
	"detail": ""
}

# commodity_reward_type 开奖类型
# countdown_millisecond 倒计时
# period_status 周期状态

```
---------------------
## 最近参与记录
###### 接口功能
> 最近参与记录

###### URL
> /snatchtreasure/recentlyparticipaterecords/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|player_pk|true|int|玩家pk|


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"luck_player_nickname": "luckting321",
		"is_win_prize": false,
		"commodity_images": "http://shopping.strongbug.com/qr_code/155713270721.jpg,http://shopping.strongbug.com/qr_code/155713271216.jpg,http://shopping.strongbug.com/qr_code/155713271994.jpg",
		"commodity_name": "戴森（Dyson）吹风机 Dyson Superonic 电吹风 进口家用 HD01 紫红色官方正品",
		"open_lottery_time": "2019-10-31T16:12:33",
		"participate_pk": 18503,
		"period_no": "000000014",
		"luck_token": "10002667",
		"participate_renci": 40
	}],
	"detail": ""
}
# is_win_prize 是否中奖
# open_lottery_time 开奖时间
# luck_token 中奖号码
# participate_renci 参与人次
```
---------------------
## 最近中奖记录
###### 接口功能
> 最近中奖记录

###### URL
> /snatchtreasure/recentlywinprizerecords/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|player_pk|true|int|玩家pk|


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"commodity_images": "http://shopping.strongbug.com/qr_code/155706609318.jpg",
		"commodity_name": "京东E卡 1000面值（杭州西施）主题卡",
		"open_lottery_time": "2019-10-31T12:36:34",
		"participate_pk": 2515,
		"period_no": "000000392",
		"luck_token": "10000864",
		"participate_renci": null
	}],
	"detail": ""
}
```
-----------------

## 订单记录
###### 接口功能
> 订单记录

###### URL
> /snatchtreasure/apporderrecords/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|last_pk|true|int|每次请求的最后一条记录pk, 进入请求页面第一次请求,该值使用999999999|
|status|false|int|状态 P:拼购中 K:开奖中 Y:已开奖|


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"luck_player_headimage": "http://shopping.strongbug.com/headimg/1559661186484429.jpg",
		"luck_player_nickname": "最后一天 玩夺宝",
		"commodity_images": "http://shopping.strongbug.com/qr_code/155723656433.jpg",
		"commodity_name": "京东E卡 1000元面值 ",
		"period_numbers": "0012729",
		"token_str": "10001132,10000951,10000837,10000855,10000259,10000279,10000875,10000586,10000792,10000405,10001007,10000155,10000879,10001146,10000177,10000301,10000555,10000158,10000744,10000217,10000615,10000688,10000128,10001166,10000564,10000838,10000297,10000776,10000545,10000566,10000599,10000630,10000150,10000716,10000671,10000533,10000041,10000800,10000002,10000684,10000541,10000656,10000699,10000471,10000123,10000211,10000337,10000989,10000152,10001153,10001040,10000892,10001005,10000912,10000102,10000732,10000793,10000975,10000655,10001199,10000955,10000483,10001071,10000968,10000309,10000520,10000354,10000280,10000333,10000761,10000737,10000638,10000644,10000165,10000101,10000617,10001067,10000448,10000108,10000525,10000023,10000210,10000674,10000487,10000865,10000979,10000691,10000788,10000552,10000794,10000247,10000933,10000971,10000484,10001109,10001070,10000321,10001179,10000353,10001107,10000274,10000151,10000468,10000576,10000717,10000473,10000946,10000264,10000490,10000802,10000476,10000201,10000518,10000851,10000982,10000648,10000649,10000614,10000910,10000764,10000352,10000479,10000067,10000481,10000991,10000585,10000517,10000378,10000250,10000110,10000591,10001148,10000690,10000934,10000025,10000503,10000749,10000107,10000261,10000432,10000109,10000799,10000523,10000826,10001019,10000909,10000731,10000496,10000735,10000395,10000340,10000393,10000235,10000012,10001164,10000270,10000540,10000675,10000854,10001158,10000587,10000206,10000055,10001130,10000218,10000757,10000660,10001185,10000370,10001018,10001162,10000631,10000419,10000447,10000507,10000745,10000369,10000049,10000216,10000964,10000298,10000154,10001006,10000288,10000050,10001017,10000372,10000010,10000278,10000293,10000243,10000557,10000635,10000001,10001064,10000543,10000514,10000136,10000601,10000485",
		"luck_player_id": 1168,                 # 幸运用户id
		"luck_token": "10000096",               # 夺宝号
		"reward_time": "2019-10-31 16:55:03",   # 开奖时间
		"rate": 100.0,                          # 进度
		"period_id": 2766,                      # 周期id
		"commodity_id": 22,                     # 商品id
		"is_win_prize": false,          # 是否中奖
		"period_no": "000000452",       # 周期号
		"order_pk": 19739,              # 订单pk
		"participate_renci": 200        # 我的购买人次
		"luck_player_participate_renci": 2000 # 幸运用户的购买人次
	}],
	"detail": ""
}
```
-----------------

## 中奖记录
###### 接口功能
> 中奖记录

###### URL
> /snatchtreasure/prizerecords/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|last_pk|true|int|每次请求的最后一条记录pk, 进入请求页面第一次请求,该值使用999999999|
|is_accept_prize|false|int|是否领奖 2:是  1:否|


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"is_accept_prize": false,
		"commodity_images": "http://shopping.strongbug.com/qr_code/15570657901.jpg",
		"commodity_name": "京东E卡 200面值 爱德华《呐喊》艺术版珍藏卡",
		"luck_token": "10000155",
		"reward_time": "10-31 17:13",
		"period_id": 2784,
		"commodity_id": 36,
		"prize_record_pk": 2739,
		"period_no": "000000047",
		"participate_renci": 240
	}, {
		"is_accept_prize": false,
		"commodity_images": "http://shopping.strongbug.com/qr_code/155730135639.jpg,http://shopping.strongbug.com/qr_code/155730136043.jpg,http://shopping.strongbug.com/qr_code/155730136719.jpg",
		"commodity_name": "冈本避孕套SKIN安全套男用超薄TOUCH套套超薄尽享装30片情趣 计生 成人用品 原装 进口 产品 okamoto",
		"luck_token": "10000043",
		"reward_time": "10-31 17:12",
		"period_id": 2774,
		"commodity_id": 61,
		"prize_record_pk": 2738,
		"period_no": "000000049",
		"participate_renci": 72
	}],
	"detail": ""
}
# is_accept_prize 是否领奖 true是 false否
```
-----------------

## 购买人次
###### 接口功能
> 购买人次

###### URL
> /snatchtreasure/participate/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|period_id|true|int|周期id|
|amounts|true|int|购买多少人次|


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 查询夺宝号
###### 接口功能
> 查询夺宝号

###### URL
> /snatchtreasure/querytokens/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|period_id|true|int|周期Id|
|text|false|string|搜索文本

###### 返回数据
``` python
{"code":0,"data":["10001123","10000123"],"detail":""}
```
-----------------

## 消费一个中奖弹出框 
###### 接口功能
> 消费一个中奖弹出框 (需要登陆)

###### URL
> /snatchtreasure/popprizedialog/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |

###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"commodity_name": "京东卡1000面值",
		"period_no": "1225016",
		"prize_record_pk": 1
	},
	"detail": ""
}
```


----------------------------------------------

## 获取一个头条 (10s请求一次接口)
###### 接口功能
> 获取一个头条 

###### URL
> /snatchtreasure/headline/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |

###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"headline": "恭喜林动中奖,iphone XS MAX 金色"
	},
	"detail": ""
}
```

----------------------------------------------


-----------------

## 玩家查询
###### 接口功能
> 玩家查询

###### URL
> /user/userinformation/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|player_pk|false|int|玩家Pk,不填则默认查询当前登陆用户|


###### 返回数据
``` python
{
	"code": 0,
	"data":  {
        "pk": 1,
        "nickname": "xxxx",
        "uid": 100011,
        "phone": "135******34",
        "headimage": "/xxxx/xxx.png"
     },
	"detail": ""
}
```
-----------------

## 用户卡密
###### 接口功能
> 用户卡密

###### URL
> /user/usercards/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|||||


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"commodity_name": "京东卡1000面值",
		"commodity_image": "",
		"card_number": "02357744613775425737674266663638",      # 卡号
		"card_pwd": "7e1ab59IU9T97AFc"                          # 卡密
		"open_lottery_time": "2018-12-11 00:00:00"                    # 揭晓时间
	}],
	"detail": ""
}
```
-----------------

## 省市区查询
###### 接口功能
> 省市区查询

###### URL
> /settings/arealist/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----|
|pid|false|int|父id|
|level|true|int|等级 1:省  2:市  3:区县


###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"count": 21,
		"next": null,
		"previous": null,
		"results": [{
			"pk": 2368,
			"pid": 2367,
			"shortname": "成都",                  
			"name": "成都市",                      # 页面显示此字段
			"merger_name": "中国,四川省,成都市",
			"level": 2,                             
			"pinyin": "chengdu",
			"code": "028",
			"zip_code": "610015",
			"first": "C",
			"lng": "104.0657",
			"lat": "30.65946"
		}]
	},
	"detail": ""
}
```
-----------------

## 添加收货地址
###### 接口功能
> 添加收货地址

###### URL
> /settings/shipping/address/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|recipents_name|true|string|收货名字|
|recipents_phone|true|string|收货号码|
|province|true|int|省pk|
|city|true|int|市pk|
|area|true|int|区pk|
|recipents_address|true|string|收货地址|
|is_default|true|int|取值 1:是 0:否|


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 收货地址列表
###### 接口功能
> 收货地址列表

###### URL
> /settings/shipping/address/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |


###### 返回数据
``` python
{
    "code": 0,
    "data": {
        "pk": 1,
        "player_id": 37,                            # 玩家pk
        "recipents_name": "林地",                    # 收货名字
        "province": 1,                              # 省pk
        "province_name": "北京",                    # 省名字
        "city_name": "北京市",                            # 市名字
        "area_name": "东城区",                         # 区名字
        "city": 2,                                  # 市pk
        "area": 3,                                  # 区pk
        "recipents_phone": "15360580822",           # 收货手机号
        "recipents_address": "北京市朝阳区朝阳大道T3 1210",   # 详细地址
        "is_default": true                          # 是否默认地址
    },
    "detail": ""
}
```
-----------------
## 收货地址更新
###### 接口功能
> 收货地址更新

###### URL
> /settings/shipping/address/1/

###### 支持格式
> JSON

###### HTTP请求方式
> PATCH

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|recipents_name|true|string|收货名字|
|recipents_phone|true|string|收货号码|
|province|true|int|省pk|
|city|true|int|市pk|
|area|true|int|区pk|
|recipents_address|true|string|收货地址|
|is_default|true|int|取值 1:是 0:否|

###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 添加收货人
###### 接口功能
> 添加收货人

###### URL
> /businessman/userconsignees/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|收货手机号|
|consignee_name|true|string|收货人|
|user_consignee_pk|false|string|主键,出现这个pk代表是更新|


###### 返回数据
``` python
{
    "code":0,
    "data":[],
    "detail":""
 }
```
-----------------

## 更新收货人
###### 接口功能
> 更新收货人

###### URL
> /businessman/updateuserconsignees/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|收货手机号|
|consignee_name|true|string|收货人|
|user_consignee_pk|false|string|主键|


###### 返回数据
``` python
{
    "code":0,
    "data":[],
    "detail":""
 }
```
----------------

## 收货人列表
###### 接口功能
> 收货人列表

###### URL
> /businessman/userconsignees/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |


###### 返回数据
``` python
{
	"code": 0,
	"data": [{
		"pk": 2,
		"player_id": 20,                        # 玩家id
		"recycle_businessman_id": 18,           # 是回收商id
		"recycle_businessman_nickname": "言情"   # 回收商昵称
	}],
	"detail": ""
}
```
-----------------

## 领奖
###### 接口功能
> 领奖

###### URL
> /user/accept/prize/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|accept_prize_type|true|int|领取方式 1.兑换豆 2:转到收货人  3:领取相应奖品  |
|prize_record_pk|true|int|获奖记录pk|
|phone|false|string|回收商号码|
|shipping_address_pk|false|string|配送地址pk|

###### 返回数据
``` python
# 正常情况
{
    "code":0,
    "data":{},
    "detail":""
}

# 如果是领取卡密,返回:
{
    "code":0,
    "data":{"code":"1","notice": "卡券号12138932714923,请进入卡号卡密查看"},
    "detail":""
}

# 如果是领取卡密,在卡密库存不足的情况下,返回数据:
{
    "code":0,
    "data":{"code":"2","notice": "卡密库存余量不足,请联系客服发放卡密"},
    "detail":""
}
```
-----------------

## 查看领奖信息
###### 接口功能
> 查看领奖信息

###### URL
> /user/accept/prize/info/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|prize_record_pk|true|int|领奖记录pk|


###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"is_card": true,                                        # 是否卡密
		"is_accept_prize": true,                                # 是否领奖
		"commodity_name": "馋小贝 休闲零食大礼包礼盒一整箱进口食品零食小吃好吃的送女友女生团购礼盒1500g",
		"luck_token": "10000081",                               # 幸运token
		"commodity_image": [{
			"pk": 6,
			"image_path": "commodity/QQ图片20181024210639.png",
			"resource_type": 1,
			"relation_pk": 6,
			"info": null
		}],
		"time": "2018-10-27 13:23:38",                          # 揭晓时间
		"participate_amounts": 3                                  # 参与人次
		"period_no": "1021001",                                 # 周期号
		"accept_prize_type": 1,                                 # 领奖方式 (1.兑换牛逼豆  2.转到回收商 3.领取相应奖品([实物 | 卡密])) 
		
		# 可选数据2 (领奖方式=2)
		"to_recycle_phone": 143588880002,                        # 转到的回收商号码
		"amounts": 1000,                                         # 数量
		
		# 可选数据3.1 (领奖方式=3)
		"express_company": null,                                # 快递公司
		"express_number": null,                                 # 快递单号
		"recipents_name": "xxx",                                # 收件人名字
		"recipents_address": "xxx省xxx市xxx县xx栋2010",          # 收件地址
		"recipents_phone": "13590901010",                       # 收件号码
		
		# 可选数据3.2 (领奖方式=3)
		"card_number": "xxxx12312331321",                       # 卡券号
	},
	"detail": ""
}

# ############ 进入领奖台的逻辑 #############################
# 1.查询接口,获取数据
# 2.先根据is_accept_prize判断是否领奖,如果已经领奖则显示领奖信息,如果没有领奖则显示领奖方式下拉列表
#       (1)如果已经领奖,则根据领奖方式来显示数据. 如果领奖方式=3,则判断is_card是否为true,为true显示数据3.2,为false显示数据3.1 (特别说明:用户领取卡密,可能卡密不足.在展示卡密的时候需要判断is_insufficient, 如果为true显示文本"卡密不足,请联系客服".为false显示卡券号)
#       (2)如果没有领奖,则显示领奖方式,用户选择领取相应奖品的时候判断is_card,为true则提交领奖请求,(请求可能返回"卡密不足", 也可能返回"卡券号").为false则让用户去选择收货地址,然后提交请求. 其他领奖方式不做说明

```

-----------------
## 获取七牛上传Token
###### 接口功能
> 获取七牛上传Token

###### URL
> /user/getqiniutoken/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|upload_file_name|true|string|上传的文件名，例如:/headimg/我的头像.png|


###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"upload_token": "tA7N_dheubA81ew5GIRtuDBsj7pIn2lH3ym427QC:Cv2lfxMHx6Ar_7WM-mpqxbJ8HtM=:eyJzY29wZSI6InNob3BwaW5nOi9oZWFkaW1nL3h4eHh4eHh4LnBuZyIsImRlYWRsaW5lIjoxNTQyNzkzMDg4fQ==",
		"expire": 3600
	},
	"detail": ""
}
```
-----------------

## 发送注册code
###### 接口功能
> 发送注册code

###### URL
> /user/sendsignupcode/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|手机号|


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```

-----------------

## 注册
###### 接口功能
> 注册

###### URL
> user/signup/player/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|手机号|
|password|true|string|密码
|code|true|string|验证码
|invite_code|false|string|邀请码


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 发送登陆code
###### 接口功能
> 发送登陆code

###### URL
> /user/sendsignincode/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|手机号|


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 登陆
###### 接口功能
> 登陆

###### URL
> /user/app/signin/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|phone|true|string|手机号|
|password|false|string|密码|
|code|false|string|code|

###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 修改用户信息
###### 接口功能
> 修改用户信息

###### URL
> /user/update/player/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|nickname|false|string|昵称|
|password|false|string|密码|
|sex|false|int|性别 1:男 2:女
|headimage|false|string|头像

###### 返回数据
``` python
# 成功
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 登出
###### 接口功能
> 登出

###### URL
> /user/signout/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
| | | | |


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```
-----------------

## 获取支付需要的数据
###### 接口功能
> 获取支付需要的数据

###### URL
> /pay/wxscancodedepost/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |
|amounts|true|float|充值金额

###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"pay_memberid": "10056",
		"pay_amount": 0.01,
		"pay_notifyurl": "http://www.shalilai.cn/pay/alfnotify/",
		"pay_orderid": "WXALF201901072033430007",
		"pay_md5sign": "F39BFCD21BBEC9C9875DE6BA3BF7D099",
		"pay_callbackurl": "http://www.shalilai.cn/pay/alfcallback/",
		"pay_productname": "藤椒牛肉面2两",
		"pay_bankcode": "48",
		"pay_applydate": "2019-01-07 20:33:43"
	},
	"detail": ""
}
```

-----------------

## 支付金额列表
###### 接口功能
> 支付金额列表

###### URL
> /pay/getpaymoney/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |

###### 返回数据
``` python
{"code":0,"data":["10","20","30","50","100"],"detail":""}
```

-----------------

## 基础配置接口
###### 接口功能
> 基础配置接口

###### URL
> /settings/basicconf/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----                               |

###### 返回数据
``` python
{
	"code": 0,
	"data": {
		"domain": "http://www.strongbug.com",
		"pay_page_url": "http://www.ncxcg.cn/Pay_Index.html",
		"is_show_deposit": 0        # 是否显示充值功能 1：是 0：否
	},
	"detail": ""
}
```

-----------------

## 晒单
###### 接口功能
> 晒单

###### URL
> /activitys/suntheorders/

###### 支持格式
> JSON

###### HTTP请求方式
> POST

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----|
|commodity_name|true|string|商品名字
|img_url|true|string|商品图片
|period_no|true|string|周期号
|reward_time|true|string|揭晓时间
|luck_player_name|true|string|幸运玩家名字
|luck_player_headimg|true|string|幸运玩家头像
|luck_player|true|int|幸运玩家pk
|period|true|int|周期pk
|text|true|string|晒单提交的文本
|upload_img|true|string|晒单提交的图片,逗号分割多张图片

###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```

-----------------

## 晒单列表
###### 接口功能
> 晒单列表

###### URL
> /activitys/suntheorders/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----|


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```

-----------------

## 点赞
###### 接口功能
> 点赞

###### URL
> /activitys/praise/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----|
|sun_the_order_pk|true|int|晒单pk
|praise_player_pk|true|int|点赞用户pk


###### 返回数据
``` python
{
	"code": 0,
	"data": {},
	"detail": ""
}
```

-----------------

## 获取机器人帐号密码
###### 接口功能
> 获取机器人帐号密码

###### URL
> /get_robot_account_pwd/

###### 支持格式
> JSON

###### HTTP请求方式
> GET

###### 请求参数
> |参数|必选|类型|说明|
|:-----  |:-------|:-----|-----|
|random_number|true|int|请各位手动晾单人员填写密令



###### 返回数据
``` python
{
	"code": 0,
	"data": {"username": player.phone, "password": "kIhHAy7pU8qM"},
	"detail": ""
}
```