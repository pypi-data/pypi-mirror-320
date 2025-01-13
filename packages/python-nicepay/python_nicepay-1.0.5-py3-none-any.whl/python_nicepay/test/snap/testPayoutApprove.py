from datetime import datetime

from python_nicepay.constants.constantsEndpoint import ConstantsEndpoints
from python_nicepay.data.builder.snap import builderPayout, builderAccessToken
from python_nicepay.service.snapService import SnapService
from python_nicepay.util.utilLogging import Log

log = Log()
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class testPayoutApprove:
    bodyCreateToken = (
        builderAccessToken.BuildAccessToken()
        .setGrantType("client_credentials")
        .setAdditionalInfo("")
        .build()
    )

    bodyPayoutApprove = (
        builderPayout.BuildPayoutApprove()
        .setOriginalPartnerReferenceNo("OrdNo20241114015744")
        .setOriginalReferenceNo("IONPAYTEST07202411140157459798")
        .setMerchantId("IONPAYTEST")
        .build()
    )

    result = SnapService.serviceTransaction(bodyCreateToken.jsonAccessToken(),
                                            bodyPayoutApprove.jsonPayoutApprove(),
                                            ConstantsEndpoints.approvePayout())
