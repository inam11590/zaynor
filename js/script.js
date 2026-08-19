/* ==========================================================================
   ZAYNOR - Premium Men's Grooming Brand
   Custom JS Script
   ========================================================================== */

// Global Configuration
const CONFIG = {
    whatsappNumber: "923185868241",
    brandName: "ZAYNOR",
    apiBaseUrl: (location.hostname === "localhost" || location.hostname === "127.0.0.1" || !location.hostname)
        ? "http://127.0.0.1:8000/api/v1"
        : "https://zaynor-backend.onrender.com/api/v1"
};

// Category ID → slug mapping (matches backend database IDs)
const CATEGORY_ID_MAP = { 1: "perfumes", 2: "skincare" };

// Wishlist session key — persists across visits
function getWishlistSessionKey() {
    let key = localStorage.getItem("zaynor_session");
    if (!key) {
        key = "sess_" + Math.random().toString(36).substring(2) + Date.now().toString(36);
        localStorage.setItem("zaynor_session", key);
    }
    return key;
}

// Product Database (hardcoded fallback — used when API is unavailable)
const PRODUCTS = {
    perfumes: [
        {
            id: "perfume-monarch",
            name: "Monarch Intense",
            price: 4500,
            image: "images/perfumes/monarch.png",
            shortDescription: "A sophisticated blend of warm amber, royal oud, and smoky vetiver designed for the modern gentleman.",
            description: "Monarch Intense is our signature fragrance. Crafted for the modern Pakistani gentleman who commands presence, it blends rich traditional notes with contemporary sophistication. It opens with striking notes of fresh bergamot and pink pepper, transitioning into a warm heart of royal oud and cedarwood, and settles into an enduring, powerful base of amber, tobacco, and oakmoss.",
            specs: {
                "Longevity": "12+ Hours (Extrait de Parfum)",
                "Notes": "Amber, Royal Oud, Warm Leather, Vetiver",
                "Volume": "50 ml",
                "Best For": "Evening wear & formal occasions"
            }
        },
        {
            id: "perfume-obsidian",
            name: "Obsidian Oud",
            price: 4800,
            image: "images/perfumes/obsidian.png",
            shortDescription: "An enigmatic, deep fragrance centered around dark wood notes, premium musk, and spicy cardamom.",
            description: "Obsidian Oud is a mysterious and captivating fragrance, designed for those who appreciate the finer things in life. This scent is built around the raw, intense aroma of rare dark agarwood, accented by notes of freshly crushed cardamom, sweet vanilla pod, and rich sandalwood. It offers a warm, enveloping trail that leaves an unforgettable impression.",
            specs: {
                "Longevity": "10+ Hours (Extrait de Parfum)",
                "Notes": "Dark Agarwood, Premium Musk, Cardamom, Sandalwood",
                "Volume": "50 ml",
                "Best For": "Signature scent / All-season night"
            }
        },
        {
            id: "perfume-safari",
            name: "Royal Safari",
            price: 3800,
            image: "images/perfumes/safari.png",
            shortDescription: "A refreshing, long-lasting concentrated attar featuring fresh citrus, white musk, and patchouli.",
            description: "Royal Safari is a premium concentrated perfume oil (attar) that brings the freshness of the outdoors directly to your grooming routine. Starting with high-energy citrus notes of green mandarin and bergamot, it leads into a heart of fresh herbs and lavender, anchored by a premium base of patchouli, white musk, and soft cedar. Alcohol-free and skin-friendly.",
            specs: {
                "Longevity": "8-10 Hours (Concentrated Attar)",
                "Notes": "Green Mandarin, Lavender, White Musk, Patchouli",
                "Volume": "12 ml (Attar)",
                "Best For": "Day wear / Post-grooming freshness"
            }
        },
        {
            id: "perfume-kashmir-wood",
            name: "Kashmir Wood",
            price: 4200,
            image: "images/perfumes/monarch.png", // Reusing generated premium monarch image
            shortDescription: "A rich, woody fragrance inspired by the crisp pine forests and cedar valleys of Kashmir.",
            description: "Kashmir Wood captures the spirit of northern Pakistan. It's a crisp, green, and deeply woody fragrance that brings to life the clean air of pine forests and Himalayan cedar valleys. Hearty base notes of earth, wet soil, and pine resin are brightened by light top notes of cypress and wild juniper berry.",
            specs: {
                "Longevity": "8-10 Hours (Eau de Parfum)",
                "Notes": "Cypress, Juniper Berry, Himalayan Cedar, Wet Earth",
                "Volume": "50 ml",
                "Best For": "Day wear / Autumn & Winter"
            }
        },
        {
            id: "perfume-sultan-gold",
            name: "Sultan Gold",
            price: 4999,
            image: "images/perfumes/safari.png", // Reusing generated attar image
            shortDescription: "A warm, opulent perfume oil blending sweet honey, oriental spices, and aged white oud.",
            description: "Sultan Gold is a truly royal attar, crafted for special occasions. It is a dense, warm, and highly comforting blend. Notes of rich honey and roasted almonds interlace with Turkish rose and a base of fine aged white oud, rich amber, and vanilla. A classic unisex blend with intense projections.",
            specs: {
                "Longevity": "12-14 Hours (Concentrated Attar)",
                "Notes": "Honey, Spiced Almond, Turkish Rose, White Oud",
                "Volume": "12 ml (Attar)",
                "Best For": "Weddings / Special gatherings"
            }
        },
        {
            id: "perfume-lahore-night",
            name: "Lahore Nights",
            price: 4600,
            image: "images/perfumes/obsidian.png", // Reusing obsidian image
            shortDescription: "An alluring, sensual night-out perfume with spicy pink pepper, tonka bean, and tobacco.",
            description: "Lahore Nights is vibrant, electric, and full of life—much like the cultural heart of Pakistan. This fragrance is designed for unforgettable nights. Spicy top notes of pink pepper and ginger give way to a smooth, sweet heart of tonka bean and vanilla, settled on a strong base of golden honeyed tobacco leaf and dark vetiver.",
            specs: {
                "Longevity": "10+ Hours (Extrait de Parfum)",
                "Notes": "Pink Pepper, Tonka Bean, Sweet Tobacco, Vetiver",
                "Volume": "50 ml",
                "Best For": "Night outs / Street wear"
            }
        }
    ],
    skincare: [
        {
            id: "skin-charcoal-wash",
            name: "Activated Charcoal Face Wash",
            price: 1200,
            image: "images/skincare/facewash.png",
            shortDescription: "Deeply detoxifying face wash that lifts impurities, regulates sebum, and prevents breakouts.",
            description: "ZAYNOR Activated Charcoal Face Wash is engineered specifically for men's thicker, oilier skin. Formulated with premium activated charcoal beads, it acts like a magnet to extract deep-seated dirt, pollution particles, and excess oils. Enriched with natural Aloe Vera and tea tree extracts to soothe skin and prevent acne without stripping natural moisture.",
            specs: {
                "Skin Type": "Oily, Acne-Prone & Combination Skin",
                "Key Ingredients": "Activated Charcoal, Tea Tree Oil, Aloe Vera Extract",
                "Volume": "150 ml",
                "Usage": "Twice daily (Morning & Night)"
            }
        },
        {
            id: "skin-hyaluronic-serum",
            name: "Elixir Hydrating Serum",
            price: 1850,
            image: "images/skincare/serum.png",
            shortDescription: "Advanced Hyaluronic Acid & Vitamin B5 serum for intense hydration and plump, youthful skin.",
            description: "Our Elixir Hydrating Serum is a lightweight, non-greasy formula that penetrates deep into skin layers. It combines multi-weight Hyaluronic Acid molecules with Vitamin B5 (Panthenol) to lock in hydration, smooth out fine lines, and rebuild skin barriers damaged by shaving, pollution, or sun exposure. Instantly refreshes tired skin.",
            specs: {
                "Skin Type": "All Skin Types (highly recommended for dry/dull skin)",
                "Key Ingredients": "Hyaluronic Acid (2%), Vitamin B5, Green Tea Extract",
                "Volume": "30 ml",
                "Usage": "3-4 drops daily on clean, damp skin"
            }
        },
        {
            id: "skin-beard-oil",
            name: "Royal Beard Growth Oil",
            price: 1500,
            image: "images/skincare/serum.png", // Reusing dropper bottle image
            shortDescription: "Premium blend of organic oils to soften hair, soothe itchy skin, and promote beard growth.",
            description: "ZAYNOR Beard Growth Oil is a premium elixir containing cold-pressed organic jojoba, argan, and sweet almond oils. Specially formulated to nourish hair follicles, eliminate 'beard dandruff', soothe dry skin, and stimulate healthy beard growth. Infused with a light signature scent of cedar and citrus that stays all day.",
            specs: {
                "Hair Type": "All Beard Types & Lengths",
                "Key Ingredients": "Jojoba Oil, Moroccan Argan Oil, Sweet Almond Oil, Cedarwood",
                "Volume": "30 ml",
                "Usage": "Once daily after shower (3-5 drops)"
            }
        },
        {
            id: "skin-clay-mask",
            name: "Himalayan Mineral Clay Mask",
            price: 1600,
            image: "images/skincare/facewash.png", // Reusing tube image
            shortDescription: "Purifying clay mask that shrinks pores, controls shine, and brightens skin tone.",
            description: "This mineral-rich clay mask draws out toxins from deep within the skin. Utilizing pure bentonite clay sourced from the foothill minerals of the Himalayas, combined with kaolin clay and soothing eucalyptus leaf oil. It effectively shrinks dilated pores, controls greasy shine, and improves skin texture for an instant brightened complexion.",
            specs: {
                "Skin Type": "Oily & Congested Skin",
                "Key Ingredients": "Himalayan Bentonite Clay, Kaolin, Eucalyptus Oil",
                "Volume": "100 g",
                "Usage": "1-2 times weekly (Leave on for 10 minutes)"
            }
        },
        {
            id: "skin-moisturizer",
            name: "Hydro-Boost Gel Cream",
            price: 1950,
            image: "images/skincare/serum.png", // Reusing serum image
            shortDescription: "Ultra-lightweight oil-free face moisturizer that absorbs instantly for 24-hour hydration.",
            description: "ZAYNOR Hydro-Boost is an oil-free, gel-based moisturizer designed specifically for men who hate the sticky feeling of traditional creams. Formulated with cooling Cucumber water, Niacinamide, and Centella Asiatica (Cica). It repairs the skin barrier, reduces redness from razor burns, and keeps skin matte yet thoroughly hydrated all day.",
            specs: {
                "Skin Type": "Normal, Oily, and Combination Skin",
                "Key Ingredients": "Niacinamide, Centella Asiatica, Cucumber Hydrosol",
                "Volume": "50 ml",
                "Usage": "Apply twice daily on clean face and neck"
            }
        },
        {
            id: "skin-acne-toner",
            name: "Salicylic Acid Clarifying Toner",
            price: 1400,
            image: "images/skincare/facewash.png", // Reusing wash image
            shortDescription: "Gently exfoliating toner containing 2% BHA to clear blackheads and prevent acne.",
            description: "Our clarifying toner features 2% Salicylic Acid (BHA), a fat-soluble acid that penetrates deep into pores to dissolve oil clogs, dead skin cells, and blackheads. Blended with witch hazel and chamomile extract to calm irritation and keep skin fresh, clear, and perfectly balanced.",
            specs: {
                "Skin Type": "Acne-Prone & Highly Congested Skin",
                "Key Ingredients": "Salicylic Acid (BHA 2%), Witch Hazel, Chamomile Extract",
                "Volume": "120 ml",
                "Usage": "Apply with cotton pad once daily at night"
            }
        }
    ]
};

