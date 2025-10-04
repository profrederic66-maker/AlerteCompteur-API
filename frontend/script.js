document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitButton = document.getElementById('submit-button');

    if (!loginForm) return;

    const showToast = (message, type = 'error') => {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('article');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        toast.style.padding = '1rem';
        toast.style.marginBottom = '1rem';
        toast.style.color = 'white';
        toast.style.backgroundColor = (type === 'error') ? 'var(--danger-color, #E53E30)' : 'var(--success-color, #28a745)';
        toast.style.borderRadius = '0.5rem';
        toast.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'opacity 0.5s, transform 0.5s';

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    };

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        submitButton.setAttribute('aria-busy', 'true');
        submitButton.textContent = 'Connexion...';

        const formData = new URLSearchParams();
        formData.append('username', emailInput.value);
        formData.append('password', passwordInput.value);

        try {
            const response = await fetch('/api/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('accessToken', data.access_token);
                window.location.href = '/dashboard.html';
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || 'Une erreur est survenue.';
                showToast(errorMessage, 'error');
            }
        } catch (error) {
            showToast('Impossible de contacter le serveur.', 'error');
            console.error('Login error:', error);
        } finally {
            submitButton.setAttribute('aria-busy', 'false');
            submitButton.textContent = 'Se connecter';
        }
    });
});