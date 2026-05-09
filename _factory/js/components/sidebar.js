/**
 * 🧭 مكون الشريط الجانبي - Sidebar Component
 */

import Store from '../store.js';

export function initSidebar() {
    const navMenu = document.getElementById('nav-menu');
    const menuToggle = document.getElementById('menuToggle');

    // الاشتراك في تغييرات البيانات والعرض الحالي
    Store.subscribe('assetsData', (data) => {
        if (data) renderNav(data.collections);
    });

    Store.subscribe('currentView', (view) => {
        updateActiveLink(view);
    });

    // زر القائمة للجوال
    menuToggle.addEventListener('click', () => {
        Store.toggleSidebar();
    });

    // الاشتراك في تغيير حالة الشريط
    Store.subscribe('sidebarOpen', (isOpen) => {
        const sidebar = document.getElementById('sidebar');
        if (isOpen) {
            sidebar.style.transform = 'translateX(0)';
        } else {
            sidebar.style.transform = 'translateX(100%)';
        }
    });
}

/**
 * رسم قائمة التنقل
 */
function renderNav(collections) {
    const navMenu = document.getElementById('nav-menu');
    
    const icons = {
        images: 'fa-image',
        templates: 'fa-code',
    };

    navMenu.innerHTML = collections.map(col => `
        <button 
            class="nav-link w-full flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-colors hover:bg-gray-800 text-right"
            data-view="${col.id}"
        >
            <i class="fas ${icons[col.id] || 'fa-folder'} text-gray-400 w-5 text-center"></i>
            <span class="flex-1">${col.label}</span>
            <span class="text-xs bg-gray-800 px-2 py-0.5 rounded-full text-gray-400">${col.count}</span>
        </button>
    `).join('');

    // إضافة مستمعي الأحداث
    navMenu.querySelectorAll('.nav-link').forEach(btn => {
        btn.addEventListener('click', () => {
            Store.switchView(btn.dataset.view);
        });
    });
}

/**
 * تحديث الرابط النشط
 */
function updateActiveLink(currentView) {
    document.querySelectorAll('.nav-link').forEach(btn => {
        if (btn.dataset.view === currentView) {
            btn.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/30');
            btn.querySelector('i').classList.add('text-emerald-400');
            btn.querySelector('i').classList.remove('text-gray-400');
        } else {
            btn.classList.remove('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/30');
            btn.querySelector('i').classList.add('text-gray-400');
            btn.querySelector('i').classList.remove('text-emerald-400');
        }
    });
}
