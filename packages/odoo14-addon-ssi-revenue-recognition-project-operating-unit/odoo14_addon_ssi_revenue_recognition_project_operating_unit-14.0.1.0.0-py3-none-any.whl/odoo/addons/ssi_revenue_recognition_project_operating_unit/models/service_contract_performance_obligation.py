# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ServiceContractPerformanceObligation(models.Model):
    _name = "service_contract.performance_obligation"
    _inherit = [
        "service_contract.performance_obligation",
    ]

    def _prepare_project_data(self):
        self.ensure_one()
        _super = super(ServiceContractPerformanceObligation, self)
        result = _super._prepare_project_data()
        result.update(
            {
                "operating_unit_id": self.contract_id.operating_unit_id
                and self.contract_id.operating_unit_id.id
                or False,
            }
        )
        return result
