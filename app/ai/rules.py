"""Operational proposals, never automatic financial or fulfilment actions."""
from app.models import ProductIssue

def proposal(issue: ProductIssue) -> str:
    if issue.problem in ('seam','unknown') or issue.product=='unknown':return 'human_review'
    if issue.product=='board' and issue.problem=='air_loss':
        if not issue.valve_checked:return 'ask_valve_check'
        if issue.delivery_days is None:return 'ask_details'
        next_action='replace_board' if issue.delivery_days<=30 else 'repair_kit'
    elif issue.product=='board' and issue.problem=='accessory':next_action='missing_accessory'
    elif issue.product=='shelf':
        if issue.problem=='panels':
            if not issue.parts:return 'ask_details'
            next_action='replacement_panels' if len(set(issue.parts))<=2 else 'replacement_unit'
        else:next_action={'hardware':'hardware_kit','frame':'replacement_unit','finish':'exchange'}.get(issue.problem,'human_review')
    else:return 'human_review'
    return next_action if issue.order else 'ask_details'
