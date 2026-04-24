const Stripe = require('stripe');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  let event;

  try {
    const sig = req.headers['stripe-signature'];
    const rawBody = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    event = stripe.webhooks.constructEvent(rawBody, sig, endpointSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).json({ error: 'Invalid signature' });
  }

  // Supabase helper
  async function supabasePost(path, body) {
    if (!supabaseUrl || !supabaseKey) return;
    return fetch(`${supabaseUrl}/rest/v1/${path}`, {
      method: 'POST',
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
      },
      body: JSON.stringify(body),
    });
  }

  async function supabasePatch(table, id, body) {
    if (!supabaseUrl || !supabaseKey) return;
    return fetch(`${supabaseUrl}/rest/v1/${table}?id=eq.${id}`, {
      method: 'PATCH',
      headers: {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
      },
      body: JSON.stringify(body),
    });
  }

  try {
    switch (event.type) {
      // ── クレジット購入完了 ──
      case 'checkout.session.completed': {
        const session = event.data.object;
        const userId = session.metadata?.user_id;
        const credits = parseInt(session.metadata?.credits || '0', 10);
        const plan = session.metadata?.plan;

        // クレジット追加購入
        if (userId && credits > 0) {
          await supabasePost('credit_purchases', {
            user_id: userId,
            credits: credits,
            amount_jpy: session.amount_total,
            stripe_session_id: session.id,
          });
          await supabasePost('rpc/add_bonus_credits', {
            p_user_id: userId,
            p_credits: credits,
          });
          console.log(`Added ${credits} bonus credits to ${userId}`);
        }

        // サブスク開始
        if (userId && plan) {
          await supabasePatch('profiles', userId, {
            plan: plan,
            stripe_customer_id: session.customer,
          });
          console.log(`Activated plan ${plan} for ${userId}`);
        }
        break;
      }

      // ── サブスク更新（プラン変更） ──
      case 'customer.subscription.updated': {
        const sub = event.data.object;
        const userId = sub.metadata?.user_id;
        const plan = sub.metadata?.plan;
        if (userId && plan) {
          const status = sub.status;
          if (status === 'active') {
            await supabasePatch('profiles', userId, { plan: plan });
            console.log(`Updated plan to ${plan} for ${userId}`);
          } else if (status === 'past_due' || status === 'unpaid') {
            await supabasePatch('profiles', userId, { plan: 'free' });
            console.log(`Downgraded to free (${status}) for ${userId}`);
          }
        }
        break;
      }

      // ── サブスク解約 ──
      case 'customer.subscription.deleted': {
        const sub = event.data.object;
        const userId = sub.metadata?.user_id;
        if (userId) {
          await supabasePatch('profiles', userId, { plan: 'free' });
          console.log(`Cancelled subscription for ${userId}`);
        }
        break;
      }
    }
  } catch (err) {
    console.error('Webhook processing error:', err.message);
  }

  return res.status(200).json({ received: true });
};

module.exports.config = {
  api: { bodyParser: false },
};
