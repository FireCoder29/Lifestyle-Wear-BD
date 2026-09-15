/* ==========================================================
   LIFESTYLE WEAR — STORE SETTINGS
   ========================================================== */

/* CHANGE #1: WhatsApp number */
const WHATSAPP_NUMBER = "8801615574500";

/* CHANGE #2: Delivery charge */
const DELIVERY_CHARGE = 100;

/* CHANGE #3: Categories */
const CATEGORIES = [
  { name: "All", sub: "Everything" },
  { name: "Dresses", sub: "Female Dress" },
  { name: "Drop-Shoulder", sub: "everyday" },
  { name: "T-Shirts", sub: "Casual" },
  { name: "New Arrivals", sub: "Just in" }
];

/* CHANGE #4: Products
   ⭐ To add/change stock, edit ONLY the stock number.
   Example: stock: 20
*/
const PRODUCTS = [
  {
    id: 1,
    name: "Drop-Shoulder - 1",
    price: 550,
    image: "images/DS-1.webp",
    category: "Drop-Shoulder",
    stock: 15,   //Use this in console -> localStorage.removeItem("LW_STOCK");
    badge: "You know",
    description: "A clean, comfortable piece selected for everyday elegance."
  },

  {
    id: 2,
    name: "Drop-Shoulder - 2",
    price: 550,
    image: "images/DS-2.webp",
    category: "Drop-Shoulder",
    stock: 15,
    badge: "NEW",
    description: "An effortless silhouette designed for comfort and confidence."
  },

  {
    id: 3,
    name: "Drop-Shoulder - 3",
    price: 550,
    image: "images/DS-3.jpg",
    category: "Drop-Shoulder",
    stock: 20,
    badge: "",
    description: "Simple, versatile and easy to style."
  },

  {
    id: 4,
    name: "Drop-Shoulder - 4",
    price: 550,
    image: "images/DS-4.webp",
    category: "Drop-Shoulder",
    stock: 15,
    badge: "POPULAR",
    description: "A refined everyday essential with a clean finish."
  },

  {
    id: 5,
    name: "Minimalist T-Shirt",
    price: 450,
    image: "images/TS-1.jpg",
    category: "T-Shirts",
    stock: 25,
    badge: "",
    description: "Minimal styling and everyday comfort."
  },

  {
    id: 6,
    name: "New Arrival T-Shirt",
    price: 450,
    image: "images/TS-2.jpg",
    category: "New Arrivals",
    stock: 30,
    badge: "NEW",
    description: "One of the latest pieces in the Lifestyle Wear edit."
  },

  {
    id: 7,
    name: "Female Everyday Dress",
    price: 1500,
    image: "images/FD-1.jpg",
    category: "Dresses",
    stock: 20,
    badge: "BEST",
    description: "A standout everyday piece from our signature selection."
  },

  {
    id: 8,
    name: "Female Everyday Dress - 2",
    price: 1500,
    image: "images/FD-2.jpg",
    category: "Dresses",
    stock: 25,
    badge: "",
    description: "Made to be worn, repeated and enjoyed."
  }
];

/* ==========================================================
   ONLINE DATABASE
   ========================================================== */

const API_BASE_URL = "https://lifestyle-wear-bd.onrender.com";
let stockReady = false;

/* ==========================================================
   BASIC SETTINGS
   ========================================================== */

