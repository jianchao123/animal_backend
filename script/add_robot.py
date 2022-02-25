# class AddRobotView(generics.ListCreateAPIView):
#     """增加机器人"""
#
#     @post_require_check([])
#     def post(self, request, *args, **kwargs):
#         """每次调用增加1000个机器人"""
#         phones_prefix = ["130", "131", "132", "133", "134", "135", "136",
#                          "137",
#                          "138", "139", "150", "151", "152", "153", "155",
#                          "156",
#                          "157", "158", "159", "180", "182", "185", "186",
#                          "187",
#                          "188", "189"]
#         import random
#         gameplayer = GamePlayer.objects.all().order_by('-pk').first()
#         max_pk = gameplayer.id + 1
#         phones = []
#         for x in range(1000):
#             pre = random.choice(phones_prefix)
#             t = ("%04d" % max_pk)
#             phone = pre + "0000" + t
#             nickname = pre + "******" + t[:-2]
#             phones.append([phone, nickname])
#             max_pk += 1
#         random.shuffle(phones)
#         for element in phones:
#             signup_gameplayer("kIhHAWexFy7pU8qM", element[0],
#                               invite_code=None, is_robot=True,
#                               nickname=element[1],
#                               headimg="headimg/default1.jpg")
#         return {}