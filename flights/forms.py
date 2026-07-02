from django import forms


class BookingConfirmForm(forms.Form):
    """Empty form used only to carry CSRF token for the book action."""
    pass