const placeholder =
  "data:image/svg+xml;charset=UTF-8," +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg"
         width="800"
         height="1000">
      <rect width="100%" height="100%" fill="#ebe8e1"/>
      <text x="50%"
            y="48%"
            text-anchor="middle"
            font-family="Arial"
            font-size="28"
            fill="#777">
        LIFESTYLE WEAR
      </text>
    </svg>
  `);



/* ==========================================================
   LOAD STOCK FROM ONLINE DATABASE
   ========================================================== */

async function loadDatabaseStock() {

  try {

    const response =
      await fetch(`${API_BASE_URL}/api/products`);

    if (!response.ok)
      throw new Error("Failed to load stock");

    const databaseProducts =
      await response.json();


    databaseProducts.forEach(dbProduct => {

      const product =
        PRODUCTS.find(
          p => p.id === dbProduct.id
        );

      if (product) {

        product.stock =
          Number(dbProduct.stock);

      }

    });


    stockReady = true;

    renderFeatured();
    renderProductsPage();
    renderCart();

  } catch (error) {

    console.error(
      "Database stock error:",
      error
    );

    alert(
      "Unable to load live stock. Please refresh the page."
    );

  }

}

/* ==========================================================
   CART
   ========================================================== */

let cart =
  JSON.parse(localStorage.getItem("LW_CART") || "[]");

let selectedCategory = "All";
let search = "";
let quickProduct = null;


/* ==========================================================
   HELPERS
   ========================================================== */

const $ = id => document.getElementById(id);

const money = n =>
  Number(n).toLocaleString("en-BD");

const img = s =>
  s || placeholder;

const escape = s =>
  String(s).replace(
    /[&<>"']/g,
    m => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[m])
  );


/* ==========================================================
   SAVE CART
   ========================================================== */

function save() {
  localStorage.setItem(
    "LW_CART",
    JSON.stringify(cart)
  );
}





/* ==========================================================
   CART CALCULATIONS
   ========================================================== */

function quantity() {

  return cart.reduce(
    (total, item) => total + item.qty,
    0
  );

}


function subtotal() {

  return cart.reduce(
    (total, item) => {

      const product =
        PRODUCTS.find(p => p.id === item.id);

      return total +
        (product
          ? product.price * item.qty
          : 0);

    },
    0
  );

}


/* ==========================================================
   ADD PRODUCT TO BAG
   ========================================================== */

function add(id) {

  const product =
    PRODUCTS.find(p => p.id === id);

  if (!product) return;


  /* STOCK OUT CHECK */

  if (product.stock <= 0) {

    alert("Sorry, this product is out of stock.");

    return;
  }


  /* FIND ITEM IN BAG */

  const item =
    cart.find(x => x.id === id);


  const currentQty =
    item ? item.qty : 0;


  /* STOCK LIMIT */

  if (currentQty >= product.stock) {

    alert(
      `Only ${product.stock} item(s) available in stock.`
    );

    return;
  }


  /* ADD PRODUCT */

  if (item) {

    item.qty++;

  } else {

    cart.push({
      id: id,
      qty: 1
    });

  }


  save();

  renderCart();

  openCart();

}


/* ==========================================================
   CHANGE CART QUANTITY
   ========================================================== */

function change(id, n) {

  const item =
    cart.find(x => x.id === id);

  if (!item) return;


  const product =
    PRODUCTS.find(p => p.id === id);

  if (!product) return;


  /* INCREASE */

  if (n > 0) {

    if (item.qty >= product.stock) {

      alert(
        `Only ${product.stock} item(s) available in stock.`
      );

      return;
    }

  }


  item.qty += n;


  /* REMOVE IF ZERO */

  if (item.qty <= 0) {

    cart =
      cart.filter(x => x.id !== id);

  }


  save();

  renderCart();

}


/* ==========================================================
   REMOVE ITEM
   ========================================================== */

function removeItem(id) {

  cart =
    cart.filter(x => x.id !== id);

  save();

  renderCart();

}


/* ==========================================================
   RENDER CART
   ========================================================== */

function renderCart() {

  const q = quantity();
  const sub = subtotal();


  if ($("cartCount"))
    $("cartCount").textContent = q;


  if ($("drawerCount"))
    $("drawerCount").textContent = q;


  if ($("subtotal"))
    $("subtotal").textContent = money(sub);


  if ($("delivery"))
    $("delivery").textContent =
      money(DELIVERY_CHARGE);


  if ($("checkoutTotal"))
    $("checkoutTotal").textContent =
      money(
        sub +
        (cart.length
          ? DELIVERY_CHARGE
          : 0)
      );


  const list = $("cartList");

  if (!list) return;


  /* EMPTY BAG */

  if (!cart.length) {

    list.innerHTML = `
      <div class="empty">
        Your bag is waiting.
        <br><br>
        Add something you love.
      </div>
    `;

    return;
  }


  list.innerHTML = "";


  cart.forEach(x => {

    const product =
      PRODUCTS.find(p => p.id === x.id);

    if (!product) return;


    const el =
      document.createElement("div");

    el.className = "cart-item";


    el.innerHTML = `
      <img
        src="${img(product.image)}"
        onerror="this.src=placeholder"
        alt=""
      >

      <div>

        <h4>
          ${escape(product.name)}
        </h4>

        <p>
          ৳${money(product.price)} each
        </p>

        <div class="qty">

          <button class="minus">
            −
          </button>

          <span>
            ${x.qty}
          </span>

          <button class="plus">
            +
          </button>

        </div>

      </div>

      <div style="text-align:right">

        <b style="font-size:12px">
          ৳${money(product.price * x.qty)}
        </b>

        <br>

        <button class="remove">
          REMOVE
        </button>

      </div>
    `;


    el.querySelector(".minus")
      .onclick =
      () => change(product.id, -1);


    el.querySelector(".plus")
      .onclick =
      () => change(product.id, 1);


    el.querySelector(".remove")
      .onclick =
      () => removeItem(product.id);


    list.appendChild(el);

  });

}


/* ==========================================================
   CART OPEN / CLOSE
   ========================================================== */

function openCart() {

  $("cart")?.classList.add("open");

  $("screen")?.classList.add("show");

}


function closeCart() {

  $("cart")?.classList.remove("open");


  if (
    !$("mobilePanel")
      ?.classList.contains("open")
  ) {

    $("screen")
      ?.classList.remove("show");

  }

}


/* ==========================================================
   HOME CATEGORIES
   ========================================================== */

function renderCategoriesHome() {

  const grid =
    $("categoryGrid");

  if (!grid) return;


  grid.innerHTML = "";


  CATEGORIES.forEach((cat, i) => {

    const el =
      document.createElement("a");

    el.className =
      "category-card";


    el.href =
      `products.html${cat.name === "All"
        ? ""
        : "?category=" +
        encodeURIComponent(cat.name)
      }`;


    el.innerHTML = `
      <span class="num">
        0${i + 1}
      </span>

      <h3>
        ${escape(cat.name)}
      </h3>

      <span>
        ${escape(cat.sub)} ↗
      </span>
    `;


    grid.appendChild(el);

  });

}


/* ==========================================================
   PRODUCT CARD
   ========================================================== */

function productCard(p) {

  const card =
    document.createElement("article");

  card.className =
    "product-card";


  /* STOCK DISPLAY */

  const stockHTML =
    p.stock > 0

      ? `
        <span class="stock">
          Stock: ${p.stock}
        </span>
      `

      : `
        <span class="stock-out">
          STOCK OUT
        </span>
      `;


  /* BUTTON */

  const buttonHTML =
    p.stock > 0

      ? `
        <button class="add-small">
          ADD +
        </button>
      `

      : `
        <button
          class="add-small"
          disabled
        >
          STOCK OUT
        </button>
      `;


  card.innerHTML = `

    <div class="product-image">

      ${p.badge
      ? `
            <span class="product-badge">
              ${escape(p.badge)}
            </span>
          `
      : ""
    }

      <img
        src="${img(p.image)}"
        onerror="this.src=placeholder"
        alt="${escape(p.name)}"
      >

      <button class="quick-view">
        ↗
      </button>

    </div>


    <div class="product-meta">

      <span class="product-cat">
        ${escape(p.category)}
      </span>

      <h3>
        ${escape(p.name)}
      </h3>


      <div class="product-row">

        <span class="product-price">
          ৳${money(p.price)}
        </span>

        ${buttonHTML}

      </div>


      ${stockHTML}

    </div>

  `;


  /* PRODUCT IMAGE CLICK */

  card
    .querySelector(".product-image")
    .onclick = e => {

      if (
        !e.target.closest(".quick-view")
      ) {

        openProductDetail(p);

      }

    };


  /* QUICK VIEW */

  card
    .querySelector(".quick-view")
    .onclick = e => {

      e.stopPropagation();

      openProductDetail(p);

    };


  /* ADD BUTTON */

  card
    .querySelector(".add-small")
    .onclick = () => {

      if (p.stock > 0) {

        add(p.id);

      }

    };


  return card;

}


/* ==========================================================
   PRODUCT DETAIL
   ========================================================== */

function openProductDetail(p) {

  quickProduct = p;


  if (!$("productOverlay"))
    return;


  $("detailImage").src =
    img(p.image);


  $("detailImage").onerror =
    () => {

      $("detailImage").src =
        placeholder;

    };


  $("detailImage").alt =
    p.name;


  $("detailCategory").textContent =
    p.category;


  $("detailName").textContent =
    p.name;


  $("detailPrice").textContent =
    money(p.price);


  $("detailDescription").textContent =
    p.description;


  /* SHOW STOCK IN DETAIL */

  const stockElement =
    $("detailStock");


  if (stockElement) {

    stockElement.textContent =
      p.stock > 0
        ? `Stock: ${p.stock}`
        : "STOCK OUT";

  }


  /* DETAIL ADD BUTTON */

  const detailAdd =
    $("detailAdd");


  if (detailAdd) {

    if (p.stock > 0) {

      detailAdd.disabled = false;

      detailAdd.textContent =
        "Add to bag +";

    } else {

      detailAdd.disabled = true;

      detailAdd.textContent =
        "STOCK OUT";

    }

  }


  $("productOverlay")
    .classList.add("show");


  document.body
    .classList.add("no-scroll");


  history.pushState(
    { product: p.id },
    "",
    `#product-${p.id}`
  );

}


