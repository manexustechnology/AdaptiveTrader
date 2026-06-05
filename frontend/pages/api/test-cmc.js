// API route to call backend Python service
export default async function handler(req, res) {
  const { symbol = 'BTC' } = req.query

  try {
    // Call Python backend API
    const backendUrl = process.env.BACKEND_API || 'http://195.26.240.233:8000'
    const response = await fetch(`${backendUrl}/api/signal/${symbol}`)
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    res.status(200).json(data)
  } catch (error) {
    console.error('Error calling backend:', error)
    res.status(500).json({ 
      error: 'Failed to fetch data from backend',
      details: error.message 
    })
  }
}
