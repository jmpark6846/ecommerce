from django.db import models

from .utils import get_now, generate_unique_id


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정 일시")
    deleted_at = models.DateTimeField(default=None, null=True, help_text="삭제 일시")

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = get_now()
        super(BaseModel, self).save()


class Log(models.Model):
    ref_data = models.CharField(max_length=16, help_text="참고 데이터", null=True)
    status_from = models.PositiveIntegerField(help_text="상태 변경 전", null=True)
    status_to = models.PositiveIntegerField(help_text="상태 변경 후", null=True)
    message = models.CharField(max_length=256, help_text="로그 메세지")


class StatusMixin(models.Model):
    STATUS_REFERENCE = {}
    MODEL_NAME = ""
    status = models.PositiveIntegerField(null=True, help_text="상태")

    class Meta:
        abstract = True

    def update_status(self, new_status, msg, ref_data=None):
        Log.objects.create(
            status_from=self.status,
            status_to=new_status,
            message=msg,
            ref_data=ref_data or f"{self.MODEL_NAME}.{self.id}"
        )
        self.status = new_status
        self.save()


class Product(BaseModel):
    price = models.IntegerField(default=0, help_text="가격")
    name = models.CharField(max_length=50, help_text="이름")

    def __str__(self):
        return f'{self.name}({self.price})'


class Receipt(BaseModel):
    order = models.ForeignKey('Order', null=True, on_delete=models.DO_NOTHING, help_text='주문')
    product = models.ForeignKey('Product', null=True, on_delete=models.DO_NOTHING, help_text='주문 항목')
    amount = models.IntegerField(default=0, help_text='금액')

    def __str__(self):
        return f'주문({self.order.id}) 상품({self.product.id}): {self.amount}원'


class Order(BaseModel, StatusMixin):
    STATUS_REFERENCE = {
        'created': 1,  # 주문 생성
        'shipping': 2,  # 배송 중
        'canceled': 3,  # 주문 취소
        'refund': 4,  # 주문 환불
        'complete': 5,  # 배송 완료
    }
    MODEL_NAME = "order"

    payment = models.OneToOneField('Payment', null=True, related_name='order', on_delete=models.DO_NOTHING,
                                   help_text='결제 정보')
    products = models.ManyToManyField('Product', through='Receipt', through_fields=('order', 'product'))

    def __str__(self):
        return f'{self.id}: {self.status}'


class Payment(BaseModel, StatusMixin):
    STATUS_REFERENCE = {
        "pending": 1,  # 결제 요청
        "failed": 21,  # 결제 실패
        "complete": 22,  # 결제 완료
        "refund": 3,  # 환불
    }
    MODEL_NAME = "payment"

    amount = models.IntegerField(help_text="결제 금액")
    uid = models.CharField(max_length=16, unique=True, help_text="주문 번호 (merchant_uid)")
    description = models.CharField(max_length=150, null=True, help_text="거래 상세 내용")
    paid_at = models.DateTimeField(default=None, null=True, help_text="결제 일시")

    @staticmethod
    def get_uid() -> str:
        return generate_unique_id()