/**
 * Fetches products from the backend API and returns a PRODUCTS-compatible object.
 * Returns null if the API is unavailable.
 *
 * Flow:
 *   1. GET /api/v1/products/ → get list of all products (summary)
 *   2. For each product, GET /api/v1/products/{slug} → get full details
 *   3. Map API data to the format the frontend expects
 *   4. Organize by category slug
 */
async function fetchProductsFromAPI() {
    if (!CONFIG.apiBaseUrl) return null;

    try {
        // Step 1: Get the product list
        const listRes = await fetch(`${CONFIG.apiBaseUrl}/products/`);
        if (!listRes.ok) return null;
        const summaryList = await listRes.json();

        // Step 2: Fetch full details for each product
        const fullProducts = await Promise.all(
            summaryList.map(async (summary) => {
                try {
                    const res = await fetch(`${CONFIG.apiBaseUrl}/products/${summary.slug}`);
                    if (!res.ok) return null;
                    return await res.json();
                } catch {
                    return null;
                }
            })
        );

        // Step 3: Filter out any failures and map to frontend format
        const valid = fullProducts.filter(Boolean);
        if (valid.length === 0) return null;

        const result = { perfumes: [], skincare: [] };

        valid.forEach((p) => {
            const slug = CATEGORY_ID_MAP[p.category_id] || "perfumes";
            const mapped = {
                id: p.slug,                         // use slug as the frontend ID
                backendId: p.id,                    // numeric ID for reviews API
                name: p.name,
                price: p.price,
                image: p.image,
                shortDescription: p.short_description,
                description: p.description,
                specs: p.specs || {}
            };

            if (result[slug]) {
                result[slug].push(mapped);
            }
        });

        return result;
    } catch (err) {
        // API is unreachable — fall back to hardcoded data
        return null;
    }
}

