/**
 * 🔍 مكون تفاصيل الأصل - Asset Detail Modal
 */

import Store from '../store.js';

export function initAssetDetail() {
    const modal = document.getElementById('detailModal');
    const modalContent = document.getElementById('modalContent');

    // الاشتراك في تغيير الأصل المحدد
    Store.subscribe('selectedAsset', (asset) => {
        if (asset) {
            renderDetail(asset);
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } else {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    });

    // إغلاق المودال بالنقر على الخلفية
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            Store.closeDetail();
        }
    });

    // إغلاق بـ Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') Store.closeDetail();
    });
}

function renderDetail(asset) {
    const modalContent = document.getElementById('modalContent');
    const isImage = asset.type === 'image';

    if (isImage) {
        modalContent.innerHTML = `
            <div class="relative">
                <!-- زر الإغلاق -->
                <button onclick="document.dispatchEvent(new CustomEvent('close-detail'))" 
                        class="absolute top-3 right-3 z-10 bg-black/50 hover:bg-black/70 text-white w-8 h-8 rounded-full flex items-center justify-center transition-colors">
                    <i class="fas fa-times"></i>
                </button>
                
                <!-- الصورة -->
                <div class="bg-gray-950 rounded-t-2xl flex items-center justify-center min-h-[300px] max-h-[60vh] overflow-hidden">
                    <img src="file://${asset.path}" 
                         alt="${asset.name}"
                         class="max-w-full max-h-[60vh] object-contain"
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22><rect fill=%22%231f2937%22 width=%22200%22 height=%22200%22/><text fill=%22%239ca3af%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22 font-size=%2240%22>🖼️</text></svg>'">
                </div>
                
                <!-- التفاصيل -->
                <div class="p-5 space-y-3">
                    <h2 class="text-lg font-bold break-all">${asset.name}</h2>
                    
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div class="bg-gray-800 rounded-lg p-3">
                            <span class="text-gray-500 block text-xs mb-1">📁 المجلد</span>
                            <span class="text-gray-200">${asset.category}</span>
                        </div>
                        <div class="bg-gray-800 rounded-lg p-3">
                            <span class="text-gray-500 block text-xs mb-1">📏 الحجم</span>
                            <span class="text-gray-200">${asset.size}</span>
                        </div>
                        <div class="bg-gray-800 rounded-lg p-3">
                            <span class="text-gray-500 block text-xs mb-1">📝 الامتداد</span>
                            <span class="text-gray-200 uppercase">${asset.extension}</span>
                        </div>
                        <div class="bg-gray-800 rounded-lg p-3">
                            <span class="text-gray-500 block text-xs mb-1">📅 التعديل</span>
                            <span class="text-gray-200 text-xs">${new Date(asset.modified).toLocaleDateString('ar-TN')}</span>
                        </div>
                    </div>
                    
                    <div class="bg-gray-800 rounded-lg p-3">
                        <span class="text-gray-500 block text-xs mb-1">📂 المسار</span>
                        <code class="text-gray-300 text-xs break-all">${asset.relativePath}</code>
                    </div>
                    
                    <!-- أزرار الإجراءات -->
                    <div class="flex gap-2 pt-2">
                        <a href="file://${asset.path}" target="_blank" 
                           class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2 rounded-lg text-sm text-center transition-colors">
                            <i class="fas fa-external-link-alt ml-1"></i> فتح
                        </a>
                        <button onclick="navigator.clipboard.writeText('${asset.path}')"
                                class="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg text-sm transition-colors">
                            <i class="fas fa-copy ml-1"></i> نسخ المسار
                        </button>
                    </div>
                </div>
            </div>
        `;
    } else {
        // عرض تفاصيل القالب
        modalContent.innerHTML = `
            <div class="relative">
                <button onclick="document.dispatchEvent(new CustomEvent('close-detail'))" 
                        class="absolute top-3 right-3 z-10 bg-black/50 hover:bg-black/70 text-white w-8 h-8 rounded-full flex items-center justify-center transition-colors">
                    <i class="fas fa-times"></i>
                </button>
                
                <div class="p-5">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-file-code text-4xl text-emerald-400"></i>
                        <div>
                            <h2 class="text-xl font-bold">${asset.name}</h2>
                            <span class="text-sm text-gray-400">${asset.totalFiles} ملف</span>
                        </div>
                    </div>
                    
                    <div class="bg-gray-800 rounded-lg p-3 mb-4">
                        <span class="text-gray-500 block text-xs mb-1">📂 المسار</span>
                        <code class="text-gray-300 text-xs break-all">${asset.relativePath}</code>
                    </div>
                    
                    <h3 class="text-sm font-bold text-gray-400 mb-2">📄 الملفات (${asset.totalFiles})</h3>
                    <div class="max-h-40 overflow-y-auto space-y-1 bg-gray-800 rounded-lg p-3">
                        ${asset.files.map(f => `
                            <div class="text-xs text-gray-400 flex items-center gap-2 py-0.5">
                                <i class="fas fa-${getFileIcon(f.extension)} text-gray-500 w-4 text-center"></i>
                                <span>${f.name}</span>
                            </div>
                        `).join('')}
                        ${asset.totalFiles > 10 ? `<p class="text-xs text-gray-600 pt-1">... و ${asset.totalFiles - 10} ملف آخر</p>` : ''}
                    </div>
                    
                    <div class="flex gap-2 pt-4">
                        <a href="file://${asset.path}" target="_blank" 
                           class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2 rounded-lg text-sm text-center">
                            <i class="fas fa-folder-open ml-1"></i> فتح المجلد
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    // مستمع زر الإغلاق
    document.addEventListener('close-detail', () => Store.closeDetail(), { once: true });
}

/**
 * أيقونة حسب نوع الملف
 */
function getFileIcon(ext) {
    const map = {
        '.html': 'fa-html5',
        '.css': 'fa-css3',
        '.js': 'fa-js',
        '.json': 'fa-code',
        '.md': 'fa-markdown',
        '.svg': 'fa-vector-square',
    };
    return map[ext] || 'fa-file';
}
