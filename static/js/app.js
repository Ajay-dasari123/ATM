document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('is-ready');

    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach((link) => {
        if (link.getAttribute('href') === currentPath) {
            link.setAttribute('aria-current', 'page');
        }
    });

    const dashboardPaths = ['/checkBalance', '/deposit', '/withdraw', '/viewtransactions'];
    if (dashboardPaths.includes(currentPath)) {
        const dashboardLink = document.querySelector('.nav-links a[href^="/dashboard/"]');
        dashboardLink?.setAttribute('aria-current', 'page');
    }

    document.querySelectorAll('form').forEach((form) => {
        form.addEventListener('submit', () => {
            const submitButton = form.querySelector('input[type="submit"]');
            if (!submitButton || !form.checkValidity()) {
                return;
            }

            submitButton.disabled = true;
            submitButton.value = 'Processing...';
            form.classList.add('is-processing');
        });
    });

    document.querySelectorAll('[data-export-pdf]').forEach((button) => {
        button.addEventListener('click', () => {
            const table = document.querySelector('table');

            if (!table) {
                alert('No transaction history found to download.');
                return;
            }

            // Extract table rows containing <td> elements only
            const rows = [...table.querySelectorAll('tr')]
                .filter((row) => row.querySelector('td'))
                .map((row) => [...row.querySelectorAll('td')].map((cell) => cell.textContent.trim()));

            if (rows.length === 0) {
                alert('No transactions available to download.');
                return;
            }

            const jsPDF = window.jspdf?.jsPDF;
            if (jsPDF) {
                try {
                    const pdf = new jsPDF();

                    pdf.setFontSize(18);
                    pdf.text('Transaction History', 20, 20);
                    pdf.setFontSize(11);
                    pdf.text('Transaction ID', 20, 34);
                    pdf.text('Description', 65, 34);
                    pdf.setLineWidth(0.5);
                    pdf.line(20, 36, 190, 36);

                    let yPosition = 44;
                    rows.forEach(([id, description]) => {
                        if (!id && !description) return;
                        const lines = pdf.splitTextToSize(description || '', 125);
                        pdf.text(String(id || ''), 20, yPosition);
                        pdf.text(lines, 65, yPosition);
                        yPosition += Math.max(8, lines.length * 6);

                        if (yPosition > 275) {
                            pdf.addPage();
                            yPosition = 20;
                        }
                    });

                    pdf.save('transactions.pdf');
                    return;
                } catch (err) {
                    console.error('jsPDF failed, falling back to CSV download:', err);
                }
            }

            // Fallback: Generate and trigger client-side TXT file download
            let textContent = "Transaction ID\tTransaction Description\n";
            rows.forEach(([id, description]) => {
                textContent += `${id}\t${description}\n`;
            });
            const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'transactions.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    });
});
