/**
 * JavaScript لمتابعة حالة الدفع وتحديثها تلقائياً
 */

// التحقق من حالة الدفع كل 3 ثوانٍ
function checkPaymentStatus(bookingId) {
    if (!bookingId) return;
    
    fetch('/payments/check-payment-status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
            booking_id: bookingId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.payment_status === 'paid') {
            // تحديث الصفحة لإظهار الحالة الجديدة
            location.reload();
        } else if (data.status === 'pending') {
            // إعادة المحاولة بعد 3 ثوانٍ
            setTimeout(() => checkPaymentStatus(bookingId), 3000);
        }
    })
    .catch(error => {
        console.error('خطأ في التحقق من حالة الدفع:', error);
        // إعادة المحاولة بعد 5 ثوانٍ في حالة الخطأ
        setTimeout(() => checkPaymentStatus(bookingId), 5000);
    });
}

// الحصول على CSRF token
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// بدء التحقق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    const bookingIdElement = document.querySelector('[data-booking-id]');
    if (bookingIdElement) {
        const bookingId = bookingIdElement.getAttribute('data-booking-id');
        const paymentStatus = bookingIdElement.getAttribute('data-payment-status');
        
        // إذا لم يكن الدفع مكتملاً، ابدأ التحقق
        if (paymentStatus !== 'paid') {
            checkPaymentStatus(bookingId);
        }
    }
});
