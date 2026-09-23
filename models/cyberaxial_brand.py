# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class CyberaxialBrand(models.Model):
    _name = "cyberaxial.brand"
    _description = "Cyberaxial Brand (PDF Report Branding)"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)

    logo_large = fields.Binary(string="Large Logo")
    logo_small = fields.Binary(string="Small Logo")
    footer_logo = fields.Binary(string="Footer Logo")

    tagline = fields.Char(string="Tagline", translate=True)
    header_html = fields.Html(string="Header Details", translate=True, sanitize=True)
    footer_html = fields.Html(string="Footer Details", translate=True, sanitize=True)

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_company_uniq", "unique(name, company_id)", "Brand name must be unique per company."),
    ]

    @api.model
    def get_or_create_default_for_company(self, company=None):
        company = company or self.env.company
        brand = self.search([("company_id", "=", company.id)], limit=1)
        if brand:
            return brand

        partner = company.partner_id
        addr_lines = []
        if partner:
            if partner.street:
                addr_lines.append(partner.street)
            if partner.street2:
                addr_lines.append(partner.street2)
            city_state_zip = []
            if partner.city:
                city_state_zip.append(partner.city)
            if partner.state_id:
                city_state_zip.append(partner.state_id.name)
            if partner.zip:
                city_state_zip.append(partner.zip)
            if city_state_zip:
                addr_lines.append(" ".join(city_state_zip))
            if partner.country_id:
                addr_lines.append(partner.country_id.name)

        address_html = "<br/>".join(addr_lines) if addr_lines else ""

        contact_lines = []
        phone = (partner and partner.phone) or getattr(company, "phone", False)
        email = (partner and partner.email) or getattr(company, "email", False)
        website = (partner and partner.website) or getattr(company, "website", False)
        vat = (partner and partner.vat) or getattr(company, "vat", False)

        if phone:
            contact_lines.append(f"Phone: {phone}")
        if email:
            contact_lines.append(f"Email: {email}")
        if website:
            contact_lines.append(f"Web: {website}")
        if vat:
            contact_lines.append(f"TIN/VAT: {vat}")

        contact_html = "<br/>".join(contact_lines) if contact_lines else ""

        header_content = []

        header_content.append(f"<strong>{company.name}</strong>")
        if address_html:
            header_content.append(address_html)
        if contact_html:
            header_content.append(contact_html)

        header_html = f"<div>{'<br/>'.join(header_content)}</div>"

        footer_html = (
            company.report_footer
            if company.report_footer
            else f"<div class='text-center'><strong>{company.name}</strong></div>"
        )
        tagline = company.report_header if company.report_header else company.name
        logo = company.logo if company.logo else False

        _logger.info("Creating default brand for company '%s' (ID: %s)", company.name, company.id)
        return self.create({
            "name": company.name,
            "company_id": company.id,
            "logo_large": logo,
            "logo_small": logo,
            "footer_logo": logo,
            "tagline": tagline,
            "header_html": header_html,
            "footer_html": footer_html,
        })

    def action_import_from_company(self):
        for brand in self:
            company = brand.company_id or self.env.company
            _logger.info("Importing details from company '%s' (ID: %s) into brand '%s' (ID: %s)", company.name, company.id, brand.name, brand.id)
            partner = company.partner_id

            addr_lines = []
            if partner:
                if partner.street:
                    addr_lines.append(partner.street)
                if partner.street2:
                    addr_lines.append(partner.street2)
                city_state_zip = []
                if partner.city:
                    city_state_zip.append(partner.city)
                if partner.state_id:
                    city_state_zip.append(partner.state_id.name)
                if partner.zip:
                    city_state_zip.append(partner.zip)
                if city_state_zip:
                    addr_lines.append(" ".join(city_state_zip))
                if partner.country_id:
                    addr_lines.append(partner.country_id.name)

            address_html = "<br/>".join(addr_lines) if addr_lines else ""

            contact_lines = []
            phone = (partner and partner.phone) or getattr(company, "phone", False)
            email = (partner and partner.email) or getattr(company, "email", False)
            website = (partner and partner.website) or getattr(company, "website", False)
            vat = (partner and partner.vat) or getattr(company, "vat", False)

            if phone:
                contact_lines.append(f"Phone: {phone}")
            if email:
                contact_lines.append(f"Email: {email}")
            if website:
                contact_lines.append(f"Web: {website}")
            if vat:
                contact_lines.append(f"TIN/VAT: {vat}")

            contact_html = "<br/>".join(contact_lines) if contact_lines else ""

            header_content = [f"<strong>{company.name}</strong>"]
            if address_html:
                header_content.append(address_html)
            if contact_html:
                header_content.append(contact_html)

            header_html = f"<div>{'<br/>'.join(header_content)}</div>"

            footer_html = (
                company.report_footer
                if company.report_footer
                else f"<div class='text-center'><strong>{company.name}</strong></div>"
            )
            tagline = company.report_header if company.report_header else company.name
            logo = company.logo if company.logo else False

            brand.write({
                "logo_large": logo,
                "logo_small": logo,
                "footer_logo": logo,
                "tagline": tagline,
                "header_html": header_html,
                "footer_html": footer_html,
            })


