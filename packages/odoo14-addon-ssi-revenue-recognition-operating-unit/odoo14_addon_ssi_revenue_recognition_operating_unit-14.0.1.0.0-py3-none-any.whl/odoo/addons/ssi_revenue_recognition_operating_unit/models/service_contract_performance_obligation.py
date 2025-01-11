# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ServiceContractPerformanceObligation(models.Model):
    _name = "service_contract.performance_obligation"
    _inherit = [
        "service_contract.performance_obligation",
        "mixin.single_operating_unit",
    ]

    operating_unit_id = fields.Many2one(
        related="contract_id.operating_unit_id",
        store=True,
        default=False,
    )
