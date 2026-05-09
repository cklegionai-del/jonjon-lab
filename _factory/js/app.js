/**
 * 🚀 المنسق الرئيسي - Main App Coordinator
 * يجمع كل المكونات ويشغل التطبيق
 */

import Store from './store.js';
import { initSidebar } from './components/sidebar.js';
import { initAssetGrid } from './components/assetGrid.js';
import { initAssetDetail } from './components/assetDetail.js';
import { initThemeToggle } from './components/themeToggle.js';

/**
 * تهيئة التطبيق
 */
async function initApp() {
    console.log('🚀 بدء تشغيل مصنع الأصول...');
    
    // 1. تهيئة كل المكونات
    initSidebar();
    initAssetGrid();
    initAssetDetail();
    initThemeToggle();
    
    // 2. إظهار شاشة تحميل جميلة
    showSplashScreen();
    
    // 3. تحميل البيانات
    await Store.loadAssets();
    
    // 4. إخفاء شاشة التحميل
    hideSplashScreen();
    
    // 5. إحصائيات سريعة في وحدة التحكم
    if (Store.state.assetsData) {
        console.log('✅ جاهز!');
        console.log(`📸 ${Store.state.assetsData.summary.totalImages} صورة`);
        console.log(`📄 ${Store.state.assetsData.summary.totalTemplates} قالب`);
    }

    // 6. اختصارات لوحة المفاتيح
    setupKeyboardShortcuts();
}

/**
 * شاشة تحميل مؤقتة
 */
function showSplashScreen() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="flex items-center justify-center py-20">
            <div class="text-center">
                <div class="relative w-20 h-20 mx-auto mb-6">
                    <div class="absolute inset-0 border-4 border-gray-800 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-emerald-400 rounded-full border-t-transparent animate-spin"></div>
                    <i class="fas fa-cubes text-2xl text-emerald-400 absolute inset-0 flex items-center justify-center"></i>
                </div>
                <h2 class="text-xl font-bold mb-2">جاري تحميل الأصول...</h2>
                <p class="text-gray-500">يتم مسح المكتبات والمجلدات</p>
            </div>
        </div>
    `;
}

function hideSplashScreen() {
    // يتم إخفاؤها تلقائياً عند أول Render للـ Grid
}

/**
 * اختصارات لوحة المفاتيح
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+K أو Cmd+K = فتح البحث
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('searchInput').focus();
        }
        // 1 = صور، 2 = قوالب
        if ((e.ctrlKey || e.metaKey) && e.key === '1') {
            e.preventDefault();
            Store.switchView('images');
        }
        if ((e.ctrlKey || e.metaKey) && e.key === '2') {
            e.preventDefault();
            Store.switchView('templates');
        }
        // T = تبديل السمة
        if ((e.ctrlKey || e.metaKey) && e.key === 't') {
            e.preventDefault();
            Store.toggleTheme();
        }
    });

    console.log('⌨️  اختصارات جاهزة: Cmd+K بحث | Cmd+1 صور | Cmd+2 قوالب | Cmd+T سمة');
}

// انطلاق!
initApp().catch(err => {
    console.error('❌ فشل التشغيل:', err);
    document.getElementById('mainContent').innerHTML = `
        <div class="text-center py-20 text-red-400">
            <i class="fas fa-exclamation-triangle text-5xl mb-4 block"></i>
            <p>فشل تحميل التطبيق</p>
            <p class="text-sm text-gray-500 mt-2">${err.message}</p>
        </div>
    `;
});