// Document Ready
document.addEventListener("DOMContentLoaded", () => {
    // 1. Sticky Navigation Scroll Handler
    const header = document.querySelector(".header");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            header.classList.add("header-scrolled");
        } else {
            header.classList.remove("header-scrolled");
        }
    });

    // 2. Mobile Menu — Only on screens ≤ 768 px
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu   = document.querySelector(".nav-menu"); // desktop nav — left untouched

    if (navToggle && navMenu && window.innerWidth <= 768) {

        // ── 1. Overlay backdrop ──────────────────────────────────────────
        const overlay = document.createElement("div");
        overlay.className = "nav-overlay";
        document.body.appendChild(overlay);

        // ── 2. Build the mobile drawer (separate element, not nav-menu) ──
        const drawer = document.createElement("nav");
        drawer.className = "mobile-drawer";
        drawer.setAttribute("aria-label", "Mobile Navigation");

        // Read page's active link to mirror it in the drawer
        const activePath = window.location.pathname.split("/").pop() || "index.html";

        const pages = [
            { href: "index.html",    label: "Home" },
            { href: "perfumes.html", label: "Perfumes" },
            { href: "skincare.html", label: "Skin Care" },
            { href: "wishlist.html", label: "Wishlist" },
            { href: "about.html",    label: "About" },
            { href: "contact.html",  label: "Contact" },
            { href: "tracking.html", label: "Track Order" },
        ];

        const linksHTML = pages.map(p => {
            const isActive = activePath === p.href || (activePath === "" && p.href === "index.html");
            return `<li><a href="${p.href}" class="nav-link${isActive ? " active" : ""}">${p.label}</a></li>`;
        }).join("");

        drawer.innerHTML = `
            <div class="drawer-header">
                <span class="drawer-brand">ZAYNOR<span>.</span></span>
                <button class="drawer-close" aria-label="Close menu" id="drawerCloseBtn">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
            <ul class="drawer-links">${linksHTML}</ul>
            <div class="drawer-footer">
                <p>ZAYNOR Premium Grooming</p>
                <a href="https://wa.me/${CONFIG.whatsappNumber}" target="_blank" rel="noopener noreferrer" class="drawer-wa-link">
                    <svg viewBox="0 0 24 24">
                        <path d="M12.012 2c-5.506 0-9.989 4.478-9.99 9.984a9.96 9.96 0 001.333 4.993L2 22l5.13-1.347a9.96 9.96 0 004.887 1.28h.005c5.505 0 9.988-4.478 9.989-9.985 0-2.67-1.037-5.18-2.92-7.065A9.925 9.925 0 0012.012 2zm5.836 14.166c-.32.902-1.854 1.764-2.556 1.87-.62.093-1.428.167-3.953-.878-3.23-1.336-5.307-4.636-5.468-4.85-.162-.216-1.309-1.742-1.309-3.324 0-1.583.826-2.36 1.118-2.667.29-.307.64-.384.85-.384.214 0 .429.002.617.01.196.009.46-.073.722.56.268.647.915 2.233.996 2.395.08.162.133.35.026.565-.107.214-.16.347-.32.532-.162.185-.34.409-.485.55-.16.155-.328.324-.143.642.185.318.824 1.354 1.766 2.195 1.21 1.08 2.227 1.414 2.549 1.575.322.161.51.134.7-.082.19-.217.825-.96.105-1.285-.246-.108-.396-.188-1.578-.667-.322-.132-.538-.066-.7.13-.16.195-.627.785-.77 0-.142-.785-.286-1.547-.63-.162-.317-.324-.633-.143-.951z"/>
                    </svg>
                    Order on WhatsApp
                </a>
            </div>`;

        document.body.appendChild(drawer);

        // ── 3. Open / close helpers ───────────────────────────────────────
        const openDrawer = () => {
            drawer.classList.add("open");
            overlay.classList.add("active");
            navToggle.setAttribute("aria-expanded", "true");
            navToggle.style.opacity = "0";          // hide hamburger while drawer is open
            navToggle.style.pointerEvents = "none";
            document.body.style.overflow = "hidden";
        };

        const closeDrawer = () => {
            drawer.classList.remove("open");
            overlay.classList.remove("active");
            navToggle.setAttribute("aria-expanded", "false");
            navToggle.style.opacity = "1";          // restore hamburger
            navToggle.style.pointerEvents = "";
            document.body.style.overflow = "";
        };

        // ── 4. Wire up events ─────────────────────────────────────────────
        navToggle.addEventListener("click", () => {
            drawer.classList.contains("open") ? closeDrawer() : openDrawer();
        });

        drawer.querySelector("#drawerCloseBtn").addEventListener("click", closeDrawer);
        overlay.addEventListener("click", closeDrawer);

        document.addEventListener("keydown", e => {
            if (e.key === "Escape" && drawer.classList.contains("open")) closeDrawer();
        });

        // Close on any nav link tap
        drawer.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", closeDrawer);
        });
    }


    // 3. Dynamic Products Grid Initialization (if container is present on page)
    //    Tries the backend API first; falls back to hardcoded PRODUCTS on failure.
    initProductGrids();

    // 4. Modal Setup & Events
    initModal();

    // 5. Contact Form Submission
    initContactForm();

    // 6. Newsletter Subscription
    initNewsletterForm();

    // 7. Load wishlist heart states
    refreshWishlistHearts();
});

