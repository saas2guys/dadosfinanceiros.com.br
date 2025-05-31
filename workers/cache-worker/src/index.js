const CACHE = {
  WEEK: 604800,
  DAY: 86400,
  HOUR_12: 43200,
  HOUR_6: 21600,
  HOUR_4: 14400,
  HOUR_2: 7200,
  HOUR_1: 3600,
  MIN_30: 1800,
  MIN_15: 900,
  MIN_5: 300,
  PERMANENT: 31536000,
  NONE: 0
}

export default {
  async fetch(request, env, ctx) {
    const BACKEND = env.BACKEND_URL || 'https://api.financialdata.online'
    
    const url = new URL(request.url)

    if (request.method === 'OPTIONS') return corsResponse()
    if (url.pathname === '/health') return Response.json({status: 'ok'})

    if (request.method !== 'GET' || url.searchParams.has('nocache')) {
      return proxy(request, BACKEND)
    }

    const ttl = getCacheTTL(url.pathname, url.searchParams)
    if (ttl === CACHE.NONE) return proxy(request, BACKEND)

    return getCachedResponse(request, ttl, BACKEND)
  }
}

function getCacheTTL(path, params) {
  const today = new Date().toISOString().split('T')[0]

  const dateParam = params.get('date') || params.get('from') || path.match(/(\d{4}-\d{2}-\d{2})/)?.[1]
  const toParam = params.get('to')
  const isPastData = (dateParam && dateParam < today) || (toParam && toParam < today)

  if (path === '/v1/reference/tickers/types') return CACHE.WEEK
  if (path.match(/^\/v1\/reference\/options\/contracts\/[^\/]+$/)) return CACHE.PERMANENT
  if (path.match(/^\/v1\/reference\/indices\/[^\/]+$/)) return CACHE.DAY

  if (path.match(/^\/v1\/reference\/tickers\/[^\/]+$/) && !path.includes('?')) return CACHE.HOUR_6
  if (path === '/v1/reference/tickers' || path.startsWith('/v1/reference/tickers?')) return CACHE.HOUR_4
  if (path === '/v1/reference/options/contracts') return CACHE.HOUR_2
  if (path === '/v1/reference/indices') return CACHE.HOUR_12
  if (path.includes('/v1/meta/symbols/') && path.endsWith('/company')) return CACHE.HOUR_6
  if (path.includes('/v1/meta/symbols/') && path.endsWith('/analysts')) return CACHE.HOUR_1

  if (isPastData) {
    if (path.includes('/v1/aggs/ticker/') && path.includes('/range/')) return CACHE.PERMANENT
    if (path.includes('/v1/open-close/') && !path.includes('/today')) return CACHE.PERMANENT
    if (path.includes('/v1/trades/')) return CACHE.PERMANENT
    if (path.includes('/v1/quotes/')) return CACHE.PERMANENT
    if (path.includes('/v1/indicators/treasury-yields')) return CACHE.PERMANENT
  }

  if (path.includes('/v1/conversion/')) {
    return isMarketHours() ? CACHE.MIN_15 : CACHE.MIN_30
  }

  if (path.includes('/v1/snapshot')) return CACHE.NONE
  if (path.includes('/v1/last/trade/') || path.includes('/v1/last/nbbo/')) return CACHE.NONE
  if (path.includes('/v1/aggs/ticker/') && path.includes('/prev')) return CACHE.NONE
  if (path.includes('/v1/open-close/') && path.includes('/today')) return CACHE.NONE

  return CACHE.MIN_5
}

function isMarketHours() {
  const et = new Date().toLocaleString("en-US", {timeZone: "America/New_York"})
  const hour = new Date(et).getHours()
  const day = new Date(et).getDay()
  return day >= 1 && day <= 5 && hour >= 9 && hour < 16
}

async function getCachedResponse(request, ttl, BACKEND) {
  const cache = caches.default

  let response = await cache.match(request)
  if (response) {
    const age = Math.floor((Date.now() - new Date(response.headers.get('cached-at'))) / 1000)
    response = new Response(response.body, response)
    response.headers.set('cache-status', 'HIT')
    response.headers.set('cache-age', age.toString())
    return response
  }

  response = await proxy(request, BACKEND)

  if (response.ok) {
    const clone = response.clone()
    clone.headers.set('cache-control', `max-age=${ttl}`)
    clone.headers.set('cached-at', new Date().toISOString())
    await cache.put(request, clone)
    response.headers.set('cache-status', 'MISS')
  }

  return response
}

async function proxy(request, BACKEND) {
  const url = new URL(request.url)

  try {
    const response = await fetch(BACKEND + url.pathname + url.search, {
      method: request.method,
      headers: request.headers,
      body: request.body
    })

    return new Response(response.body, {
      status: response.status,
      headers: {
        ...Object.fromEntries(response.headers),
        'access-control-allow-origin': '*'
      }
    })
  } catch (error) {
    return Response.json({error: error.message}, {
      status: 502,
      headers: {'access-control-allow-origin': '*'}
    })
  }
}

function corsResponse() {
  return new Response(null, {
    status: 200,
    headers: {
      'access-control-allow-origin': '*',
      'access-control-allow-methods': '*',
      'access-control-allow-headers': '*'
    }
  })
}
