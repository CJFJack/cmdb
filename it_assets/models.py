from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Supplier(models.Model):
    """供应商"""
    name = models.CharField(max_length=50, unique=True, help_text='供应商名字')
    address = models.CharField(max_length=50, help_text='地址')

    def __str__(self):
        return self.name

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }

    class Meta:
        db_table = 'supplier'


class Position(models.Model):
    """位置表"""
    name = models.CharField(max_length=50, unique=True, help_text='位置')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'position'

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class CompanyCode(models.Model):
    """公司代号"""
    name = models.CharField(max_length=10, help_text='公司名称')
    code = models.CharField(max_length=10, help_text='公司代号, GZCY, HNCY')
    leader = models.ForeignKey(User, help_text='公司负责人')

    class Meta:
        db_table = 'it_assets_company_code'

    def __str__(self):
        return self.name + ':' + self.code

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'leader': self.leader.username,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'leader_id': self.leader.id,
            'leader': self.leader.username,
        }


class PartModel(models.Model):
    """配件型号表
    CPU  i5-5460
    CPU  i5-2934u
    """

    ctype = models.CharField(max_length=10, help_text='类别')
    brand = models.CharField(max_length=20, null=True, blank=True, help_text='品牌', verbose_name='品牌')
    smodel = models.CharField(max_length=20, help_text='型号')
    supplier = models.ForeignKey(Supplier, blank=True, null=True, default=None, help_text='供应商')
    company = models.ForeignKey(CompanyCode, help_text='公司')

    class Meta:
        db_table = 'it_assets_part_model'
        # unique_together = (('ctype', 'smodel', 'company'))

    def __str__(self):
        return self.ctype + ':' + self.smodel


