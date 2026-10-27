<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import portfolio from './data/portfolio.json'
import { saveOrder } from './db'

const plans = [
  { id: 'one', amount: 1, price: 3, label: 'Inicio', note: 'Para probar una nueva idea' },
  { id: 'five', amount: 5, price: 10, label: 'Creator', note: 'Contenido constante sin excederte' },
  { id: 'ten', amount: 10, price: 15, label: 'Pro', note: 'El favorito de los creadores', featured: true },
  { id: 'fifteen', amount: 15, price: 20, label: 'Studio', note: 'Para calendarios intensivos' },
  { id: 'twenty', amount: 20, price: 30, label: 'Ultra', note: 'Máximo volumen, mejor valor' },
]

const theme = ref(localStorage.getItem('bannegfx-theme') || 'dark')
const cart = ref(JSON.parse(localStorage.getItem('bannegfx-cart') || '[]'))
const cartOpen = ref(false)
const checkoutOpen = ref(false)
const selectedThumb = ref(null)
const query = ref('')
const client = ref('Todos')
const visibleCount = ref(18)
const orderState = ref('form')
const newOrderId = ref('')
const form = ref({ name: '', email: '', channel: '', notes: '' })
const heroIndex = ref(0)
const heroItems = portfolio.filter((item, index, items) => items.findIndex(candidate => candidate.client === item.client) === index)
let heroTimer

const clients = computed(() => ['Todos', ...new Set(portfolio.map(item => item.client))])
const filteredPortfolio = computed(() => portfolio.filter(item => {
  const matchesClient = client.value === 'Todos' || item.client === client.value
  const text = `${item.client} ${item.original}`.toLowerCase()
  return matchesClient && text.includes(query.value.trim().toLowerCase())
}))
const visiblePortfolio = computed(() => filteredPortfolio.value.slice(0, visibleCount.value))
const cartTotal = computed(() => cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0))
const cartUnits = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0))
const totalThumbnails = computed(() => cart.value.reduce((sum, item) => sum + item.amount * item.quantity, 0))

watch(theme, value => {
  document.documentElement.dataset.theme = value
  localStorage.setItem('bannegfx-theme', value)
}, { immediate: true })
watch(cart, value => localStorage.setItem('bannegfx-cart', JSON.stringify(value)), { deep: true })
watch([query, client], () => { visibleCount.value = 18 })

onMounted(() => {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.isIntersecting && entry.target.classList.add('revealed'))
  }, { threshold: 0.12 })
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
  startHeroRotation()
})

onBeforeUnmount(() => clearInterval(heroTimer))

function startHeroRotation() {
  clearInterval(heroTimer)
  heroTimer = setInterval(() => changeHero(1, false), 4200)
}

function pauseHeroRotation() {
  clearInterval(heroTimer)
}

function changeHero(direction, restart = true) {
  heroIndex.value = (heroIndex.value + direction + heroItems.length) % heroItems.length
  if (restart) startHeroRotation()
}

function addToCart(plan) {
  const existing = cart.value.find(item => item.id === plan.id)
  if (existing) existing.quantity += 1
  else cart.value.push({ ...plan, quantity: 1 })
  cartOpen.value = true
}

function changeQuantity(id, delta) {
  const item = cart.value.find(entry => entry.id === id)
  if (!item) return
  item.quantity += delta
  if (item.quantity <= 0) cart.value = cart.value.filter(entry => entry.id !== id)
}

function openCheckout() {
  if (!cart.value.length) return
  cartOpen.value = false
  orderState.value = 'form'
  checkoutOpen.value = true
}

async function submitOrder() {
  orderState.value = 'saving'
  const id = `BG-${Date.now().toString(36).toUpperCase()}`
  await saveOrder({
    id,
    customer: { ...form.value },
    items: cart.value.map(item => ({ ...item })),
    total: cartTotal.value,
    thumbnailCount: totalThumbnails.value,
    paymentMethod: 'PayPal',
    status: 'demo-pending',
    createdAt: new Date().toISOString(),
  })
  newOrderId.value = id
  orderState.value = 'success'
  cart.value = []
}

function closeCheckout() {
  checkoutOpen.value = false
  if (orderState.value === 'success') form.value = { name: '', email: '', channel: '', notes: '' }
}

