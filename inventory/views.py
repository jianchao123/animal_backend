# coding:utf-8
import re, os, xlrd, time
import datetime as datetime_m
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Q, Sum
from rest_framework import generics
from shopping_user.permissions import IsAdministratorPermission
from utils.AppError import AppError
from utils import code_set
from utils import framework
from paginations import LargeResultsSetPagination
from models import CardInventories, CardDeliveryRecord, Card, CardEntryRecord
from serializers import CardDeliveryRecordSerializer, \
    CardEntryRecordSerializer, CardInventoriesSerializer, CardSerializer
from rest_framework import filters
import django_filters
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from shopping_user.models import Administrator


class CardInventoriesList(generics.ListCreateAPIView):
    """卡密种类列表"""

    queryset = CardInventories.objects.all()
    serializer_class = CardInventoriesSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class CardInventoriesDetail(generics.UpdateAPIView):
    """卡密种类详情"""
    queryset = CardInventories.objects.all()
    serializer_class = CardInventoriesSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data


class CardDeliveryRecordList(generics.ListCreateAPIView):
    """卡密发货记录列表"""

    queryset = CardDeliveryRecord.objects.all()
    serializer_class = CardDeliveryRecordSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class CardFilter(django_filters.FilterSet):
    batch_no = django_filters.CharFilter(name="batch_no", lookup_expr="iexact")
    card_inventory_pk = django_filters.NumberFilter(name="card_inventory_id")

    class Meta:
        model = Card
        fields = []


class CardList(generics.ListAPIView):
    """卡密表"""

    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = (IsAdministratorPermission,)
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,)
    filter_class = CardFilter
    pagination_class = LargeResultsSetPagination

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class CardEntryRecordList(generics.ListAPIView):
    """卡密入库记录"""

    queryset = CardEntryRecord.objects.all()
    serializer_class = CardEntryRecordSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data


class CardEntryRecordDetail(generics.RetrieveAPIView):
    """卡密入库详情"""
    queryset = CardEntryRecord.objects.all()
    serializer_class = CardEntryRecordSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data


class CardInventory(generics.ListAPIView):
    """卡密库存"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        today = datetime_m.date.today()
        t_year = today.year
        t_month = today.month
        t_day = today.day

        end_date = today - timedelta(days=5)

        card_inventories = CardInventories.objects.filter(
            Q(status=code_set.CardInventoryStatus.ENABLED[0]))
        data = []

        for row in card_inventories:
            cur_date = today
            d = defaultdict()
            d["pk"] = row.pk
            d["name"] = row.name
            d["warning_volumes"] = row.warning_volumes
            volumes = \
                CardEntryRecord.objects.filter(
                    Q(card_inventory=row) & Q(entry_time__year=t_year) &
                    Q(entry_time__month=t_month) &
                    Q(entry_time__day=t_day)).aggregate(
                    Sum('volumes')).values()[0]
            d["today_warehousing_volumes"] = volumes if volumes else 0

            # 查询前五日提卡量
            cards_list = []
            while cur_date:
                result = CardDeliveryRecord.objects.filter(
                    Q(delivery_time__year=cur_date.year) &
                    Q(delivery_time__month=cur_date.month) &
                    Q(delivery_time__day=cur_date.day) &
                    Q(card_inventory=row)).aggregate(
                    Sum('volumes')).values()[0]
                result = result if result else 0
                cards_list.append((cur_date.strftime("%Y-%m-%d"), result))
                cur_date = cur_date - timedelta(days=1)
                if cur_date == end_date:
                    cur_date = None
            cards_list.reverse()
            d["ti_ka_volumes"] = cards_list
            d["cur_residue"] = row.volumes
            data.append(d)
        return data


class ImportCard(generics.CreateAPIView):
    """导入卡密"""

    permission_classes = (IsAdministratorPermission,)

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        file_obj = request.FILES.get('file')
        card_inventory_pk = request.data.get("card_inventory_pk")

        try:
            card_inventory = CardInventories.objects.get(pk=card_inventory_pk)
            admin = Administrator.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 将文件写入本地
        file_path = os.path.join(settings.TMP_PATH, file_obj.name)
        f = open(file_path, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        # 休眠1s等待IO完成
        time.sleep(1)

        # 读取文件并保存记录
        excel_file = xlrd.open_workbook(file_path)
        incr = 0
        batch_no = str(int(time.time()))
        cur_time = datetime.now()
        for sheet in excel_file.sheets():
            # 打印sheet的名称，行数，列数
            if re.match("[\u4E00-\u9FA5]+", sheet.row_values(2)[0]):
                incr = 1
            volumes = sheet.nrows - incr

            # 入库记录
            card_entry_record = CardEntryRecord()
            card_entry_record.batch_no = batch_no
            card_entry_record.card_inventory = card_inventory
            card_entry_record.volumes = volumes
            card_entry_record.entry_time = cur_time
            card_entry_record.entry_admin = admin
            card_entry_record.save()

            for inx in range(sheet.nrows - incr):
                row = sheet.row_values(inx + incr)
                card = Card()
                card.card_entry_no = card_entry_record
                card.card_inventory = card_inventory
                card.card_number = row[0]
                card.card_pwd = row[1]
                card.batch_no = batch_no
                card.status = code_set.CardStatusCode.VALID[0]
                card.save()
        # 删除文件
        os.remove(file_path)
        card_inventory.volumes += volumes
        card_inventory.save()
        return {}