class AssetsWarehousingRegion(models.Model):
    """仓库区域，描述资产所在位置中，所放的区，如A区、B区、C区"""
    name = models.CharField(max_length=10, unique=True, verbose_name=u'区域名称')

    class Meta:
        verbose_name = '仓库区域'
        verbose_name_plural = verbose_name
        db_table = 'it_assets_warehousing_region'

    def show_all(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def __str__(self):
        return self.name


class Assets(models.Model):
    """资产表，例如主机，显示器，绘画板"""
    STATUS = (
        (0, '库存'),
        (1, '领用'),
        (2, '外借'),
        (3, '回收'),
        (4, '损毁'),
        (5, '清理'),
        (6, '变卖'),
    )

    TYPE = (
        (0, '电子设备'),
        (1, '其他电子设备'),
    )
    PURCHASE = (
        (0, '否'),
        (1, '是'),
    )
    company = models.ForeignKey(CompanyCode, null=True, blank=True, on_delete=models.PROTECT, help_text='所属公司')
    ctype = models.IntegerField(choices=TYPE, help_text='类型')
    assets_number = models.CharField(max_length=20, unique=True, help_text='资产编号')
    name = models.CharField(max_length=20, help_text='资产名称')
    mounting_part = models.ManyToManyField(PartModel, through='AssetsPartModel')
    brand = models.CharField(max_length=30, help_text='品牌')
    specification = models.CharField(max_length=50, help_text='规格')
    using_department = models.CharField(max_length=50, blank=True, null=True, help_text='使用部门')
    user = models.CharField(max_length=10, blank=True, null=True, help_text='使用人')
    status = models.IntegerField(choices=STATUS, help_text='状态')
    pos = models.ForeignKey(Position, null=True, blank=True, on_delete=models.PROTECT, help_text='位置')
    supplier = models.ForeignKey(Supplier, blank=True, null=True, on_delete=models.PROTECT, help_text='供应商')
    belongs_to_assets = models.ForeignKey('self', blank=True, null=True, default=None, help_text='所属固定资产')
    auth_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='所属员工',
                                  help_text='所属员工')
    belongs_to_new_organization = models.CharField(max_length=50, null=True, blank=True, verbose_name='所属部门',
                                                   help_text='所属部门')
    remark = models.TextField(null=True, blank=True, verbose_name='备注', help_text='备注')
    warehousing_region = models.ForeignKey(AssetsWarehousingRegion, null=True, blank=True, on_delete=models.PROTECT,
                                           verbose_name='仓库区域', help_text='仓库区域')

    class Meta:
        db_table = 'it_assets_assets'

    def __str__(self):
        return self.assets_number

    def show_all(self):
        return {
            'id': self.id,
            'ctype': self.get_ctype_display(),
            'company': self.company.name if self.company else '',
            'assets_number': self.assets_number,
            'name': self.name,
            'with_cpu': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='CPU')]),
            'board': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='主板')]),
            'with_ssd': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='固态硬盘')]),
            'with_disk': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='机械硬盘')]),
            'with_mem': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='内存')]),
            'with_graphics': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='显卡')]),
            'brand': self.brand,
            'specification': self.specification if self.specification else '',
            'user': self.user,
            'status': self.get_status_display(),
            'pos': self.pos.name,
            'supplier': self.supplier.name if self.supplier else '',
            'merge_assets': ','.join([x.assets_number for x in self.assets_set.all()]),
            'auth_user': self.auth_user.username if self.auth_user else self.user,
            'new_organization': self.belongs_to_new_organization,
            'remark': self.remark if self.remark else '',
            'warehousing_region': self.warehousing_region.name if self.warehousing_region else '',
        }

    def show_shell(self):
        return {
            'id': self.id,
            'ctype': self.get_ctype_display(),
            'company': self.company.name,
            'assets_number': self.assets_number,
            'name': self.name,
            'brand': self.brand,
            'specification': self.specification if self.specification else '',
            'using_department': self.using_department,
            'user': self.user,
            'status': self.get_status_display(),
            'pos': self.pos.name,
            'supplier': self.supplier.name if self.supplier else '',
            'new_organization': self.belongs_to_new_organization,
            'remark': self.remark if self.remark else '',
        }

    def edit_data(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier.id if self.supplier else '0',
            'supplier': self.supplier.name if self.supplier else '',
            'user': self.user,
            'using_department': self.using_department,
            'pos_id': self.pos.id,
            'pos': self.pos.name,
            'brand': self.brand,
            'specification': self.specification,
            'belongs_to_new_organization': self.belongs_to_new_organization,
            'cpu': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='CPU')]),
            'ssd': ', '.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='固态硬盘')]),
            'hdd': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='机械硬盘')]),
            'mem': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='内存')]),
            'graphics': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='显卡')]),
            'board': ','.join([str(x.brand or '')+x.smodel for x in self.mounting_part.filter(ctype='主板')]),
            'remark': self.remark,
            'is_dz_assets_type': True if 'DZ' in self.assets_number else False,
            'company_id': self.company.id if self.company else '0',
            'company': self.company.name if self.company else '选择所属公司',
            'warehousing_region_id': self.warehousing_region.id if self.warehousing_region else '0',
            'warehousing_region': self.warehousing_region.name if self.warehousing_region else '选择仓库区域',
        }

    def get_ancestor(self):
        return self.auth_user.organizationmptt_set.first().get_ancestors_except_self() \
            if self.auth_user and self.auth_user.organizationmptt_set.all() else self.using_department


class AssetsPartModel(models.Model):
    """资产和配件的关联的中间表
    """
    assets = models.ForeignKey(Assets)
    part_model = models.ForeignKey(PartModel)
    number = models.IntegerField(help_text='数量')

    class Meta:
        db_table = 'it_assets_assets_part_model'

    def __str__(self):
        return self.assets.assets_number + ':' + self.part_model.ctype + ':' + self.part_model.smodel


class PartModelStatus(models.Model):
    """配件状态表
    """
    STATUS = (
        (0, '库存'),
        (1, '领用'),
        (2, '外借'),
        (3, '回收'),
        (4, '损毁'),
        (5, '清理'),
    )
    part_model = models.ForeignKey(PartModel, help_text='配件型号')
    status = models.IntegerField(choices=STATUS, help_text='状态')
    number = models.IntegerField(help_text='数量')
    pos = models.ForeignKey(Position, help_text='位置')
    user = models.CharField(max_length=10, help_text='保管人')

    class Meta:
        db_table = 'it_assets_part_model_status'
        unique_together = (('part_model', 'status', 'pos', 'user'), )

    def show_all(self):
        return {
            'id': self.id,
            'company': self.part_model.company.name,
            'ctype': self.part_model.ctype,
            'brand': self.part_model.brand,
            'smodel': self.part_model.smodel,
            'status': self.get_status_display(),
            'number': self.number,
            'pos': self.pos.name,
            'supplier': self.part_model.supplier.name if self.part_model.supplier else '',
            'user': self.user,
        }