/* ==========================================================
   CLOSE PRODUCT DETAIL
   ========================================================== */

function closeProductDetail() {

  if (!$("productOverlay"))
    return;


  $("productOverlay")
    .classList.remove("show");


  document.body
    .classList.remove("no-scroll");


  if (
    location.hash.startsWith(
      "#product-"
    )
  ) {

    history.replaceState(
      null,
      "",
      location.pathname +
      location.search
    );

  }


  quickProduct = null;

}


/* ==========================================================
   PRODUCTS PAGE
   ========================================================== */

function renderProductsPage() {

  const grid =
    $("productGrid");

  if (!grid) return;


  const tabs =
    $("categoryTabs");


  if (tabs) {

    tabs.innerHTML = "";


    CATEGORIES.forEach(cat => {

      const b =
        document.createElement("button");


      b.className =
        cat.name === selectedCategory
          ? "active"
          : "";


      b.textContent =
        cat.name;


      b.onclick = () => {

        selectedCategory =
          cat.name;

        renderProductsPage();

      };


      tabs.appendChild(b);

    });

  }


  const items =
    PRODUCTS.filter(p => {

      const c =
        selectedCategory === "All" ||
        p.category === selectedCategory;


      const s =
        !search ||
        p.name
          .toLowerCase()
          .includes(
            search.toLowerCase()
          );


      return c && s;

    });


  if ($("resultCount")) {

    $("resultCount").textContent =
      `${items.length} PRODUCTS`;

  }


  grid.innerHTML = "";


  items.forEach(p => {

    grid.appendChild(
      productCard(p)
    );

  });

}


