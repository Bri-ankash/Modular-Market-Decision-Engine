from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment

@login_required
def admin_approve(request, payment_id):
    if not request.user.is_superuser:
        return redirect('/')
    payment = get_object_or_404(Payment, id=payment_id)
    payment.approve(admin_user=request.user)
    messages.success(request, f'Subscription activated for {payment.user.email} — {payment.plan}')
    return redirect('/admin/payments/payment/')