/**
 * Initializes and dynamically loads products to perfume and skincare pages.
 * Tries the backend API first; falls back to hardcoded PRODUCTS on failure.
 */
function initProductGrids() {
    const perfumeGrid = document.getElementById("perfumes-grid");
    const skincareGrid = document.getElementById("skincare-grid");
    const featuredGrid = document.getElementById("featured-grid");

    // No product grids on this page — nothing to do
    if (!perfumeGrid && !skincareGrid && !featuredGrid) return;

    // Helper: render grids from a PRODUCTS-compatible object
    function renderFromProducts(products) {
        if (perfumeGrid) {
            perfumeGrid.innerHTML = products.perfumes.map(p => generateProductCardHTML(p, "perfumes")).join("");
        }
        if (skincareGrid) {
            skincareGrid.innerHTML = products.skincare.map(p => generateProductCardHTML(p, "skincare")).join("");
        }
        if (featuredGrid) {
            const featuredList = [
                { ...products.perfumes[0], cat: "perfumes", badge: "Best Seller" },
                { ...products.skincare[0], cat: "skincare", badge: "New Arrival" },
                { ...products.perfumes[1], cat: "perfumes", badge: "Premium Choice" },
                { ...products.skincare[1], cat: "skincare", badge: "Must Have" }
            ];
            featuredGrid.innerHTML = featuredList.map(p => generateProductCardHTML(p, p.cat, p.badge)).join("");
        }
    }

    // Try API first, fall back to hardcoded PRODUCTS
    fetchProductsFromAPI().then(apiProducts => {
        if (apiProducts && (apiProducts.perfumes.length > 0 || apiProducts.skincare.length > 0)) {
            // Store API products globally so the modal can look them up
            window._API_PRODUCTS = apiProducts;
            renderFromProducts(apiProducts);
        } else {
            // API unavailable — use hardcoded data
            renderFromProducts(PRODUCTS);
        }
    });
}

/**
 * Helper to build product card HTML markup
 */
