// Script pour améliorer l'interactivité

document.addEventListener('DOMContentLoaded', function() {
    // Animation au survol des cartes
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Gestion de la navigation active
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath.includes('/dash1') && link.getAttribute('href') === '/dash1/') ||
            (currentPath.includes('/dash2') && link.getAttribute('href') === '/dash2/')) {
            link.classList.add('active');
        }
    });

    // Smooth scroll pour les ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Ajustement de la hauteur de l'iframe (debounce pour éviter que le graphique "bouge")
    const iframe = document.querySelector('.dashboard-iframe');
    if (iframe) {
        let resizeTimeout;
        function adjustIframeHeight() {
            const nav = document.querySelector('.dashboard-nav');
            if (!nav) return;
            const navHeight = nav.offsetHeight;
            const windowHeight = window.innerHeight;
            iframe.style.height = (windowHeight - navHeight) + 'px';
        }
        function debouncedResize() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(adjustIframeHeight, 150);
        }
        adjustIframeHeight();
        window.addEventListener('resize', debouncedResize);
    }

    // Effet de chargement
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.opacity = '0';
        setTimeout(() => {
            mainContent.style.transition = 'opacity 0.5s ease';
            mainContent.style.opacity = '1';
        }, 100);
    }

    // Console log pour le débogage
    console.log('⚡ DashFlow - Script chargé avec succès');
    console.log('📍 Page actuelle:', window.location.pathname);
});

// Fonction pour gérer les erreurs de chargement d'iframe
window.addEventListener('error', function(e) {
    console.error('Erreur détectée:', e);
}, true);
