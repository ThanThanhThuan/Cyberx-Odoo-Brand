# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    def _default_brand_id(self):
        return self.env["cyberaxial.brand"].get_or_create_default_for_company(self.env.company)



    brand_id = fields.Many2one(
        "cyberaxial.brand",
        string="Brand",
        domain="[('company_id', '=', company_id)]",
        default=_default_brand_id,
        help="Brand to use for PDF layout (header/footer).",
    )