/* ==========================================================
   FEATURED PRODUCTS
   ========================================================== */

function renderFeatured() {

  const grid =
    $("featuredGrid");

  if (!grid) return;


  grid.innerHTML = "";


  PRODUCTS
    .slice(0, 4)
    .forEach(p => {

      grid.appendChild(
        productCard(p)
      );

    });

}

/* ==========================================================
   SUBMIT ORDER TO ONLINE DATABASE
   ========================================================== */

async function submitDatabaseOrder(customer) {

  const response =
    await fetch(`${API_BASE_URL}/api/orders`, {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({

        customer: {
          name: customer.name,
          phone: customer.phone,
          address: customer.address,
          note: customer.note
        },

        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.qty
        }))

      })

    });


  const data =
    await response.json();


  if (!response.ok) {

    let errorMessage =
      "Order could not be completed.";

    if (typeof data.detail === "string") {

      errorMessage =
        data.detail;

    }
    else if (data.detail) {

      errorMessage =
        JSON.stringify(
          data.detail
        );

    }

    throw new Error(
      errorMessage
    );

  }


  return data;

}


/* ==========================================================
   WHATSAPP ORDER MESSAGE
   ========================================================== */

function buildMessage(customer) {

  let m =
    `Hello Lifestyle Wear!%0A%0A` +
    `*NEW ORDER*%0A` +
    `--------------------%0A`;


  cart.forEach((x, i) => {

    const p =
      PRODUCTS.find(
        p => p.id === x.id
      );


    if (p) {

      m +=
        `${i + 1}. ` +
        `${encodeURIComponent(p.name)}` +
        `%0A`;

      m +=
        `Qty: ${x.qty}%0A`;

      m +=
        `Price: ৳${p.price * x.qty}%0A`;

    }

  });


  const sub =
    subtotal();


  const total =
    sub +
    (
      cart.length
        ? DELIVERY_CHARGE
        : 0
    );


  m +=
    `%0A*Subtotal:* ৳${sub}`;


  m +=
    `%0A*Delivery:* ৳${DELIVERY_CHARGE}`;


  m +=
    `%0A*TOTAL:* ৳${total}`;


  m +=
    `%0A%0A*CUSTOMER*`;


  m +=
    `%0AName: ` +
    `${encodeURIComponent(customer.name)}`;


  m +=
    `%0APhone: ` +
    `${encodeURIComponent(customer.phone)}`;


  m +=
    `%0AAddress: ` +
    `${encodeURIComponent(customer.address)}`;


  if (customer.note) {

    m +=
      `%0ANote: ` +
      `${encodeURIComponent(customer.note)}`;

  }


  return m;

}


