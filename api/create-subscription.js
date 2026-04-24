const Stripe = require('stripe');
const { getAuthenticatedUser } = require('./_supabaseUser');

const PLANS = {
  pro:     { price: 500,  name: 'Terroir HUB Pro',     credits: 100 },
  premium: { price: 1500, name: 'Terroir HUB Premium', credits: 300 },
};

const ALLOWED_ORIGINS = [
  'https://sake.terroirhub.com','https://shochu.terroirhub.com',
  'https://whisky.terroirhub.com','https://liqueur.terroirhub.com',
  'https://craft.terroirhub.com',
  'https://www.terroirhub.com','https://terroirhub.com',
];

module.exports = async function handler(req, res) {
  var origin = req.headers.origin || '';
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  }
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const { plan } = req.body || {};
  const user = await getAuthenticatedUser(req);

  if (!plan || !PLANS[plan]) {
    return res.status(400).json({ error: 'Invalid plan' });
  }
  if (!user || !user.id || !user.email) {
    return res.status(401).json({ error: 'Login required' });
  }

  const selected = PLANS[plan];

  try {
    // 既存の Stripe Customer を探す or 作成
    const customers = await stripe.customers.list({ email: user.email, limit: 1 });
    let customer;
    if (customers.data.length > 0) {
      customer = customers.data[0];
    } else {
      customer = await stripe.customers.create({
        email: user.email,
        metadata: { user_id: user.id },
      });
    }

    // Price を動的に作成（or 既存のものを使う）
    // 本番では Stripe ダッシュボードで事前に Price を作っておくのが望ましい
    const prices = await stripe.prices.list({
      lookup_keys: ['thub_' + plan],
      limit: 1,
    });

    let priceId;
    if (prices.data.length > 0) {
      priceId = prices.data[0].id;
    } else {
      // Price が存在しない場合は作成
      const product = await stripe.products.create({
        name: selected.name,
        metadata: { plan: plan },
      });
      const price = await stripe.prices.create({
        product: product.id,
        unit_amount: selected.price,
        currency: 'jpy',
        recurring: { interval: 'month' },
        lookup_key: 'thub_' + plan,
      });
      priceId = price.id;
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      customer: customer.id,
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      metadata: {
        user_id: user.id,
        plan: plan,
      },
      subscription_data: {
        metadata: {
          user_id: user.id,
          plan: plan,
        },
      },
      success_url: `${req.headers.origin || 'https://sake.terroirhub.com'}/?plan_activated=${plan}`,
      cancel_url: `${req.headers.origin || 'https://sake.terroirhub.com'}/`,
    });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('Stripe subscription error:', err.message);
    return res.status(500).json({ error: 'Subscription creation failed' });
  }
};