class LogAssets(models.Model):
    """资产变更日志"""
    EVENT = (
        (0, '入库'),
        (1, '领用'),
        (2, '外借'),
        (3, '调拨'),
        (4, '回收'),
        (5, '损毁'),
        (6, '清理'),
        (7, '位置变更'),
        (8, '部门变更'),
        (9, '主机参数变更'),
        (10, '主机配置升级'),
        (11, '公司主体变更'),
        (12, '变卖'),
        (13, '仓库区域变更'),
    )

    PURCHASE = (
        (0, '否'),
        (1, '是'),
        (2, ''),
    )

    event = models.IntegerField(choices=EVENT, help_text='事件类型')
    assets = models.ForeignKey(Assets, on_delete=models.SET_NULL, blank=True, null=True, help_text='资产')
    part_model = models.ForeignKey(PartModel, blank=True, null=True, help_text='配件')
    etime = models.DateTimeField(help_text='事件发生时间')
    log_user = models.CharField(max_length=10, help_text='操作人')
    pos = models.ForeignKey(Position, help_text='位置')
    user = models.CharField(max_length=10, help_text='保管人')
    number = models.IntegerField(default=1, help_text='数量')
    purchase = models.IntegerField(choices=PURCHASE, default=2, help_text='是否新购买')
    price = models.CharField(max_length=20, blank=True, null=True, default=None, help_text='单价')
    pre_user = models.CharField(max_length=10, default='', help_text='上一个保管人')
    ctype = models.CharField(max_length=20, null=True, blank=True, help_text='配置变更项目', verbose_name='配置变更项目')
    pre_configuration = models.CharField(max_length=50, null=True, blank=True, verbose_name='上一个配置', help_text='上一个配置')
    current_configuration = models.CharField(max_length=50, null=True, blank=True, verbose_name='当前配置', help_text='当前配置')

    class Meta:
        db_table = 'it_assets_log_assets'

    def show_all(self):
        """如果是领用的事件
        name展示的是领用的ctype，这里为了兼容一些
        不正确的数据，如果没有part_model，展示固定或者列管资产的name
        """
        if self.event == 1:
            if self.part_model:
                name = self.part_model.ctype
                smodel = self.part_model.smodel
            else:
                name = self.assets.name
                smodel = self.assets.brand + self.assets.specification
        elif self.event == 4:
            if self.assets and self.part_model:
                # 从固定资产回收主机配件
                name = self.part_model.ctype
                smodel = self.part_model.smodel
            if not self.part_model:
                name = self.assets.name
                smodel = self.assets.brand + self.assets.specification
            if not self.assets:
                name = self.part_model.ctype
                smodel = self.part_model.smodel
        else:
            if self.assets:
                name = self.assets.name
                smodel = self.assets.brand + self.assets.specification
            else:
                name = self.part_model.ctype
                smodel = self.part_model.smodel

        return {
            'id': self.id,
            'event': self.get_event_display(),
            'assets': self.assets.assets_number if self.assets else '',
            'name': name,
            'smodel': smodel,
            'number': self.number,
            'etime': self.etime.strftime('%Y-%m-%d %H:%M'),
            'log_user': self.log_user,
            'pos': self.pos.name,
            'user': self.user,
            'purchase': self.get_purchase_display(),
            'price': self.price,
            'pre_user': self.pre_user,
            'ctype': self.ctype,
            'pre_configuration': self.pre_configuration if self.pre_configuration else '无',
            'current_configuration': self.current_configuration,
            'change_remark': (str(self.ctype or '') + '： ' + str(self.pre_configuration or '无') + ' --> ' + str(self.current_configuration or '')) if self.event in (9, 10, 11, 13) else ''
        }


