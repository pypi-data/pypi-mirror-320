from policyengine_us.model_api import *


class mi_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
