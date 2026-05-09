/**
 * 🌙 مكون تبديل الوضع الليلي/النهاري - Theme Toggle
 */

import Store from '../store.js';

export function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    const icon = toggle.querySelector('i');
    const label = toggle.querySelector('span');

    // تطبيق السمة الحالية
    Store.subscribe('theme', (theme) => {
        applyTheme(theme, icon, label);
    });

    // مستمع النقر
    toggle.addEventListener('click', () => {
        Store.toggleTheme();
    });

    // تحميل السمة المحفوظة مسبقاً
    const saved = localStorage.getItem('theme');
    if (saved) {
        Store.setState('theme', saved);
    }
}

function applyTheme(theme, icon, label) {
    const html = document.documentElement;
    
    if (theme === 'light') {
        html.classList.remove('dark');
        html.classList.add('light');
        icon.className = 'fas fa-sun text-yellow-400';
        label.textContent = 'الوضع النهاري';
        // ألوان الوضع النهاري
        document.body.classList.add('bg-gray-100', 'text-gray-900');
        document.body.classList.remove('bg-gray-950', 'text-gray-100');
    } else {
        html.classList.add('dark');
        html.classList.remove('light');
        icon.className = 'fas fa-moon text-gray-400';
        label.textContent = 'الوضع الليلي';
        // ألوان الوضع الليلي
        document.body.classList.add('bg-gray-950', 'text-gray-100');
        document.body.classList.remove('bg-gray-100', 'text-gray-900');
    }

    // حفظ التفضيل
    localStorage.setItem('theme', theme);
}
