# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PerformanceObligationAcceptance(models.Model):
    _name = "performance_obligation_acceptance"
    _inherit = [
        "performance_obligation_acceptance",
        "mixin.single_operating_unit",
    ]

    operating_unit_id = fields.Many2one(
        related="contract_id.operating_unit_id",
        store=True,
        default=False,
    )