function generateProductCardHTML(product, category, badge = "") {
    const badgeHTML = badge ? `<div class="product-badge">${badge}</div>` : '';
    const formattedPrice = Number(product.price).toLocaleString("en-PK");
    
    return `
        <article class="product-card" data-id="${product.id}" data-category="${category}">
            <div class="product-image-container" onclick="openProductModal('${product.id}', '${category}')">
                ${badgeHTML}
                <img src="${product.image}" alt="${product.name}" class="product-image" loading="lazy">
                <button class="wishlist-heart" data-slug="${product.id}" onclick="event.stopPropagation(); toggleWishlist('${product.id}', this);" aria-label="Add to wishlist">&#9825;</button>
                <div class="product-quickview">Quick View</div>
            </div>
            <div class="product-details">
                <h3 class="product-title">${product.name}</h3>
                <div class="product-meta">
                    <span class="product-price">Rs. ${formattedPrice}</span>
                </div>
                <p class="product-description">${product.shortDescription}</p>
                <div class="product-actions">
                    <a href="${getWhatsAppOrderLink(product)}" target="_blank" class="btn btn-whatsapp btn-small btn-full">
                        <svg class="icon" viewBox="0 0 24 24" style="margin-right: 5px;">
                            <path d="M12.012 2c-5.506 0-9.989 4.478-9.99 9.984a9.96 9.96 0 001.333 4.993L2 22l5.13-1.347a9.96 9.96 0 004.887 1.28h.005c5.505 0 9.988-4.478 9.989-9.985 0-2.67-1.037-5.18-2.92-7.065A9.925 9.925 0 0012.012 2zm5.836 14.166c-.32.902-1.854 1.764-2.556 1.87-.62.093-1.428.167-3.953-.878-3.23-1.336-5.307-4.636-5.468-4.85-.162-.216-1.309-1.742-1.309-3.324 0-1.583.826-2.36 1.118-2.667.29-.307.64-.384.85-.384.214 0 .429.002.617.01.196.009.46-.073.722.56.268.647.915 2.233.996 2.395.08.162.133.35.026.565-.107.214-.16.347-.32.532-.162.185-.34.409-.485.55-.16.155-.328.324-.143.642.185.318.824 1.354 1.766 2.195 1.21 1.08 2.227 1.414 2.549 1.575.322.161.51.134.7-.082.19-.217.825-.96.105-1.285-.246-.108-.396-.188-1.578-.667-.322-.132-.538-.066-.7.13-.16.195-.627.785-.77 0-.142-.785-.286-1.547-.63-.162-.317-.324-.633-.143-.951z"/>
                        </svg>
                        Order on WhatsApp
                    </a>
                </div>
            </div>
        </article>
    `;
}

/**
 * Returns formatted WhatsApp wa.me link for a product order
 */
function getWhatsAppOrderLink(product, coupon) {
    const formattedPrice = Number(product.price).toLocaleString("en-PK");
    let textMessage = `Assalam-o-Alaikum ${CONFIG.brandName},\n\nI would like to order the following product:\n\n*Product Name:* ${product.name}\n*Price:* Rs. ${formattedPrice}`;
    if (coupon && coupon.valid) {
        textMessage += `\n\n*Coupon:* ${coupon.code} (${coupon.discount_percent}% off)`;
        textMessage += `\n*Discount:* Rs. ${coupon.discount_amount.toLocaleString("en-PK")}`;
        textMessage += `\n*Final Price:* Rs. ${coupon.final_amount.toLocaleString("en-PK")}`;
    }
    textMessage += `\n\nPlease let me know the details to confirm my order. Thank you!`;
    return `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(textMessage)}`;
}

/**
 * Apply a coupon code to the current modal product.
 */
