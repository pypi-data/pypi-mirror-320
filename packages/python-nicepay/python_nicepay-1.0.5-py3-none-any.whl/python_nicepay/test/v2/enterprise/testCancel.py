from python_nicepay.constants.constantsGeneral import ConstantsGeneral
from python_nicepay.data.builder.v2.enterprise import builderCancel
from python_nicepay.data.builder.v2.enterprise.dataGenerator import DataGenerator
from python_nicepay.service.v2EnterpriseService import ServiceNicepay


class testCancel:
    bodyCancel = (
        builderCancel.BuildCancel()
        .setPayMethod(ConstantsGeneral.getPayMethodEWallet())
        .setTxid("IONPAYTEST05202501122104399654")
        .setReferenceNo("OrdNo20250112210438")
        .setCancelType("1")
        .setCancelMsg("Testing Cancellation - n1tr0")
        .setAmt("1")
        .build()
    )

    response = ServiceNicepay.serviceCancel(DataGenerator.getCancelBody(bodyCancel.jsonCancel()))