/* ==========================================================
   CHECKOUT
   ========================================================== */

$("checkoutForm")
  ?.addEventListener(
    "submit",
    async e => {

      e.preventDefault();


      /* BAG EMPTY CHECK */

      if (!cart.length) {

        alert(
          "Your bag is empty."
        );

        return;

      }


      /* LIVE STOCK CHECK */

      if (!stockReady) {

        alert(
          "Live stock is still loading. Please wait a moment and try again."
        );

        return;

      }


      /* REFRESH LIVE STOCK */

      await loadDatabaseStock();

      if (!stockReady)
        return;


      /* CHECK STOCK ONE MORE TIME */

      for (const item of cart) {

        const product =
          PRODUCTS.find(
            p => p.id === item.id
          );


        if (!product)
          continue;


        if (item.qty > product.stock) {

          alert(
            `${product.name} does not have enough stock. Only ${product.stock} available.`
          );

          renderCart();

          return;

        }

      }


      /* CUSTOMER INFORMATION */

      const customer = {

        name:
          $("customerName")
            ?.value
            .trim() || "",

        phone:
          $("customerPhone")
            ?.value
            .trim() || "",

        address:
          $("customerAddress")
            ?.value
            .trim() || "",

        note:
          $("customerNote")
            ?.value
            .trim() || ""

      };


      /* BUILD MESSAGE BEFORE ORDER */

      const message =
        buildMessage(customer);


      /* SEND ORDER TO ONLINE DATABASE */

      try {

        await submitDatabaseOrder(
          customer
        );


        /* ORDER SUCCESSFUL */


        /* CLEAR BAG */

        cart = [];

        save();


        /* UPDATE WEBSITE */

        renderCart();

        renderFeatured();

        renderProductsPage();


        /* CLOSE CHECKOUT */

        $("checkoutModal")
          ?.classList
          .remove("show");


        /* OPEN WHATSAPP */

        window.open(
          `https://wa.me/${WHATSAPP_NUMBER}?text=${message}`,
          "_blank"
        );


        /* GET UPDATED STOCK */

        loadDatabaseStock();


      } catch (error) {

        console.error(
          "Order error:",
          error
        );


        alert(
          error.message ||
          "Order could not be completed. Please try again."
        );

      }

    }
  );


