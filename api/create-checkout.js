const Stripe = require('stripe');
const { getAuthenticatedUser } = require('./_supabaseUser');

const CREDIT_PACKS = {
  '10': { credits: 10, price: 300, name: '10 credits' },
  '30': { credits: 30, price: 600, name: '30 credits' },
  '50': { credits: 50, price: 800, name: '50 credits' },
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

  const { pack } = req.body || {};
  const user = await getAuthenticatedUser(req);

  if (!pack || !CREDIT_PACKS[pack]) {
    return res.status(400).json({ error: 'Invalid pack' });
  }
  if (!user || !user.id) {
    return res.status(401).json({ error: 'Login required' });
  }

  const selected = CREDIT_PACKS[pack];

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [{
        price_data: {
          currency: 'jpy',
          product_data: {
            name: `Terroir HUB - ${selected.name}`,
            description: `AIサクラ追加クレジット ${selected.credits}回分`,
          },
          unit_amount: selected.price,
        },
        quantity: 1,
      }],
      metadata: {
        user_id: user.id,
        credits: String(selected.credits),
        pack: pack,
      },
      success_url: `${req.headers.origin || 'https://sake.terroirhub.com'}/?credit_purchased=${selected.credits}`,
      cancel_url: `${req.headers.origin || 'https://sake.terroirhub.com'}/`,
    });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error('Stripe checkout error:', err.message);
    return res.status(500).json({ error: 'Checkout failed' });
  }
};