function applyCoupon(product, code, msgEl) {
    if (!code) { msgEl.style.color = "#e74c3c"; msgEl.textContent = "Please enter a coupon code."; return; }
    if (!CONFIG.apiBaseUrl) { msgEl.style.color = "#e74c3c"; msgEl.textContent = "API unavailable."; return; }

    msgEl.style.color = "var(--text-secondary)";
    msgEl.textContent = "Checking...";

    fetch(`${CONFIG.apiBaseUrl}/coupons/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: code.toUpperCase(), order_amount: product.price })
    })
    .then(r => { if (!r.ok) throw new Error("not found"); return r.json(); })
    .then(data => {
        const modal = document.getElementById("product-modal");
        if (data.valid) {
            msgEl.style.color = "#2ecc71";
            msgEl.textContent = data.message + ` — You save Rs. ${data.discount_amount.toLocaleString("en-PK")}`;
            modal.querySelector(".modal-price").innerHTML =
                `<span style="text-decoration:line-through;color:var(--text-secondary);font-size:0.9em;">Rs. ${Number(product.price).toLocaleString("en-PK")}</span> ` +
                `<span style="color:#2ecc71;">Rs. ${data.final_amount.toLocaleString("en-PK")}</span>`;
            modal._appliedCoupon = data;
            // Update WhatsApp link with coupon
            modal.querySelector(".modal-order-btn").href = getWhatsAppOrderLink(product, data);
        } else {
            msgEl.style.color = "#e74c3c";
            msgEl.textContent = data.message;
            modal._appliedCoupon = null;
            modal.querySelector(".modal-price").innerText = `Rs. ${Number(product.price).toLocaleString("en-PK")}`;
            modal.querySelector(".modal-order-btn").href = getWhatsAppOrderLink(product, null);
        }
    })
    .catch(() => {
        msgEl.style.color = "#e74c3c";
        msgEl.textContent = "Coupon not found.";
    });
}

/**
 * Fetches and renders reviews for a product in the modal.
 */
function loadReviews(productId, container) {
    const apiBase = CONFIG.apiBaseUrl;
    if (!apiBase) { container.innerHTML = ""; return; }

    // Fetch summary + reviews in parallel
    Promise.all([
        fetch(`${apiBase}/reviews/summary?product_id=${productId}`).then(r => r.ok ? r.json() : null),
        fetch(`${apiBase}/reviews/?product_id=${productId}`).then(r => r.ok ? r.json() : null)
    ]).then(([summary, reviews]) => {
        let html = '';

        // Rating summary
        if (summary && summary.review_count > 0) {
            const stars = renderStars(summary.average_rating);
            html += `<div class="reviews-summary" style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
                <span style="font-size:1.5rem;font-weight:700;color:var(--gold-primary);">${summary.average_rating}</span>
                <span>${stars}</span>
                <span style="color:var(--text-secondary);font-size:0.85rem;">(${summary.review_count} review${summary.review_count !== 1 ? 's' : ''})</span>
            </div>`;
        }

        // Reviews list
        if (reviews && reviews.length > 0) {
            html += '<div class="reviews-list">';
            reviews.forEach(r => {
                const date = new Date(r.created_at).toLocaleDateString();
                html += `<div style="border-top:1px solid var(--border-light);padding:0.75rem 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
                        <strong style="color:var(--text-primary);font-size:0.9rem;">${escHTML(r.customer_name)}</strong>
                        <span style="color:var(--text-secondary);font-size:0.75rem;">${date}</span>
                    </div>
                    <div style="margin-bottom:0.25rem;">${renderStars(r.rating)}</div>
                    ${r.comment ? `<p style="color:var(--text-secondary);font-size:0.85rem;margin:0;">${escHTML(r.comment)}</p>` : ''}
                </div>`;
            });
            html += '</div>';
        }

        // Review form
        html += `<div style="border-top:1px solid var(--border-light);padding-top:1rem;margin-top:0.75rem;">
            <h4 style="font-family:var(--font-heading);font-size:1rem;color:var(--text-primary);margin-bottom:0.75rem;">Write a Review</h4>
            <form id="review-form" style="display:flex;flex-direction:column;gap:0.75rem;">
                <input type="text" id="review-name" placeholder="Your name" required style="padding:0.5rem 0.75rem;background:var(--bg-tertiary);border:1px solid var(--border-light);border-radius:6px;color:var(--text-primary);font-family:var(--font-body);font-size:0.85rem;">
                <select id="review-rating" required style="padding:0.5rem 0.75rem;background:var(--bg-tertiary);border:1px solid var(--border-light);border-radius:6px;color:var(--text-primary);font-family:var(--font-body);font-size:0.85rem;">
                    <option value="">Rate this product</option>
                    <option value="5">5 - Excellent</option>
                    <option value="4">4 - Very Good</option>
                    <option value="3">3 - Good</option>
                    <option value="2">2 - Fair</option>
                    <option value="1">1 - Poor</option>
                </select>
                <textarea id="review-comment" rows="2" placeholder="Your review (optional)" style="padding:0.5rem 0.75rem;background:var(--bg-tertiary);border:1px solid var(--border-light);border-radius:6px;color:var(--text-primary);font-family:var(--font-body);font-size:0.85rem;resize:vertical;"></textarea>
                <div id="review-form-msg" style="font-size:0.8rem;"></div>
                <button type="submit" class="btn btn-primary btn-small" style="align-self:flex-start;">Submit Review</button>
            </form>
        </div>`;

        container.innerHTML = html;

        // Bind review form submission
        const form = container.querySelector('#review-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                submitReview(productId, container);
            });
        }
    }).catch(() => {
        container.innerHTML = "";
    });
}

function renderStars(rating) {
    let html = '';
    for (let i = 1; i <= 5; i++) {
        html += i <= Math.round(rating)
            ? '<span style="color:#f1c40f;font-size:0.9rem;">&#9733;</span>'
            : '<span style="color:var(--border-light);font-size:0.9rem;">&#9733;</span>';
    }
    return html;
}

function escHTML(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

function submitReview(productId, container) {
    const name = document.getElementById('review-name').value.trim();
    const rating = document.getElementById('review-rating').value;
    const comment = document.getElementById('review-comment').value.trim();
    const msgEl = document.getElementById('review-form-msg');

    if (!name || !rating) {
        msgEl.style.color = '#e74c3c';
        msgEl.textContent = 'Please enter your name and select a rating.';
        return;
    }

    const apiBase = CONFIG.apiBaseUrl;
    fetch(`${apiBase}/reviews/?product_id=${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_name: name, rating: parseInt(rating), comment: comment || null })
    }).then(r => {
        if (!r.ok) throw new Error('Failed');
        msgEl.style.color = '#2ecc71';
        msgEl.textContent = 'Thank you for your review!';
        loadReviews(productId, container);
    }).catch(() => {
        msgEl.style.color = '#e74c3c';
        msgEl.textContent = 'Could not submit review. Try again.';
    });
}

/**
 * Setup and controller for product details modal
 */