class AssetsTemplates(models.Model):
    """资产模板"""
    template_name = models.CharField(max_length=20, help_text='模板名称')
    name = models.CharField(max_length=20, help_text='资产名称')
    cpu = models.CharField(max_length=50, blank=True, null=True, help_text='cpu,如果有多个,用英文,(逗号分开)')
    board = models.CharField(max_length=50, blank=True, null=True, help_text='主板，同上')
    ssd = models.CharField(max_length=50, blank=True, null=True, help_text='固态硬盘，同上')
    disk = models.CharField(max_length=50, blank=True, null=True, help_text='机械硬盘，同上')
    mem = models.CharField(max_length=50, blank=True, null=True, help_text='内存，同上')
    graphics = models.CharField(max_length=50, blank=True, null=True, help_text='显卡，同上')
    brand = models.CharField(max_length=20, blank=True, null=True, help_text='品牌')
    specification = models.CharField(max_length=20, blank=True, null=True, help_text='规格')
    using_department = models.CharField(max_length=50, blank=True, null=True, help_text='使用部门')
    remark = models.TextField(null=True, blank=True, verbose_name='备注', help_text='备注')

    class Meta:
        db_table = 'it_assets_template'

    def __str__(self):
        return self.template_name

    def show_all(self):
        return {
            'id': self.id,
            'template_name': self.template_name,
            'name': self.name,
            'cpu': self.cpu,
            'board': self.board,
            'ssd': self.ssd,
            'disk': self.disk,
            'mem': self.mem,
            'graphics': self.graphics,
            'brand': self.brand,
            'specification': self.specification,
            'using_department': self.using_department,
            'remark': self.remark,
        }

    def edit_data(self):
        return {
            'id': self.id,
            'template_name': self.template_name,
            'name': self.name,
            'cpu': self.cpu,
            'board': self.board,
            'ssd': self.ssd,
            'disk': self.disk,
            'mem': self.mem,
            'graphics': self.graphics,
            'brand': self.brand,
            'specification': self.specification,
            'using_department': self.using_department,
            'remark': self.remark,
        }


class PrintNumberRecord(models.Model):
    """打印单生成编号记录表"""
    serial_id = models.IntegerField(default=0, verbose_name='生成打印但编号序列')
    number = models.CharField(max_length=50, verbose_name='生成打印但编号字符串')

    class Meta:
        verbose_name = '打印单生成编号记录表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.number


class AssetsBatchAlterRecord(models.Model):
    """批量修改资产信息记录表"""
    TYPE = (
        (1, u'修改公司主体'),
        (2, u'修改资产状态'),
        (3, u'修改所在仓库区域'),
    )
    alter_time = models.DateTimeField(auto_now_add=True, verbose_name=u'提交修改时间')
    alter_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=u'提交修改人')
    alter_type = models.IntegerField(choices=TYPE, default=1, verbose_name=u'修改类型')

    class Meta:
        verbose_name = u'批量修改资产信息记录表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'id': self.id,
            'alter_time': str(self.alter_time)[:19],
            'alter_user': self.alter_user.username,
            'alter_type': self.get_alter_type_display(),
        }

    def __str__(self):
        return self.alter_user.username + '-' + str(self.alter_time[:19] + '-' + self.get_alter_type_display())


class AssetsBatchAlterRecordDetail(models.Model):
    """批量修改资产信息结果明细表"""
    RESULT = (
        (0, u'修改失败'),
        (1, u'修改成功'),
    )
    record = models.ForeignKey(AssetsBatchAlterRecord, verbose_name=u'所属批量修改资产记录')
    assets_number = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'修改的资产编号')
    result = models.IntegerField(choices=RESULT, default=1, verbose_name=u'修改结果')
    remark = models.CharField(max_length=50, default='', verbose_name=u'备注')
    old_value = models.CharField(max_length=30, default='', verbose_name=u'修改前的值')
    new_value = models.CharField(max_length=30, default='', verbose_name=u'修改后的值')

    class Meta:
        verbose_name = u'批量修改资产信息结果明细表'
        verbose_name_plural = verbose_name

    def show_all(self):
        return {
            'assets_number': self.assets_number,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'result': self.get_result_display(),
            'remark': self.remark,
        }

    def __str__(self):
        return self.assets_number + '-' + self.get_result_display()
