# ZAYNOR — Premium Men's Grooming Brand Website

A fully static, professional e-commerce website for **ZAYNOR**, a Pakistani men's grooming brand specializing in luxury fragrances (attars) and organic skin care products.

---

## 🌐 Live Site

Deploy to **GitHub Pages** for free:
1. Push this repo to GitHub.
2. Go to **Settings → Pages → Source → `main` branch → `/` (root)**.
3. Your site will be live at: `https://<your-username>.github.io/<repo-name>/`

---

## 📁 File Structure

```
zaynor-ecommerce/
├── index.html          → Home page (Hero, Category cards, Featured Products)
├── perfumes.html       → Perfumes & Attars product grid
├── skincare.html       → Skin Care Essentials product grid
├── about.html          → Brand story and values
├── contact.html        → WhatsApp + email contact form
│
├── css/
│   └── style.css       → All custom styles (premium dark/gold design system)
│
├── js/
│   └── script.js       → All interactivity, product data, WhatsApp links
│
└── images/
    ├── hero-bg.png         → Homepage hero background
    ├── perfumes/
    │   ├── monarch.png     → Monarch Intense product image
    │   ├── obsidian.png    → Obsidian Oud product image
    │   └── safari.png      → Royal Safari attar image
    └── skincare/
        ├── facewash.png    → Charcoal Face Wash image
        └── serum.png       → Hydrating Serum / Beard Oil image
```

---

## ✏️ How to Customize

### 1. Change WhatsApp Number
Open `js/script.js` and edit line 8:
```js
const CONFIG = {
    whatsappNumber: "923084111590",  // ← Replace with your real number (92 + number without 0)
    brandName: "ZAYNOR"
};
```
For example, if your number is **0321-1234567**, use: `"923211234567"`

---

### 2. Add / Edit Products
All products are defined in the `PRODUCTS` object in `js/script.js`.

**Perfume example:**
```js
{
    id: "perfume-new",           // Must be unique
    name: "Your Fragrance Name",
    price: 3500,                 // in PKR (numbers only)
    image: "images/perfumes/yourfile.png",
    shortDescription: "Short 1-line teaser...",
    description: "Full detailed description shown in the modal popup.",
    specs: {
        "Longevity": "8-10 Hours",
        "Notes": "Oud, Rose, Sandalwood",
        "Volume": "50 ml",
        "Best For": "Evening wear"
    }
}
```

**Skincare example:**
```js
{
    id: "skin-new",
    name: "Your Product Name",
    price: 1200,
    image: "images/skincare/yourfile.png",
    shortDescription: "Short description...",
    description: "Full description...",
    specs: {
        "Skin Type": "All skin types",
        "Key Ingredients": "Charcoal, Tea Tree, Aloe Vera",
        "Volume": "150 ml",
        "Usage": "Twice daily"
    }
}
```

---

### 3. Replace Product Images
1. Put your images in `/images/perfumes/` or `/images/skincare/`
2. Update the `image` field in the product data in `js/script.js`
3. Use JPG or PNG — recommended size: **800x800px** (square)

---

### 4. Change Social Media Links
Search and replace placeholder `#` links in each HTML file:
```html
<!-- Instagram -->
<a href="https://www.instagram.com/zaynormen">

<!-- Facebook -->
<a href="https://www.facebook.com/zaynormen">
```

### 5. Change Email
Replace `inamullah11590@gmail.com` in all HTML files with your actual email.

---

## 🎨 Design System

| Token | Value | Use |
|---|---|---|
| `--bg-primary` | `#0a0a0c` | Main background |
| `--bg-secondary` | `#121216` | Card / footer background |
| `--gold-primary` | `#c5a059` | Primary gold accent color |
| `--gold-accent` | `#e5c483` | Hover / lighter gold |
| `--text-primary` | `#f5f5f7` | Main text |
| `--text-secondary` | `#a1a1a6` | Muted text |

---

## 📱 Ordering Flow

No cart or payment system. Every product has an **"Order on WhatsApp"** button that opens WhatsApp with a pre-filled message:

> *Assalam-o-Alaikum ZAYNOR, I would like to order:*
> ***Product Name** - Rs. [Price]*
> *Please let me know the details to confirm my order. Thank you!*

---

## ✅ GitHub Pages Checklist

- [x] All links are relative (no hardcoded domains)
- [x] No server-side code, no database
- [x] Fully static HTML/CSS/JS
- [x] Images in `/images/` folder
- [x] Mobile-first responsive layout
- [x] SEO meta descriptions on every page

---

## 📞 Support

Replace with your actual support contact in the files. The placeholder WhatsApp number is `923084111590`.

---

*© 2026 ZAYNOR Men. Crafted for the Modern Gentleman.*
