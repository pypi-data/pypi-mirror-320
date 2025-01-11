# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

{
    "name": "Revenue Recognition + Operating Unit Integration",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "ssi_revenue_recognition",
        "ssi_service_operating_unit",
    ],
    "data": [
        "security/res_group/service_contract_performance_obligation.xml",
        "security/res_group/performance_obligation_acceptance.xml",
        "security/ir_rule/service_contract_performance_obligation.xml",
        "security/ir_rule/performance_obligation_acceptance.xml",
        "views/service_contract_performance_obligation_views.xml",
        "views/performance_obligation_acceptance_views.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
