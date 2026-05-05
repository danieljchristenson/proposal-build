"""Render one ItemizedPricingDoc → 1 two-page tier PDF."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from weasyprint import HTML

from proposal_build.composer.ctx_builders import _LOGO_PATH
from proposal_build.composer.pricing import compute_partnership_savings
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


LAYOUTS_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "layouts"


def render_pricing_pdf(doc, out_path: Path) -> Path:
    """Renders one ItemizedPricingDoc to a 2-page PDF at out_path."""
    bp = load_boilerplate()
    env = Environment(
        loader=FileSystemLoader(str(LAYOUTS_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
    )
    template = env.get_template("itemized_pricing.html")

    model = doc.project
    placeholders = {
        "project_name": model.project_name, "project_short": model.project_short,
        "project_year": model.project_year,
        "client_short": model.client_short, "proposal_type": model.proposal_type,
        "fabrication_lock_long": _date_long(model.fabrication_lock),
        "signing_deadline_long": _date_long(model.signing_deadline),
        "proposal_date_long": _date_long(model.proposal_date),
    }

    discount_pcts = {d["term"]: d["discount"] for d in bp.partnership_discounts}
    partnership_rows = compute_partnership_savings(
        tier_total=doc.tier_total,
        discounts=tuple((d["term"], d["label"]) for d in bp.partnership_discounts),
        discount_pcts=discount_pcts,
    )

    ctx = {
        "logo_path": _LOGO_PATH,
        "client_company": model.client_company, "client_short": model.client_short,
        "client_contact_name": model.client_contact_name,
        "client_contact_title": model.client_contact_title,
        "client_contact_email": model.client_contact_email,
        "client_contact_phone": model.client_contact_phone,
        "project_name": model.project_name, "project_year": model.project_year,
        "proposal_type": model.proposal_type,
        "proposal_date_long": _date_long(model.proposal_date),
        "tier_name": doc.tier.value, "tier_total": doc.tier_total,
        "base_scope_lines": list(doc.base_scope_lines),
        "enhancement_lines": list(doc.enhancement_lines),
        "base_subtotal": sum(li.line_total for li in doc.base_scope_lines),
        "enh_subtotal": sum(li.line_total for li in doc.enhancement_lines),
        "payment_schedule_md_html": _md_to_simple_html(
            substitute_placeholders(model.term_panels.get("payment_schedule", ""), placeholders)
        ),
        "partnership_rows": partnership_rows,
        "non_multi_year_renewal_note": bp.non_multi_year_renewal_note,
        "term_panels": {k: substitute_placeholders(v, placeholders)
                        for k, v in model.term_panels.items()},
    }

    html_str = template.render(**ctx)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_str, base_url=str(LAYOUTS_DIR)).write_pdf(target=str(out_path))
    return out_path


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %d, %Y")


def _md_to_simple_html(text: str) -> str:
    """Wrap each non-blank line of payment_schedule text in a <div class='payment-row'>."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "".join(f"<div class='payment-row'><div>{ln}</div></div>" for ln in lines)