/* ==========================================================
   GENERAL CONTROLS
   ========================================================== */

$("cartBtn")
  ?.addEventListener(
    "click",
    openCart
  );


$("closeCart")
  ?.addEventListener(
    "click",
    closeCart
  );


$("screen")
  ?.addEventListener(
    "click",
    () => {

      closeCart();

      closeMenu();

    }
  );


$("clearCart")
  ?.addEventListener(
    "click",
    () => {

      if (
        confirm(
          "Clear your bag?"
        )
      ) {

        cart = [];

        save();

        renderCart();

      }

    }
  );


$("checkoutBtn")
  ?.addEventListener(
    "click",
    () => {

      if (!cart.length) {

        alert(
          "Add a product to your bag first."
        );

        return;

      }


      $("checkoutModal")
        ?.classList
        .add("show");

    }
  );


$("closeCheckout")
  ?.addEventListener(
    "click",
    () => {

      $("checkoutModal")
        ?.classList
        .remove("show");

    }
  );


/* ==========================================================
   SEARCH
   ========================================================== */

$("searchBtn")
  ?.addEventListener(
    "click",
    () => {

      $("searchbar")
        ?.classList
        .add("active");


      $("searchInput")
        ?.focus();

    }
  );


$("closeSearch")
  ?.addEventListener(
    "click",
    () => {

      $("searchbar")
        ?.classList
        .remove("active");


      if ($("searchInput"))
        $("searchInput").value = "";


      search = "";


      renderProductsPage();

    }
  );


$("searchInput")
  ?.addEventListener(
    "input",
    e => {

      search =
        e.target.value;

      renderProductsPage();

    }
  );


/* ==========================================================
   MOBILE MENU
   ========================================================== */

function openMenu() {

  $("mobilePanel")
    ?.classList
    .add("open");


  $("screen")
    ?.classList
    .add("show");

}


function closeMenu() {

  $("mobilePanel")
    ?.classList
    .remove("open");


  if (
    !$("cart")
      ?.classList
      .contains("open")
  ) {

    $("screen")
      ?.classList
      .remove("show");

  }

}


$("menuBtn")
  ?.addEventListener(
    "click",
    openMenu
  );


$("closeMenu")
  ?.addEventListener(
    "click",
    closeMenu
  );


/* ==========================================================
   PRODUCT DETAIL CONTROLS
   ========================================================== */

$("detailClose")
  ?.addEventListener(
    "click",
    closeProductDetail
  );


$("productOverlay")
  ?.addEventListener(
    "click",
    e => {

      if (
        e.target ===
        $("productOverlay")
      ) {

        closeProductDetail();

      }

    }
  );


$("detailAdd")
  ?.addEventListener(
    "click",
    () => {

      if (
        quickProduct &&
        quickProduct.stock > 0
      ) {

        add(
          quickProduct.id
        );

        closeProductDetail();

      }

    }
  );


/* ==========================================================
   BROWSER BACK BUTTON
   ========================================================== */

window.addEventListener(
  "popstate",
  () => {

    if (
      $("productOverlay")
        ?.classList
        .contains("show")
    ) {

      closeProductDetail();

    }

  }
);


/* ==========================================================
   URL CATEGORY SUPPORT
   ========================================================== */

const params =
  new URLSearchParams(
    location.search
  );


if (
  params.get("category") &&
  CATEGORIES.some(
    c =>
      c.name ===
      params.get("category")
  )
) {

  selectedCategory =
    params.get("category");

}


/* ==========================================================
   INITIAL LOAD
   ========================================================== */

renderCategoriesHome();

renderFeatured();

renderProductsPage();

renderCart();

/* LOAD LIVE STOCK */
loadDatabaseStock();

/* AUTO SYNC LIVE STOCK EVERY 5 SECONDS */
setInterval(
  loadDatabaseStock,
  5000
);