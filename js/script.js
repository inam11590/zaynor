/* ==========================================================================
   ZAYNOR - Premium Men's Grooming Brand
   Custom JS Script
   ========================================================================== */

// Global Configuration
const CONFIG = {
    whatsappNumber: "923000000000", // Replace with your real Pakistani WhatsApp number (e.g., "923XXXXXXXXX")
    brandName: "ZAYNOR"
};

// Product Database
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

    // 2. Mobile Menu Toggling
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu = document.querySelector(".nav-menu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navToggle.classList.toggle("open");
            navMenu.classList.toggle("open");
        });

        // Close menu on nav-link clicks (crucial for mobile layout)
        const navLinks = document.querySelectorAll(".nav-link");
        navLinks.forEach(link => {
            link.addEventListener("click", () => {
                navToggle.classList.remove("open");
                navMenu.classList.remove("open");
            });
        });
    }

    // 3. Dynamic Products Grid Initialization (if container is present on page)
    initProductGrids();

    // 4. Modal Setup & Events
    initModal();

    // 5. Contact Form Submission
    initContactForm();

    // 6. Newsletter Subscription
    initNewsletterForm();
});

/**
 * Initializes and dynamically loads products to perfume and skincare pages
 */
function initProductGrids() {
    const perfumeGrid = document.getElementById("perfumes-grid");
    const skincareGrid = document.getElementById("skincare-grid");
    const featuredGrid = document.getElementById("featured-grid");

    // Populate Perfume Page
    if (perfumeGrid) {
        perfumeGrid.innerHTML = PRODUCTS.perfumes.map(p => generateProductCardHTML(p, "perfumes")).join("");
    }

    // Populate Skincare Page
    if (skincareGrid) {
        skincareGrid.innerHTML = PRODUCTS.skincare.map(p => generateProductCardHTML(p, "skincare")).join("");
    }

    // Populate Featured Products on Home Page (take first 2 from perfumes, first 2 from skincare)
    if (featuredGrid) {
        const featuredList = [
            { ...PRODUCTS.perfumes[0], cat: "perfumes", badge: "Best Seller" },
            { ...PRODUCTS.skincare[0], cat: "skincare", badge: "New Arrival" },
            { ...PRODUCTS.perfumes[1], cat: "perfumes", badge: "Premium Choice" },
            { ...PRODUCTS.skincare[1], cat: "skincare", badge: "Must Have" }
        ];
        
        featuredGrid.innerHTML = featuredList.map(p => generateProductCardHTML(p, p.cat, p.badge)).join("");
    }
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
function getWhatsAppOrderLink(product) {
    const formattedPrice = Number(product.price).toLocaleString("en-PK");
    const textMessage = `Assalam-o-Alaikum ${CONFIG.brandName},\n\nI would like to order the following product:\n\n*Product Name:* ${product.name}\n*Price:* Rs. ${formattedPrice}\n\nPlease let me know the details to confirm my order. Thank you!`;
    return `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(textMessage)}`;
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
        const productList = PRODUCTS[category];
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

        // WhatsApp CTA Config
        const orderButton = modal.querySelector(".modal-order-btn");
        orderButton.href = getWhatsAppOrderLink(product);

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