function initModal() {
    const modal = document.getElementById("product-modal");
    if (!modal) return;

    const closeBtn = modal.querySelector(".modal-close");
    const backdrop = modal.querySelector(".modal-backdrop");

    // Helper to close modal
    const closeModal = () => {
        modal.classList.remove("open");
        setTimeout(() => {
            modal.style.display = "none";
            document.body.style.overflow = ""; // Enable body scroll
        }, 300);
    };

    closeBtn.addEventListener("click", closeModal);
    backdrop.addEventListener("click", closeModal);

    // Escape Key listener
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal.classList.contains("open")) {
            closeModal();
        }
    });

    // Attach to global window object so it can be called from inline onclick events
    window.openProductModal = (productId, category) => {
        // Prefer API products if available, otherwise use hardcoded
        const source = (window._API_PRODUCTS && window._API_PRODUCTS[category])
            ? window._API_PRODUCTS
            : PRODUCTS;

        const productList = source[category];
        if (!productList) return;

        const product = productList.find(p => p.id === productId);
        if (!product) return;

        // Populate Modal Fields
        modal.querySelector(".modal-image").src = product.image;
        modal.querySelector(".modal-image").alt = product.name;
        modal.querySelector(".modal-title").innerText = product.name;
        modal.querySelector(".modal-category").innerText = category === "perfumes" ? "Fragrance / Attar" : "Premium Skin Care";
        modal.querySelector(".modal-price").innerText = `Rs. ${Number(product.price).toLocaleString("en-PK")}`;
        modal.querySelector(".modal-description").innerText = product.description;

        // Specifications Grid
        const specGrid = modal.querySelector(".modal-spec-grid");
        specGrid.innerHTML = Object.entries(product.specs).map(([key, value]) => `
            <div class="modal-spec-item">
                <div class="modal-spec-label">${key}</div>
                <div class="modal-spec-value">${value}</div>
            </div>
        `).join("");

        // Coupon section — inject if not already present
        let couponSection = modal.querySelector(".modal-coupon");
        if (!couponSection) {
            couponSection = document.createElement("div");
            couponSection.className = "modal-coupon";
            const specGridInner = modal.querySelector(".modal-spec-grid");
            specGridInner.parentNode.insertBefore(couponSection, specGridInner.nextSibling);
        }
        couponSection.innerHTML = `
            <div style="display:flex;gap:0.5rem;margin-top:1rem;">
                <input type="text" id="coupon-input" placeholder="Have a coupon code?" style="flex:1;padding:0.5rem 0.75rem;background:var(--bg-tertiary);border:1px solid var(--border-light);border-radius:6px;color:var(--text-primary);font-family:var(--font-body);font-size:0.85rem;text-transform:uppercase;">
                <button id="coupon-apply-btn" class="btn btn-outline btn-small" style="white-space:nowrap;">Apply</button>
            </div>
            <div id="coupon-msg" style="font-size:0.8rem;margin-top:0.4rem;"></div>
        `;

        const couponApplyBtn = couponSection.querySelector("#coupon-apply-btn");
        const couponInput = couponSection.querySelector("#coupon-input");
        const couponMsg = couponSection.querySelector("#coupon-msg");
        couponApplyBtn.addEventListener("click", function () {
            applyCoupon(product, couponInput.value.trim(), couponMsg);
        });
        couponInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") { e.preventDefault(); applyCoupon(product, couponInput.value.trim(), couponMsg); }
        });
        // Reset any previous coupon state
        modal._appliedCoupon = null;
        modal.querySelector(".modal-price").innerText = `Rs. ${Number(product.price).toLocaleString("en-PK")}`;

        // WhatsApp CTA Config
        const orderButton = modal.querySelector(".modal-order-btn");
        orderButton.href = getWhatsAppOrderLink(product);

        // Wishlist button in modal
        let wishlistBtn = modal.querySelector(".modal-wishlist-btn");
        if (!wishlistBtn) {
            wishlistBtn = document.createElement("button");
            wishlistBtn.className = "btn btn-outline btn-small modal-wishlist-btn";
            wishlistBtn.style.marginTop = "0.75rem";
            wishlistBtn.style.width = "100%";
            wishlistBtn.style.textAlign = "center";
            orderButton.parentNode.insertBefore(wishlistBtn, orderButton.nextSibling);
        }
        wishlistBtn.setAttribute("data-slug", product.id);
        checkWishlistStatus(product.id, wishlistBtn);

        // Reviews Section — inject if not already present
        let reviewsSection = modal.querySelector(".modal-reviews");
        if (!reviewsSection) {
            reviewsSection = document.createElement("div");
            reviewsSection.className = "modal-reviews";
            const specGrid = modal.querySelector(".modal-spec-grid");
            specGrid.parentNode.insertBefore(reviewsSection, specGrid.nextSibling);
        }

        // Load reviews from API if backendId is available
        if (product.backendId && CONFIG.apiBaseUrl) {
            reviewsSection.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem;">Loading reviews...</p>';
            loadReviews(product.backendId, reviewsSection);
        } else {
            reviewsSection.innerHTML = "";
        }

        // Open animation
        modal.style.display = "flex";
        document.body.style.overflow = "hidden"; // Disable background scrolling
        setTimeout(() => {
            modal.classList.add("open");
        }, 10);
    };
}

/**
 * Handle Contact Page Form Submission
 */
function initContactForm() {
    const contactForm = document.getElementById("contact-form");
    if (!contactForm) return;

    contactForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const name = document.getElementById("contact-name").value.trim();
        const email = document.getElementById("contact-email").value.trim();
        const subject = document.getElementById("contact-subject").value.trim();
        const message = document.getElementById("contact-message").value.trim();

        if (!name || !email || !message) {
            showToast("Please fill in all required fields.");
            return;
        }

        // Generate contact request WhatsApp text
        const textMessage = `Assalam-o-Alaikum ${CONFIG.brandName},\n\nI have a general inquiry:\n\n*Name:* ${name}\n*Email:* ${email}\n*Subject:* ${subject || "General Inquiry"}\n*Message:* ${message}`;
        const whatsappLink = `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(textMessage)}`;

        // Open in new tab
        window.open(whatsappLink, "_blank");
        
        // Show confirmation toast and reset form
        showToast("Message prepared! Opening WhatsApp...");
        contactForm.reset();
    });
}

