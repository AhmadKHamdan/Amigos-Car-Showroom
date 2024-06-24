document.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('.employee-table tbody tr');
    rows.forEach(row => {
        row.addEventListener('mouseover', () => {
            row.style.backgroundColor = '#e0e0e0';
        });
        row.addEventListener('mouseout', () => {
            row.style.backgroundColor = '';
        });
    });
});

