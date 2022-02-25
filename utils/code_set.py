# coding:utf-8


class GlobalErrorCode(object):
    """全局错误码"""
    PARAM_ERROR = (1, u"参数错误")
    BUSINESS_ERROR = (2, u"逻辑错误")


class SubErrorCode(object):
    """局部错误码"""
    RECYCLE_PHONE_USED_ERROR = (10001, u"收卡号已被使用")
    PWD_FORMAT_ERROR = (10002, u"密码格式错误")
    SIGNIN_CODE_VALID_ERROR = (10003, u"上次的验证码尚可使用")
    PWD_INCORRECT_ERROR = (10004, u"密码不正确")
    PHONE_NUMBER_REGISTERED = (10005, u"手机号已经注册")
    SIGNUP_INVALID_ERROR = (10006, u"无效验证码")
    INVITE_CODE_ERROR = (10007, u"邀请码错误")
    IN_BLACKLIST_ERROR = (10008, u"在黑名单中")
    USERNAME_USED_ERROR = (10009, u"用户名已被使用")
    AMOUNTS_INSUFFICIENT_ERROR = (10010, u"数量不足")
    NOT_SUFFICIENT_FUNDS_ERROR = (10011, u"存款不足")
    RECYCLE_PHONE_ERROR = (10012, u"收卡号错误")
    CARD_INVENTORIES_INSUFFICIENT_ERROR = (10013, u"卡密库存余量不足,请联系客服发放卡密")
    RECYCLE_PHONE_MISSING_ERROR = (10014, U"未找到收卡号或兑换号")
    NOT_FOUND_RECYCLE_BUSINESSMAN_ERROR = (10015, u"未找到回收商")
    RECYCLE_PHONE_ALREADY_EXIST_ERROR = (10016, u"收卡号已经存在")
    #DH_PHONE_ALREADY_EXIST_ERROR = (10017, u"兑换号已经存在")
    PHONE_NUMBER_FORMAT_ERROR = (10018, u"手机号格式错误")
    FLAG_DIFFERENT_ERROR = (10019, u"修改的号码类型和添加的不一致")
    MISSING_PHONE_ERROR = (10020, u"找不到号码")
    MSG_LIMIT_ERROR = (10021, u"超出短信验证码限制条数")
    _CARD_INVENTORIES_INSUFFICIENT_ERROR = (10022, u"卡密库存余量不足")
    NOT_ADD_CONFIGURE_ERROR = (10023, u"管理员未添加配置")
    MONEY_SECTION_ERROR = (10024, u"金额区间错误")
    BUSINESS_NUMBER_NOT_LOGIN = (10025, u"收卡兑换号不能登陆app,请更换")
    BUSINESS_NICKNAME_EXIST = (10026, U"卡商昵称已存在")
    PHONE_LIMIT_THE_LOGIN = (10028, u"号码可能被爆破,限制登陆")
    TRY_AGAIN_MINUTE = (10029, u"一分钟后重试")
    IS_BINDING = (10030, u"已经绑定")
    NOT_THE_FULL_PHONE_NUMBER = (10031, u"不是完整的手机号")
    NOT_MODIFY = (10032, u"已结束,不能指定中奖人")
    NOT_EXIST_PLAYER = (10033, u"不存在玩家")
    PLAYER_NOT_BUY = (10034, u"玩家没有购买")


class PeriodStatusCode(object):
    PARTICIPATING = (1, u"筹备中")
    PARTICIPATE_FINISH = (2, u"筹备完成")
    WATING_B_V = (3, u"等待B值中")
    COUNTDOWNING = (4, u"倒计时中")
    REWARDING = (5, u"开奖中")
    REWARDED = (6, u"已开奖")


class ConsumeStatusCode(object):
    CONSUME_SUCCESS = (1, u"消费成功")
    DELETE = (10, u"删除")


class CommodityRewardCode(object):
    MIAOKAI = (1, u"秒开")
    B_VALUE = (2, u"B值")


class PrizeStatusCode(object):
    NOT_ACCEPT_PRIZE = (1, u"未领奖")
    ACCEPT_PRIZED = (2, u"已领奖")
    CARD_INVENTORIES_INSUFFICIENT = (9, u"卡密库存不足")


class AcceptPrizeType(object):
    DHHLD = (1, u"兑换豆")
    ZDSHR = (2, u"转到收货人")
    LQJP = (3, u"领取奖品")


class CardStatusCode(object):
    VALID = (1, u"有效")
    USED = (2, u"已使用")


class WalletUnit(object):
    B = (1, u"B")
    CNY = (2, u"CNY")


class OutTradeNoPrefix(object):
    RECYCEL_BUSINESSMAN = "RBPAY"
    ALIPAY = "ALIPAY"


class BackProfitType(object):
    dc_back_profit = (1, u"代充返利")
    recycle_back_profit = (2, u"收货返利")
    ls_back_profit = (3, u"流水返利")


class BackProfitStatus(object):
    NOT_BACK = (0, u"未返利")
    BACKED = (1, u"已返利")
    BACK_FAILED = (2, u"返利失败")


class PayStatus(object):
    WAITING = (0, u"等待付款")
    SUCCESS = (1, u"充值成功")
    REFUNDED = (2, u"已退费")
    DELETE = (10, u"删除")


class BannerStatus(object):
    VALID = (1, u"启用")
    INVALID = (2, u"删除")


class ImgResourceType(object):
    COMMODITY = (1, u"Commodity")


class CardInventoryStatus(object):
    ENABLED = (1, u"启用")
    DISABLED = (2, u"禁用")
    DELETE = (3, u"删除")


class UserConsigneeFlag(object):
    RECYCLE_PHONE = (1, u"回收号")
    CONVERSION_PHONE = (2, u"兑换号")


class AgencyStatus(object):
    AUDITING = (1, u"申请中")
    SUCCESS = (2, u"充值成功")
    AUDIT_NO_PASS = (3, u"审核不通过")
    REFUNDED = (4, u"已退费")
    DELETE = (10, u"删除")


class AgencyUnits(object):
    CNY = (1, u"cny")


class PayAccountsConfStatus(object):
    NORMAL = (1, u"正常")
    UNNORMAL = (2, u"异常")
    BAN = (3, u"封停中")


class OrderStatus(object):
    IN_THE_ORDER = (1, u"下单中")
    ORDERED = (2, u"下单完成")


class SettlementStatus(object):
    SETTLED = (1, u"已结算")
    NO_SETTLED = (2, u"未结算")


class PresentStatus(object):
    FIRST_DEPOSIT = (1, u"首充赠送")
    SUMMON = (2, u"召回赠送")
    SIGNUP = (3, u"注册赠送")