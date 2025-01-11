# Third party
from django.dispatch import Signal


change_referent_contact = Signal(providing_args=["current_referent", "new_referent"])
bnb_capacity_changed = Signal(
    providing_args=["instance", "old_capacity", "new_capacity"]
)
