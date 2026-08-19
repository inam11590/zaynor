/* ==========================================================================
   ZAYNOR Admin Dashboard — Phase 6
   Handles login, products CRUD, orders management, customer listing.
   ========================================================================== */
(function () {
    'use strict';

    var API = (location.hostname === "localhost" || location.hostname === "127.0.0.1" || !location.hostname)
        ? 'http://127.0.0.1:8000/api/v1'
        : 'https://zaynor-backend.onrender.com/api/v1';
    var token = localStorage.getItem('zaynor_admin_token');

    // ── DOM helpers ──────────────────────────────────────────────────────
    function $(sel) { return document.querySelector(sel); }
    function $$(sel) { return document.querySelectorAll(sel); }

    function show(el) { el.classList.remove('hidden'); }
    function hide(el) { el.classList.add('hidden'); }

    function toast(msg) {
        var t = $('#toast');
        t.textContent = msg;
        show(t);
        setTimeout(function () { hide(t); }, 2500);
    }

    // ── API helper ───────────────────────────────────────────────────────
    function api(method, path, body) {
        var opts = {
            method: method,
            headers: {}
        };
        if (token) {
            opts.headers['Authorization'] = 'Bearer ' + token;
        }
        if (body !== undefined) {
            if (body instanceof FormData) {
                opts.body = body;
            } else {
                opts.headers['Content-Type'] = 'application/json';
                opts.body = JSON.stringify(body);
            }
        }
        return fetch(API + path, opts).then(function (res) {
            if (res.status === 204) return null;
            return res.json().then(function (data) {
                if (!res.ok) {
                    throw new Error(data.detail || 'Request failed');
                }
                return data;
            });
        });
    }

    // ── Login / Logout ───────────────────────────────────────────────────
    function isLoggedIn() {
        return !!token;
    }

    function doLogin(email, password) {
        var form = new URLSearchParams();
        form.append('username', email);
        form.append('password', password);

        return fetch(API + '/auth/login', {
            method: 'POST',
            body: form
        }).then(function (res) {
            return res.json().then(function (data) {
                if (!res.ok) throw new Error(data.detail || 'Login failed');
                token = data.access_token;
                localStorage.setItem('zaynor_admin_token', token);
                return data;
            });
        });
    }

    function doLogout() {
        token = null;
        localStorage.removeItem('zaynor_admin_token');
        show($('#login-screen'));
        hide($('#dashboard'));
    }

    // ── UI State ─────────────────────────────────────────────────────────
    function showDashboard() {
        hide($('#login-screen'));
        show($('#dashboard'));
        loadTab('products');
    }

    function loadTab(tab) {
        $$('.admin-tab-content').forEach(function (el) { el.classList.remove('active'); });
        $$('.admin-tab').forEach(function (el) { el.classList.remove('active'); });

        var content = $('#tab-' + tab);
        var btn = $('.admin-tab[data-tab="' + tab + '"]');
        if (content) content.classList.add('active');
        if (btn) btn.classList.add('active');

        if (tab === 'products') loadProducts();
        else if (tab === 'orders') loadOrders();
        else if (tab === 'customers') loadCustomers();
        else if (tab === 'analytics') loadAnalytics();
    }

    // ── Products ─────────────────────────────────────────────────────────
    function loadProducts() {
        api('GET', '/products/all').then(function (products) {
            var tbody = $('#products-table-body');
            tbody.innerHTML = '';
            products.forEach(function (p) {
                var imgSrc = p.image ? '../' + p.image : '';
                var statusHtml = p.is_active
                    ? '<span class="status-badge status-delivered">Active</span>'
                    : '<span class="status-badge status-cancelled">Inactive</span>';
                var tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + p.id + '</td>' +
                    '<td style="display:flex;align-items:center;gap:0.6rem;">' +
                        (imgSrc ? '<img src="' + esc(imgSrc) + '" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:6px;border:1px solid var(--border-light);">' : '') +
                        '<span>' + esc(p.name) + '</span>' +
                    '</td>' +
                    '<td>' + esc(p.slug) + '</td>' +
                    '<td>' + Number(p.price).toLocaleString() + '</td>' +
                    '<td>' + esc(p.category ? p.category.name : '-') + '</td>' +
                    '<td>' + statusHtml + '</td>' +
                    '<td class="actions-cell">' +
                        '<button class="btn btn-outline btn-small" data-action="toggle-active" data-id="' + p.id + '" data-active="' + (p.is_active ? '1' : '0') + '">' + (p.is_active ? 'Hide' : 'Show') + '</button>' +
                        '<button class="btn btn-outline btn-small" data-action="edit" data-id="' + p.id + '" data-slug="' + esc(p.slug) + '">Edit</button>' +
                        '<button class="btn btn-danger btn-small" data-action="delete" data-id="' + p.id + '">Delete</button>' +
                    '</td>';
                tbody.appendChild(tr);
            });
        }).catch(function (e) { toast('Error: ' + e.message); });
    }

    function openProductModal(product) {
        var modal = $('#product-modal');
        var title = $('#product-modal-title');
        var preview = $('#pf-image-preview');
        hide(preview);

        if (product) {
            title.textContent = 'Edit Product';
            $('#pf-id').value = product.id;
            $('#pf-name').value = product.name;
            $('#pf-slug').value = product.slug;
            $('#pf-price').value = product.price;
            $('#pf-image').value = product.image;
            $('#pf-short-desc').value = product.short_description;
            $('#pf-description').value = product.description;
            var catSlug = product.category ? product.category.slug : 'perfumes';
            $('#pf-category').value = catSlug;
            var specs = product.specs;
            if (typeof specs === 'object') {
                $('#pf-specs').value = JSON.stringify(specs, null, 2);
            } else {
                $('#pf-specs').value = specs || '{}';
            }
            $('#pf-active').checked = product.is_active !== false;
            if (product.image) {
                preview.innerHTML = '<img src="../' + esc(product.image) + '" style="width:100%;height:100%;object-fit:cover;">';
                show(preview);
            }
        } else {
            title.textContent = 'Add Product';
            $('#product-form').reset();
            $('#pf-id').value = '';
            $('#pf-active').checked = true;
        }
        $('#pf-image-file').value = '';
        hide($('#product-form-error'));
        show(modal);
    }

    function saveProduct(e) {
        e.preventDefault();
        var id = $('#pf-id').value;
        var specsVal = $('#pf-specs').value.trim() || '{}';
        var catSlug = $('#pf-category').value;
        var name = $('#pf-name').value;
        var slug = $('#pf-slug').value;
        var price = $('#pf-price').value;
        var image = $('#pf-image').value;
        var shortDesc = $('#pf-short-desc').value;
        var desc = $('#pf-description').value;
        var isActive = $('#pf-active').checked;

        function buildQs(extra) {
            var qs = '?name=' + encodeURIComponent(name) +
                '&slug=' + encodeURIComponent(slug) +
                '&price=' + encodeURIComponent(price) +
                '&image=' + encodeURIComponent(image) +
                '&short_description=' + encodeURIComponent(shortDesc) +
                '&description=' + encodeURIComponent(desc) +
                '&category_slug=' + encodeURIComponent(catSlug) +
                '&specs=' + encodeURIComponent(specsVal) +
                '&is_active=' + isActive;
            return qs;
        }

        if (id) {
            api('PUT', '/products/' + id + buildQs())
                .then(function () {
                    toast('Product updated');
                    hide($('#product-modal'));
                    loadProducts();
                })
                .catch(function (e) {
                    show($('#product-form-error'));
                    $('#product-form-error').textContent = e.message;
                });
        } else {
            api('POST', '/products/' + buildQs())
                .then(function () {
                    toast('Product created');
                    hide($('#product-modal'));
                    loadProducts();
                })
                .catch(function (e) {
                    show($('#product-form-error'));
                    $('#product-form-error').textContent = e.message;
                });
        }
    }

    function deleteProduct(id) {
        if (!confirm('Delete this product?')) return;
        api('DELETE', '/products/' + id)
            .then(function () { toast('Product deleted'); loadProducts(); })
            .catch(function (e) { toast('Error: ' + e.message); });
    }

    function toggleProductActive(id, currentActive) {
        var newActive = currentActive === '1' ? false : true;
        api('PUT', '/products/' + id + '?is_active=' + newActive)
            .then(function () {
                toast(newActive ? 'Product is now visible' : 'Product hidden from website');
                loadProducts();
            })
            .catch(function (e) { toast('Error: ' + e.message); });
    }

    function uploadImage(file, callback) {
        var formData = new FormData();
        formData.append('file', file);
        var catSlug = $('#pf-category').value;
        var folder = catSlug === 'skincare' ? 'skincare' : 'perfumes';
        api('POST', '/products/upload?folder=' + encodeURIComponent(folder), formData)
            .then(function (data) {
                callback(data.path);
            })
            .catch(function (e) {
                toast('Upload failed: ' + e.message);
            });
    }

    // ── Orders ───────────────────────────────────────────────────────────
    function loadOrders(statusFilter) {
        var qs = statusFilter ? '?status=' + encodeURIComponent(statusFilter) : '';
        api('GET', '/orders/' + qs).then(function (orders) {
            var tbody = $('#orders-table-body');
            tbody.innerHTML = '';
            orders.forEach(function (o) {
                var itemCount = o.items ? o.items.length : 0;
                var date = o.created_at ? new Date(o.created_at).toLocaleDateString() : '-';
                var tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + o.id + '</td>' +
                    '<td>' + o.customer_id + '</td>' +
                    '<td>' + itemCount + ' item(s)</td>' +
                    '<td>' + Number(o.total).toLocaleString() + '</td>' +
                    '<td><span class="status-badge status-' + o.status + '">' + o.status + '</span></td>' +
                    '<td>' + date + '</td>' +
                    '<td><button class="btn btn-outline btn-small" data-action="view-order" data-id="' + o.id + '">View</button></td>';
                tbody.appendChild(tr);
            });
        }).catch(function (e) { toast('Error: ' + e.message); });
    }

    var currentOrderId = null;

    function openOrderModal(orderId) {
        currentOrderId = orderId;
        api('GET', '/orders/' + orderId).then(function (o) {
            var body = $('#order-detail-body');
            var date = o.created_at ? new Date(o.created_at).toLocaleString() : '-';
            var itemsHtml = '';
            if (o.items && o.items.length) {
                itemsHtml = '<ul class="order-items-list">';
                o.items.forEach(function (item) {
                    itemsHtml += '<li>' +
                        '<span>' + esc(item.product_name) + ' x' + item.quantity + '</span>' +
                        '<span>' + Number(item.unit_price).toLocaleString() + ' PKR</span>' +
                    '</li>';
                });
                itemsHtml += '</ul>';
            }

            body.innerHTML =
                '<dl class="order-meta">' +
                    '<div><dt>Order ID</dt><dd>#' + o.id + '</dd></div>' +
                    '<div><dt>Status</dt><dd><span class="status-badge status-' + o.status + '">' + o.status + '</span></dd></div>' +
                    '<div><dt>Customer ID</dt><dd>' + o.customer_id + '</dd></div>' +
                    '<div><dt>Date</dt><dd>' + date + '</dd></div>' +
                    '<div><dt>Total</dt><dd>' + Number(o.total).toLocaleString() + ' PKR</dd></div>' +
                    '<div><dt>Notes</dt><dd>' + esc(o.notes || 'None') + '</dd></div>' +
                '</dl>' +
                itemsHtml;

            $('#order-new-status').value = o.status;
            show($('#order-modal'));
        }).catch(function (e) { toast('Error: ' + e.message); });
    }

    function updateOrderStatus() {
        if (!currentOrderId) return;
        var newStatus = $('#order-new-status').value;
        api('PATCH', '/orders/' + currentOrderId + '/status?new_status=' + encodeURIComponent(newStatus))
            .then(function () {
                toast('Order status updated');
                hide($('#order-modal'));
                loadOrders($('#order-status-filter').value);
            })
            .catch(function (e) { toast('Error: ' + e.message); });
    }

    // ── Customers ────────────────────────────────────────────────────────
    function loadCustomers() {
        api('GET', '/customers/').then(function (customers) {
            var tbody = $('#customers-table-body');
            tbody.innerHTML = '';
            customers.forEach(function (c) {
                var date = c.created_at ? new Date(c.created_at).toLocaleDateString() : '-';
                var tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + c.id + '</td>' +
                    '<td>' + esc(c.name) + '</td>' +
                    '<td>' + esc(c.email) + '</td>' +
                    '<td>' + esc(c.phone || '-') + '</td>' +
                    '<td>' + esc(c.address || '-') + '</td>' +
                    '<td>' + date + '</td>';
                tbody.appendChild(tr);
            });
        }).catch(function (e) { toast('Error: ' + e.message); });
    }

    // ── Utilities ────────────────────────────────────────────────────────
    function esc(str) {
        if (!str) return '';
        var div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ── Event Binding ────────────────────────────────────────────────────
    function init() {
        // Check if already logged in
        if (isLoggedIn()) {
            api('GET', '/auth/me').then(function () {
                showDashboard();
                loadUserInfo();
            }).catch(function () {
                token = null;
                localStorage.removeItem('zaynor_admin_token');
            });
        }

        // Login form
        $('#login-form').addEventListener('submit', function (e) {
            e.preventDefault();
            var email = $('#login-email').value;
            var password = $('#login-password').value;
            var errEl = $('#login-error');
            hide(errEl);

            doLogin(email, password).then(function () {
                showDashboard();
                loadUserInfo();
            }).catch(function (err) {
                show(errEl);
                errEl.textContent = err.message;
            });
        });

        // Logout
        $('#logout-btn').addEventListener('click', doLogout);

        // Tabs
        $$('.admin-tab').forEach(function (btn) {
            btn.addEventListener('click', function () {
                loadTab(this.getAttribute('data-tab'));
            });
        });

        // Products — Add button
        $('#btn-add-product').addEventListener('click', function () {
            openProductModal(null);
        });

        // Products — Modal close / cancel
        $('#product-modal-close').addEventListener('click', function () { hide($('#product-modal')); });
        $('#product-modal-cancel').addEventListener('click', function () { hide($('#product-modal')); });

        // Products — Form submit
        $('#product-form').addEventListener('submit', saveProduct);

        // Products — Table action buttons (edit / delete / toggle)
        $('#products-table-body').addEventListener('click', function (e) {
            var btn = e.target.closest('[data-action]');
            if (!btn) return;
            var action = btn.getAttribute('data-action');
            var id = btn.getAttribute('data-id');

            if (action === 'delete') {
                deleteProduct(id);
            } else if (action === 'toggle-active') {
                toggleProductActive(id, btn.getAttribute('data-active'));
            } else if (action === 'edit') {
                var slug = btn.getAttribute('data-slug');
                api('GET', '/products/' + encodeURIComponent(slug)).then(function (p) {
                    openProductModal(p);
                }).catch(function (e) { toast('Error: ' + e.message); });
            }
        });

        // Products — Image file upload
        $('#pf-image-file').addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;
            var preview = $('#pf-image-preview');
            var reader = new FileReader();
            reader.onload = function (ev) {
                preview.innerHTML = '<img src="' + ev.target.result + '" style="width:100%;height:100%;object-fit:cover;">';
                show(preview);
            };
            reader.readAsDataURL(file);

            uploadImage(file, function (path) {
                $('#pf-image').value = path;
                toast('Image uploaded');
            });
        });

        // Orders — Filter
        $('#order-status-filter').addEventListener('change', function () {
            loadOrders(this.value);
        });

        // Orders — Table action buttons (view order)
        $('#orders-table-body').addEventListener('click', function (e) {
            var btn = e.target.closest('[data-action]');
            if (!btn) return;
            if (btn.getAttribute('data-action') === 'view-order') {
                openOrderModal(btn.getAttribute('data-id'));
            }
        });

        // Orders — Modal
        $('#order-modal-close').addEventListener('click', function () { hide($('#order-modal')); });
        $('#btn-update-status').addEventListener('click', updateOrderStatus);

        // Close modals on backdrop click
        $$('.admin-modal').forEach(function (modal) {
            modal.addEventListener('click', function (e) {
                if (e.target === modal) hide(modal);
            });
        });

        // Analytics — period change
        $('#analytics-revenue-period').addEventListener('change', function () { loadAnalytics(); });
    }

    // ── Analytics ─────────────────────────────────────────────────────────
    function loadAnalytics() {
        var days = parseInt($('#analytics-revenue-period').value) || 30;

        // Fetch overview + revenue + top products + recent orders in parallel
        Promise.all([
            api('GET', '/analytics/overview'),
            api('GET', '/analytics/revenue?days=' + days),
            api('GET', '/analytics/top-products?limit=5'),
            api('GET', '/analytics/recent-orders?limit=10')
        ]).then(function (results) {
            var overview = results[0];
            var revenue = results[1];
            var topProducts = results[2];
            var recentOrders = results[3];

            renderAnalyticsKPIs(overview);
            renderRevenueTable(revenue);
            renderTopProducts(topProducts);
            renderRecentOrders(recentOrders);
        }).catch(function (e) { toast('Analytics error: ' + e.message); });
    }

    function renderAnalyticsKPIs(data) {
        var kpis = $('#analytics-kpis');
        var status = data.orders_by_status || {};
        kpis.innerHTML =
            '<div class="kpi-card"><div class="kpi-value">' + data.total_orders + '</div><div class="kpi-label">Total Orders</div></div>' +
            '<div class="kpi-card"><div class="kpi-value">Rs. ' + Number(data.total_revenue).toLocaleString() + '</div><div class="kpi-label">Total Revenue</div></div>' +
            '<div class="kpi-card"><div class="kpi-value">' + data.total_customers + '</div><div class="kpi-label">Customers</div></div>' +
            '<div class="kpi-card"><div class="kpi-value">Rs. ' + Number(data.avg_order_value).toLocaleString() + '</div><div class="kpi-label">Avg Order Value</div></div>' +
            '<div class="kpi-card"><div class="kpi-value">' + data.total_products + '</div><div class="kpi-label">Products</div></div>' +
            '<div class="kpi-card"><div class="kpi-value">' + (status.pending || 0) + '</div><div class="kpi-label">Pending Orders</div></div>';
    }

    function renderRevenueTable(rows) {
        var el = $('#analytics-revenue-table');
        if (!rows || rows.length === 0) {
            el.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem;">No revenue data for this period.</p>';
            return;
        }
        var totalRev = rows.reduce(function (s, r) { return s + r.revenue; }, 0);
        var totalOrd = rows.reduce(function (s, r) { return s + r.order_count; }, 0);
        var html = '<table class="admin-table"><thead><tr><th>Date</th><th>Orders</th><th>Revenue (PKR)</th></tr></thead><tbody>';
        rows.forEach(function (r) {
            html += '<tr><td>' + r.date + '</td><td>' + r.order_count + '</td><td>' + Number(r.revenue).toLocaleString() + '</td></tr>';
        });
        html += '</tbody><tfoot><tr style="font-weight:bold;"><td>Total</td><td>' + totalOrd + '</td><td>' + Number(totalRev).toLocaleString() + '</td></tr></tfoot></table>';
        el.innerHTML = html;
    }

    function renderTopProducts(products) {
        var el = $('#analytics-top-products');
        if (!products || products.length === 0) {
            el.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem;">No sales data yet.</p>';
            return;
        }
        var html = '<table class="admin-table"><thead><tr><th>#</th><th>Product</th><th>Price</th><th>Sold</th><th>Revenue (PKR)</th></tr></thead><tbody>';
        products.forEach(function (p, i) {
            html += '<tr><td>' + (i + 1) + '</td><td>' + esc(p.name) + '</td><td>' + Number(p.price).toLocaleString() + '</td><td>' + p.total_sold + '</td><td>' + Number(p.total_revenue).toLocaleString() + '</td></tr>';
        });
        html += '</tbody></table>';
        el.innerHTML = html;
    }

    function renderRecentOrders(orders) {
        var el = $('#analytics-recent-orders');
        if (!orders || orders.length === 0) {
            el.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem;">No orders yet.</p>';
            return;
        }
        var html = '<table class="admin-table"><thead><tr><th>ID</th><th>Status</th><th>Total (PKR)</th><th>Items</th><th>Date</th></tr></thead><tbody>';
        orders.forEach(function (o) {
            var itemCount = o.items ? o.items.reduce(function (s, i) { return s + i.quantity; }, 0) : 0;
            var date = new Date(o.created_at).toLocaleDateString();
            html += '<tr><td>' + o.id + '</td><td><span class="status-badge status-' + o.status + '">' + o.status + '</span></td><td>' + Number(o.total).toLocaleString() + '</td><td>' + itemCount + '</td><td>' + date + '</td></tr>';
        });
        html += '</tbody></table>';
        el.innerHTML = html;
    }

    function loadUserInfo() {
        api('GET', '/auth/me').then(function (user) {
            $('#admin-email').textContent = user.email;
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();
