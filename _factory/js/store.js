/**
 * 🧠 المتجر المركزي - Central State Store
 * الإصدار 2.0: متصل بالـ API
 */

const API_BASE = 'http://localhost:8000/api';

const Store = {
    state: {
        currentView: 'images',
        currentCollection: null,
        selectedAsset: null,
        searchQuery: '',
        theme: 'dark',
        sidebarOpen: true,
        assetsData: null,
        isLoading: true,
    },

    listeners: {},

    setState(key, value) {
        this.state[key] = value;
        this.notify(key, value);
    },

    setMultiple(updates) {
        Object.entries(updates).forEach(([key, value]) => {
            this.state[key] = value;
            this.notify(key, value);
        });
    },

    subscribe(key, callback) {
        if (!this.listeners[key]) this.listeners[key] = [];
        this.listeners[key].push(callback);
        callback(this.state[key]);
    },

    notify(key, value) {
        if (this.listeners[key]) {
            this.listeners[key].forEach(cb => cb(value));
        }
    },

    switchView(viewId) {
        this.setState('currentView', viewId);
        this.setState('selectedAsset', null);
        this.setState('searchQuery', '');
        if (this.state.assetsData) {
            const collection = this.state.assetsData.find(c => c.id === viewId);
            this.setState('currentCollection', collection);
        }
    },

    selectAsset(asset) {
        this.setState('selectedAsset', asset);
    },

    closeDetail() {
        this.setState('selectedAsset', null);
    },

    toggleTheme() {
        const newTheme = this.state.theme === 'dark' ? 'light' : 'dark';
        this.setState('theme', newTheme);
    },

    toggleSidebar() {
        this.setState('sidebarOpen', !this.state.sidebarOpen);
    },

    setSearch(query) {
        this.setState('searchQuery', query);
    },

    async loadAssets() {
        this.setState('isLoading', true);
        try {
            const response = await fetch(`${API_BASE}/collections`);
            const collections = await response.json();
            
            // تحويل البيانات لنفس الشكل القديم
            const data = {
                collections: collections,
                summary: {
                    totalImages: collections.find(c => c.id === 'images')?.count || 0,
                    totalTemplates: collections.find(c => c.id === 'templates')?.count || 0,
                    totalPages: collections.find(c => c.id === 'pages')?.count || 0,
                }
            };
            
            this.setMultiple({
                assetsData: data,
                isLoading: false
            });
            
            if (data.collections.length > 0) {
                this.switchView(data.collections[0].id);
            }
        } catch (error) {
            console.error('❌ فشل الاتصال بالـ API:', error);
            // الرجوع لـ JSON إذا فشل الـ API
            try {
                const response = await fetch('./data/assets.json');
                const data = await response.json();
                this.setMultiple({ assetsData: data, isLoading: false });
                if (data.collections.length > 0) {
                    this.switchView(data.collections[0].id);
                }
            } catch (e) {
                console.error('❌ فشل التحميل من الملف المحلي أيضاً:', e);
                this.setState('isLoading', false);
            }
        }
    },

    getFilteredAssets() {
        if (!this.state.currentCollection || !this.state.currentCollection.items) return [];
        const query = this.state.searchQuery.toLowerCase().trim();
        if (!query) return this.state.currentCollection.items;
        
        return this.state.currentCollection.items.filter(item => {
            return item.name.toLowerCase().includes(query) ||
                   (item.category && item.category.toLowerCase().includes(query)) ||
                   (item.extension && item.extension.includes(query));
        });
    }
};

export default Store;
