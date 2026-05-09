/**
 * 🖼️ مكون شبكة عرض الأصول - Asset Grid Component
 */

import Store from '../store.js';

export function initAssetGrid() {
    const mainContent = document.getElementById('mainContent');
    const searchInput = document.getElementById('searchInput');
    const assetCount = document.getElementById('assetCount');

    // الاشتراك في تغييرات تؤثر على العرض
    Store.subscribe('currentCollection', renderGrid);
    Store.subscribe('searchQuery', renderGrid);
    Store.subscribe('currentView', () => renderGrid(Store.state.currentCollection));
    Store.subscribe('isLoading', (loading) => {
        if (loading) showLoading();
    });

    // مستمع البحث
    searchInput.addEventListener('input', (e) => {
        Store.setSearch(e.target.value);
    });
}

function showLoading() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="flex items-center justify-center py-20">
            <div class="text-center">
                <i class="fas fa-spinner fa-spin text-4xl text-emerald-400 mb-4"></i>
                <p class="text-gray-400">جاري تحميل الأصول...</p>
            </div>
        </div>
    `;
}

function renderGrid(collection) {
    if (!collection) return;
    
    const mainContent = document.getElementById('mainContent');
    const assetCount = document.getElementById('assetCount');
    const pageTitle = document.getElementById('pageTitle');

    // تحديث العنوان
    pageTitle.textContent = collection.icon === 'image' ? '📸 مكتبة الصور' : '📄 قوالب HTML';
    
    // الحصول على الأصول المفلترة
    const assets = Store.getFilteredAssets();
    
    // تحديث العداد
    assetCount.textContent = `${assets.length} / ${collection.count} أصل`;

    // رسم الأصول حسب النوع
    if (collection.id === 'images') {
        renderImageGrid(mainContent, assets);
    } else {
        renderTemplateGrid(mainContent, assets);
    }
}

/**
 * شبكة عرض الصور
 */
function renderImageGrid(container, images) {
    if (images.length === 0) {
        container.innerHTML = `
            <div class="text-center py-20 text-gray-500">
                <i class="fas fa-search text-5xl mb-4 block"></i>
                <p>لا توجد صور مطابقة للبحث</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            ${images.slice(0, 100).map(img => `
                <div class="asset-card card-hover bg-gray-900 border border-gray-800 rounded-xl overflow-hidden cursor-pointer group"
                     data-id="${img.id}">
                    <!-- المعاينة -->
                    <div class="aspect-square bg-gray-800 flex items-center justify-center overflow-hidden">
                        <img src="file://${img.path}" 
                             alt="${img.name}"
                             loading="lazy"
                             class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                             onerror="this.parentElement.innerHTML='<i class=\\'fas fa-image text-4xl text-gray-600\\'></i>'">
                    </div>
                    <!-- المعلومات -->
                    <div class="p-3">
                        <p class="text-sm font-medium truncate" title="${img.name}">${img.name}</p>
                        <div class="flex items-center justify-between mt-1.5">
                            <span class="text-xs text-gray-500">${img.size}</span>
                            <span class="text-xs bg-gray-800 px-2 py-0.5 rounded-full text-gray-400 truncate max-w-[80px]" title="${img.category}">
                                ${img.category}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        ${images.length > 100 ? `<p class="text-center text-gray-500 mt-4 text-sm">... و ${images.length - 100} صورة أخرى (استخدم البحث للتصفية)</p>` : ''}
    `;

    // إضافة مستمعي النقر
    container.querySelectorAll('.asset-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.dataset.id;
            const collection = Store.state.currentCollection;
            const asset = collection.items.find(item => item.id === id);
            if (asset) Store.selectAsset(asset);
        });
    });
}

/**
 * شبكة عرض القوالب
 */
function renderTemplateGrid(container, templates) {
    if (templates.length === 0) {
        container.innerHTML = `
            <div class="text-center py-20 text-gray-500">
                <i class="fas fa-code text-5xl mb-4 block"></i>
                <p>لا توجد قوالب مطابقة</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${templates.map(tpl => `
                <div class="asset-card card-hover bg-gray-900 border border-gray-800 rounded-xl p-4 cursor-pointer group"
                     data-id="${tpl.id}">
                    <div class="flex items-start justify-between mb-3">
                        <i class="fas fa-file-code text-3xl text-emerald-400 group-hover:scale-110 transition-transform"></i>
                        <span class="text-xs bg-gray-800 px-2 py-0.5 rounded-full text-gray-400">
                            ${tpl.totalFiles} ملف
                        </span>
                    </div>
                    <h3 class="font-bold text-lg mb-2 group-hover:text-emerald-400 transition-colors">
                        ${tpl.name}
                    </h3>
                    <div class="flex flex-wrap gap-1">
                        ${tpl.files.slice(0, 5).map(f => `
                            <span class="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-500">
                                ${f.name.length > 20 ? f.name.slice(0, 20) + '...' : f.name}
                            </span>
                        `).join('')}
                        ${tpl.files.length > 5 ? `<span class="text-xs text-gray-600">+${tpl.totalFiles - 5}...</span>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    // مستمعو النقر
    container.querySelectorAll('.asset-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.dataset.id;
            const collection = Store.state.currentCollection;
            const asset = collection.items.find(item => item.id === id);
            if (asset) Store.selectAsset(asset);
        });
    });
}