function scrollToId(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function planPreview(plan) {
  const previewCount = Math.min(plan.amount, 5)
  const offset = { 1: 116, 5: 248, 10: 365, 15: 487, 20: 603 }[plan.amount] || 0
  return Array.from({ length: previewCount }, (_, index) => portfolio[(offset + index * 7) % portfolio.length])
}
</script>

<template>
  <div class="app-shell">
    <div class="ambient ambient-one"></div>
    <div class="ambient ambient-two"></div>
    <div class="pixel-world" aria-hidden="true">
      <span class="voxel voxel-grass"></span><span class="voxel voxel-diamond"></span><span class="voxel voxel-purple"></span>
      <i class="pixel-star star-a">✦</i><i class="pixel-star star-b">✦</i><i class="pixel-star star-c">✦</i>
      <span class="overworld-cloud cloud-a"></span><span class="overworld-cloud cloud-b"></span>
      <span class="end-island island-a"></span><span class="end-island island-b"></span>
      <span class="chorus-plant chorus-a"><i></i><i></i><i></i></span><span class="chorus-plant chorus-b"><i></i><i></i></span>
    </div>

    <header class="nav-wrap">
      <nav class="nav container">
        <button class="brand" aria-label="Ir al inicio" @click="scrollToId('inicio')">
          <span class="brand-mark">B</span>
          <span><strong>Banne</strong><em>GFX</em></span>
        </button>
        <div class="nav-links">
          <button @click="scrollToId('portfolio')">Portafolio</button>
          <button @click="scrollToId('planes')">Planes</button>
          <button @click="scrollToId('proceso')">Proceso</button>
        </div>
        <div class="nav-actions">
          <button class="icon-button" :aria-label="theme === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'" @click="theme = theme === 'dark' ? 'light' : 'dark'">
            <span v-if="theme === 'dark'">☀</span><span v-else>☾</span>
          </button>
          <button class="cart-button" @click="cartOpen = true">
            <span>Carrito</span><b>{{ cartUnits }}</b>
          </button>
        </div>
      </nav>
    </header>

    <main>
      <section id="inicio" class="hero container">
        <div class="hero-copy reveal">
          <div class="eyebrow"><i></i> BANNEGFX CRAFTING STUDIO · ONLINE</div>
          <div class="biome-indicator"><small>BIOMA ACTUAL</small><strong>{{ theme === 'light' ? 'OVERWORLD' : 'THE END' }}</strong></div>
          <h1>Haz que tu próximo video sea <span>imposible de ignorar.</span></h1>
          <p>Thumbnails hechas a medida para contar una historia, destacar en el feed y convertir una buena idea en un clic.</p>
          <div class="hero-actions">
            <button class="primary-button" @click="scrollToId('planes')">Ver planes <span>↗</span></button>
            <button class="secondary-button" @click="scrollToId('portfolio')">Explorar trabajos</button>
          </div>
          <div class="hero-proof">
            <div><strong>{{ portfolio.length }}</strong><span>diseños en el portafolio</span></div>
            <div><strong>{{ clients.length - 1 }}</strong><span>creadores atendidos</span></div>
            <div><strong>100%</strong><span>estilo personalizado</span></div>
          </div>
        </div>

        <div class="hero-visual reveal">
          <div class="hero-stack" @mouseenter="pauseHeroRotation" @mouseleave="startHeroRotation">
            <span class="pixel-corner corner-a"></span><span class="pixel-corner corner-b"></span><span class="pixel-corner corner-c"></span><span class="pixel-corner corner-d"></span>
            <Transition name="hero-swap" mode="out-in">
              <img :key="heroItems[heroIndex].id" :src="heroItems[heroIndex].src" :alt="`Thumbnail de Minecraft para ${heroItems[heroIndex].client}`" />
            </Transition>
            <div class="image-caption"><span>DISEÑADO POR <b>BANNEGFX</b> · PARA <b>{{ heroItems[heroIndex].client }}</b></span><span class="live-dot">PORTFOLIO REAL</span></div>
            <div class="hero-slider-controls">
              <button aria-label="Thumbnail anterior" @click="changeHero(-1)">‹</button>
              <span>{{ String(heroIndex + 1).padStart(2, '0') }} / {{ String(heroItems.length).padStart(2, '0') }}</span>
              <button aria-label="Siguiente thumbnail" @click="changeHero(1)">›</button>
            </div>
          </div>
          <div class="hotbar" aria-label="Barra de inventario decorativa">
            <span class="active">⛏</span><span>◆</span><span>✦</span><span>▣</span><span>◈</span><span>✧</span><span>◇</span><span>▦</span><span>★</span>
          </div>
        </div>
      </section>

      <section class="ticker" aria-label="Servicios">
        <div class="ticker-track">
          <span>THUMBNAILS MINECRAFT</span><i>◆</i><span>COMPOSICIÓN 3D</span><i>◆</i><span>COLOR GRADING</span><i>◆</i><span>STORYTELLING VISUAL</span><i>◆</i>
          <span>THUMBNAILS MINECRAFT</span><i>◆</i><span>COMPOSICIÓN 3D</span><i>◆</i><span>COLOR GRADING</span><i>◆</i><span>STORYTELLING VISUAL</span><i>◆</i>
        </div>
      </section>
      <div class="block-divider" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>

      <section id="portfolio" class="section container">
        <div class="section-biome-scene scene-gallery" aria-hidden="true">
          <div class="pixel-tree overworld-only tree-left"><i></i><i></i></div>
          <div class="pixel-mob creeper overworld-only"><span></span></div>
          <div class="obsidian-tower end-only"><i></i></div>
          <div class="pixel-mob enderman end-only"><span></span></div>
        </div>
        <div class="section-heading reveal">
          <div><span class="section-kicker">TRABAJOS SELECCIONADOS</span><h2>El feed es una batalla.<br><em>Entra para ganar.</em></h2></div>
          <p>Explora diseños reales. Cada pieza muestra a su creador y el cliente para quien fue realizada.</p>
        </div>

        <div class="gallery-tools reveal">
          <label class="search-box"><span>⌕</span><input v-model="query" type="search" placeholder="Buscar por cliente o archivo..." /></label>
          <label class="select-box"><span>Cliente</span><select v-model="client"><option v-for="name in clients" :key="name">{{ name }}</option></select></label>
          <span class="results-count">{{ filteredPortfolio.length }} resultados</span>
        </div>

        <div class="gallery-grid">
          <button v-for="item in visiblePortfolio" :key="item.id" class="thumb-card reveal revealed" @click="selectedThumb = item">
            <img :src="item.src" :alt="`Thumbnail de Minecraft para ${item.client}`" loading="lazy" />
            <span class="thumb-overlay">
              <span><small>CLIENTE</small><strong>{{ item.client }}</strong></span>
              <span><small>DISEÑO</small><strong>BanneGFX</strong></span>
              <b>↗</b>
            </span>
          </button>
        </div>
        <div v-if="visiblePortfolio.length < filteredPortfolio.length" class="load-wrap">
          <button class="secondary-button" @click="visibleCount += 18">Cargar más <span>{{ filteredPortfolio.length - visiblePortfolio.length }} restantes</span></button>
        </div>
        <div v-if="!filteredPortfolio.length" class="empty-state">No encontramos diseños con ese filtro.</div>
      </section>

      <section id="planes" class="pricing-section">
        <div class="section-biome-scene scene-pricing" aria-hidden="true">
          <div class="pixel-tree overworld-only tree-right"><i></i><i></i></div>
          <div class="pixel-mob pig overworld-only"><span></span></div>
          <div class="chorus-grove end-only"><i></i><i></i><i></i></div>
          <div class="end-crystal end-only"><i></i></div>
        </div>
        <div class="container">
          <div class="section-heading centered reveal">
            <div><span class="section-kicker">ELIGE TU PACK</span><h2>Craftea tu contenido. <em>Sube de nivel.</em></h2></div>
            <p>Elige el paquete que encaja con tu ritmo. Todos incluyen diseño personalizado y entrega digital.</p>
          </div>
          <div class="pricing-grid">
            <article v-for="plan in plans" :key="plan.id" class="price-card reveal" :class="{ featured: plan.featured }">
              <span v-if="plan.featured" class="popular">MÁS ELEGIDO</span>
              <div class="plan-head"><span>{{ plan.label }}</span><i>{{ String(plan.amount).padStart(2, '0') }}</i></div>
              <div class="plan-visual" :class="`visual-${Math.min(plan.amount, 5)}`">
                <img
                  v-for="(thumb, index) in planPreview(plan)"
                  :key="thumb.id"
                  :src="thumb.src"
                  :alt="`Ejemplo ${index + 1} del plan de ${plan.amount} thumbnails`"
                  loading="lazy"
                  :style="{ '--index': index, '--total': Math.min(plan.amount, 5) }"
                />
                <span v-if="plan.amount > 5" class="stack-count">+{{ plan.amount - 5 }}</span>
                <span class="visual-volume">{{ plan.amount }} diseño{{ plan.amount > 1 ? 's' : '' }}</span>
              </div>
              <h3>x{{ plan.amount }} <small>Thumbnail{{ plan.amount > 1 ? 's' : '' }}</small></h3>
              <div class="price"><sup>$</sup>{{ plan.price }}<span>USD</span></div>
              <p>{{ plan.note }}</p>
              <ul>
                <li>✓ Diseño 100% personalizado</li>
                <li>✓ Formato 16:9 listo para YouTube</li>
                <li>✓ Ajustes incluidos</li>
              </ul>
              <button :class="plan.featured ? 'primary-button' : 'secondary-button'" @click="addToCart(plan)">Agregar al carrito <span>＋</span></button>
            </article>
          </div>
        </div>
      </section>

      <section id="proceso" class="section process container">
        <div class="section-biome-scene scene-process" aria-hidden="true">
          <div class="pixel-tree overworld-only tree-small"><i></i><i></i></div>
          <div class="pixel-mob cow overworld-only"><span></span></div>
          <div class="end-portal end-only"><i></i></div>
          <div class="pixel-mob enderman enderman-two end-only"><span></span></div>
        </div>
        <div class="section-heading reveal">
          <div><span class="section-kicker">DE LA IDEA AL FEED</span><h2>Un proceso claro.<br><em>Un resultado potente.</em></h2></div>
          <p>La demo simula el recorrido completo de una compra. El pago no es real todavía.</p>
        </div>
        <div class="process-grid">
          <article class="reveal"><span>01</span><div class="process-icon">◇</div><h3>Elige tu plan</h3><p>Selecciona la cantidad de thumbnails que necesitas y agrégala al carrito.</p></article>
          <article class="reveal"><span>02</span><div class="process-icon">✎</div><h3>Comparte tu idea</h3><p>Déjanos tus datos, canal y una breve descripción del contenido.</p></article>
          <article class="reveal"><span>03</span><div class="process-icon">P</div><h3>Checkout PayPal</h3><p>Confirma el pedido con el único método disponible en esta demostración.</p></article>
          <article class="reveal"><span>04</span><div class="process-icon">✦</div><h3>Listo para crear</h3><p>Tu orden se guarda localmente y recibes un número de seguimiento demo.</p></article>
        </div>
      </section>

      <section class="cta container reveal">
        <div class="section-biome-scene scene-cta" aria-hidden="true">
          <div class="overworld-hills overworld-only"><i></i><i></i></div>
          <div class="ender-dragon end-only"><i></i><i></i><span></span></div>
        </div>
        <div><span class="section-kicker">¿TU PRÓXIMO VIDEO YA TIENE IDEA?</span><h2>Hagamos que tenga <em>presencia.</em></h2></div>
        <button class="primary-button" @click="scrollToId('planes')">Comenzar ahora <span>↗</span></button>
      </section>
    </main>

    <footer class="footer container">
      <div class="brand"><span class="brand-mark">B</span><span><strong>Banne</strong><em>GFX</em></span></div>
      <p>Thumbnails de Minecraft con dirección visual.</p>
      <span>© {{ new Date().getFullYear() }} BanneGFX · Sitio demostrativo</span>
    </footer>

    <transition name="fade"><div v-if="cartOpen || checkoutOpen || selectedThumb" class="backdrop" @click="cartOpen = false; checkoutOpen = false; selectedThumb = null"></div></transition>

    <transition name="slide">
      <aside v-if="cartOpen" class="cart-drawer">
        <div class="drawer-head"><div><span class="section-kicker">TU SELECCIÓN</span><h2>Carrito</h2></div><button class="close" @click="cartOpen = false">×</button></div>
        <div v-if="cart.length" class="cart-list">
          <article v-for="item in cart" :key="item.id">
            <div><strong>x{{ item.amount }} Thumbnails</strong><span>{{ item.label }} · ${{ item.price }} USD</span></div>
            <div class="quantity"><button @click="changeQuantity(item.id, -1)">−</button><b>{{ item.quantity }}</b><button @click="changeQuantity(item.id, 1)">＋</button></div>
          </article>
        </div>
        <div v-else class="cart-empty"><span>◇</span><h3>Tu carrito está vacío</h3><p>Elige uno de los planes para comenzar.</p><button class="primary-button" @click="cartOpen = false; scrollToId('planes')">Ver planes</button></div>
        <div v-if="cart.length" class="cart-summary">
          <div><span>Total de diseños</span><strong>{{ totalThumbnails }}</strong></div>
          <div class="grand-total"><span>Total</span><strong>${{ cartTotal }} <small>USD</small></strong></div>
          <button class="paypal-button" @click="openCheckout"><b>Pay</b><i>Pal</i> Continuar al checkout</button>
          <small>Pago demostrativo. No se realizará ningún cargo.</small>
        </div>
      </aside>
    </transition>

    <transition name="pop">
      <div v-if="checkoutOpen" class="modal checkout-modal" role="dialog" aria-modal="true">
        <button class="close" @click="closeCheckout">×</button>
        <template v-if="orderState !== 'success'">
          <span class="section-kicker">CHECKOUT DEMOSTRATIVO</span><h2>Finaliza tu pedido</h2>
          <div class="checkout-layout">
            <form @submit.prevent="submitOrder">
              <label>Nombre<input v-model="form.name" required placeholder="Tu nombre" /></label>
              <label>Correo<input v-model="form.email" required type="email" placeholder="tu@correo.com" /></label>
              <label>Canal de YouTube<input v-model="form.channel" required placeholder="Nombre o enlace de tu canal" /></label>
              <label>¿Qué tienes en mente?<textarea v-model="form.notes" rows="3" placeholder="Cuéntame sobre tus próximos videos..."></textarea></label>
              <div class="payment-choice"><div class="radio active"></div><div><strong><b>Pay</b><i>Pal</i></strong><span>Único método disponible</span></div><em>DEMO</em></div>
              <button class="paypal-button" :disabled="orderState === 'saving'"><span v-if="orderState === 'saving'">Guardando...</span><span v-else>Confirmar pedido · ${{ cartTotal }} USD</span></button>
            </form>
            <aside><span>RESUMEN</span><div v-for="item in cart" :key="item.id"><p>x{{ item.amount }} Thumbnails × {{ item.quantity }}</p><b>${{ item.price * item.quantity }}</b></div><hr><div><strong>Total</strong><strong>${{ cartTotal }} USD</strong></div><small>Los datos se guardan únicamente en la base de datos local de este navegador.</small></aside>
          </div>
        </template>
        <div v-else class="success-state"><div class="success-icon">✓</div><span class="section-kicker">PEDIDO REGISTRADO</span><h2>¡Tu idea ya está en marcha!</h2><p>Esta es una confirmación demostrativa. Tu orden quedó guardada localmente.</p><div class="order-id"><span>NÚMERO DE PEDIDO</span><strong>{{ newOrderId }}</strong></div><button class="primary-button" @click="closeCheckout">Volver al sitio</button></div>
      </div>
    </transition>

    <transition name="pop">
      <div v-if="selectedThumb" class="modal image-modal" role="dialog" aria-modal="true">
        <button class="close" @click="selectedThumb = null">×</button>
        <img :src="selectedThumb.src" :alt="`Thumbnail para ${selectedThumb.client}`" />
        <div><span><small>CREADO POR</small><strong>BanneGFX</strong></span><span><small>PARA</small><strong>{{ selectedThumb.client }}</strong></span><button class="primary-button" @click="selectedThumb = null; scrollToId('planes')">Quiero una así <span>↗</span></button></div>
      </div>
    </transition>
  </div>
</template>
