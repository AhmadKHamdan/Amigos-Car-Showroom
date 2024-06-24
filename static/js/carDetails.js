document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('paymentForm');
    const purchaseForm = document.getElementById('purchaseForm');
    const paymentMethod = document.getElementById('paymentMethod');
    const paymentMethodHidden = document.getElementById('payment_method');

    paymentForm.addEventListener('submit', function(event) {
        event.preventDefault();
        paymentMethodHidden.value = paymentMethod.value;
        purchaseForm.submit();
        closeModal();
    });
});

function showModal() {
    document.getElementById('paymentMethodModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('paymentMethodModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('paymentMethodModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