/**
 * Handle Newsletter form submit placeholder
 */
function initNewsletterForm() {
    const forms = document.querySelectorAll(".newsletter-form");
    forms.forEach(form => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const input = form.querySelector(".newsletter-input");
            if (input && input.value.trim()) {
                showToast("Thank you for subscribing to ZAYNOR!");
                input.value = "";
            }
        });
    });
}

/**
 * Toast Notification system helper
 */
function showToast(message) {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Show slide-in animation
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    // Dismiss toast after 3.5 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 3500);
}

/**
 * Toggle a product in the wishlist (add/remove).
 */
function toggleWishlist(slug, btnEl) {
    const apiBase = CONFIG.apiBaseUrl;
    if (!apiBase) return;

    const sessionKey = getWishlistSessionKey();
    const isInWishlist = btnEl.classList.contains("active");

    if (isInWishlist) {
        fetch(`${apiBase}/wishlist/${encodeURIComponent(slug)}?session_key=${encodeURIComponent(sessionKey)}`, { method: "DELETE" })
            .then(() => {
                btnEl.classList.remove("active");
                btnEl.innerHTML = "&#9825;";
                showToast("Removed from wishlist");
            });
    } else {
        fetch(`${apiBase}/wishlist/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_key: sessionKey, product_slug: slug })
        })
        .then(r => r.ok ? r.json() : null)
        .then(() => {
            btnEl.classList.add("active");
            btnEl.innerHTML = "&#9829;";
            showToast("Added to wishlist!");
        });
    }
}

/**
 * Check if a product is in the wishlist and update button state.
 */
function checkWishlistStatus(slug, btnEl) {
    const apiBase = CONFIG.apiBaseUrl;
    if (!apiBase) return;

    const sessionKey = getWishlistSessionKey();
    fetch(`${apiBase}/wishlist/check?session_key=${encodeURIComponent(sessionKey)}&product_slug=${encodeURIComponent(slug)}`)
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (data && data.in_wishlist) {
                btnEl.classList.add("active");
                btnEl.innerHTML = "&#9829;";
            } else {
                btnEl.classList.remove("active");
                btnEl.innerHTML = "&#9825;";
            }
            btnEl.onclick = function(e) { e.stopPropagation(); toggleWishlist(slug, btnEl); };
        });
}

/**
 * Load and update all wishlist heart buttons on the page.
 */
function refreshWishlistHearts() {
    const apiBase = CONFIG.apiBaseUrl;
    if (!apiBase) return;

    const sessionKey = getWishlistSessionKey();
    fetch(`${apiBase}/wishlist/?session_key=${encodeURIComponent(sessionKey)}`)
        .then(r => r.ok ? r.json() : null)
        .then(items => {
            if (!items) return;
            const slugs = new Set(items.map(i => i.product_slug));
            document.querySelectorAll(".wishlist-heart").forEach(btn => {
                const slug = btn.getAttribute("data-slug");
                if (slugs.has(slug)) {
                    btn.classList.add("active");
                    btn.innerHTML = "&#9829;";
                }
            });
        });
}

/**
 * Inject and initialize the Scroll-to-Top button (injected via JS so it works on every page)
 */
(function initScrollTop() {
    const btn = document.createElement("button");
    btn.className = "scroll-top";
    btn.setAttribute("aria-label", "Scroll back to top");
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/></svg>`;
    document.body.appendChild(btn);

    window.addEventListener("scroll", () => {
        if (window.scrollY > 400) {
            btn.classList.add("visible");
        } else {
            btn.classList.remove("visible");
        }
    });

    btn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
})();

/**
 * Inject a floating WhatsApp CTA button on every page
 */
(function initWhatsAppFloat() {
    const link = document.createElement("a");
    link.className = "whatsapp-float";
    link.href = `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent("Assalam-o-Alaikum ZAYNOR! I'd like to know more about your products.")}`;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Chat with us on WhatsApp");
    link.innerHTML = `
        <svg viewBox="0 0 24 24">
            <path d="M12.012 2c-5.506 0-9.989 4.478-9.99 9.984a9.96 9.96 0 001.333 4.993L2 22l5.13-1.347a9.96 9.96 0 004.887 1.28h.005c5.505 0 9.988-4.478 9.989-9.985 0-2.67-1.037-5.18-2.92-7.065A9.925 9.925 0 0012.012 2zm5.836 14.166c-.32.902-1.854 1.764-2.556 1.87-.62.093-1.428.167-3.953-.878-3.23-1.336-5.307-4.636-5.468-4.85-.162-.216-1.309-1.742-1.309-3.324 0-1.583.826-2.36 1.118-2.667.29-.307.64-.384.85-.384.214 0 .429.002.617.01.196.009.46-.073.722.56.268.647.915 2.233.996 2.395.08.162.133.35.026.565-.107.214-.16.347-.32.532-.162.185-.34.409-.485.55-.16.155-.328.324-.143.642.185.318.824 1.354 1.766 2.195 1.21 1.08 2.227 1.414 2.549 1.575.322.161.51.134.7-.082.19-.217.825-.96.105-1.285-.246-.108-.396-.188-1.578-.667-.322-.132-.538-.066-.7.13-.16.195-.627.785-.77 0-.142-.785-.286-1.547-.63-.162-.317-.324-.633-.143-.951z"/>
        </svg>
    `;
    document.body.appendChild(link);
})();

