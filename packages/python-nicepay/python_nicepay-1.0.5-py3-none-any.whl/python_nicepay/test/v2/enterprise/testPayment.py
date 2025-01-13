from datetime import datetime

from python_nicepay.data.builder.v2.enterprise import builderPayment
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testPayment:
    bodyPayment = (
        builderPayment.BuildPayment()
        .setTimestamp(datetime.now().strftime("%Y%m%d%H%M%S"))
        .setTxid("IONPAYTEST05202501122104399654")
        .setReferenceNo("OrdNo20250112210438")
        .setCashtag("")
        .setCardNo("5123450000000008")
        .setCardExpYymm("3901")
        .setCardCvv("100")
        .setRecurringToken("")
        .setPreAuthToken("")
        .setAmt("1")
        .build()
    )

    response = ServiceNicepay.servicePayment(DataGenerator.getPaymentBody(bodyPayment.dataPayment()))
