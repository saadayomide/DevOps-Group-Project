import React, { useEffect, useMemo, useState } from 'react'
import { fetchSupermarkets, compareBasket } from '../api'
import ShoppingList from '../components/ShoppingList'
import SupermarketsList from '../components/SupermarketsList'
import Results from '../components/Results'

export default function ShoppingPage() {
  const [supermarkets, setSupermarkets] = useState([])
  const [selectedStores, setSelectedStores] = useState([])
  const [items, setItems] = useState([])
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [loadingStores, setLoadingStores] = useState(false)
  const [comparing, setComparing] = useState(false)

  useEffect(() => {
    setLoadingStores(true)
    fetchSupermarkets()
      .then((list) => {
        setSupermarkets(list)
        setSelectedStores(list.map((s) => s.name))
      })
      .catch((e) => setError(`Failed to load supermarkets: ${e.message}`))
      .finally(() => setLoadingStores(false))
  }, [])

  const handleCompare = async () => {
    setError('')
    setResults(null)
    if (!items.length) {
      setError('Add at least one item to compare.')
      return
    }
    if (!selectedStores.length) {
      setError('Select at least one supermarket.')
      return
    }
    setComparing(true)
    try {
      const resp = await compareBasket(items, selectedStores)
      setResults(resp)
    } catch (e) {
      setError(e.message)
    } finally {
      setComparing(false)
    }
  }

  const bestStore = useMemo(() => {
    if (!results?.storeTotals?.length) return null
    return [...results.storeTotals].sort((a, b) => Number(a.total) - Number(b.total))[0]
  }, [results])

  const savings = useMemo(() => {
    if (!results?.storeTotals || results.storeTotals.length < 2) return null
    const sorted = [...results.storeTotals].sort((a, b) => Number(a.total) - Number(b.total))
    const cheapest = Number(sorted[0].total)
    const next = Number(sorted[1].total)
    if (Number.isNaN(cheapest) || Number.isNaN(next)) return null
    return Math.max(0, next - cheapest)
  }, [results])

  return (
    <div className="dashboard">
      {error && <div className="alert error">{error}</div>}
      {comparing && <div className="alert info">Comparing prices...</div>}

      <div className="dashboard-grid">
        <ShoppingList items={items} setItems={setItems} />
        <SupermarketsList
          supermarkets={supermarkets}
          selected={selectedStores}
          setSelected={setSelectedStores}
          loading={loadingStores}
          onCompare={handleCompare}
          onResetSelection={() => setSelectedStores([])}
          comparing={comparing}
        />
        <Results
          results={results}
          comparing={comparing}
          bestStore={bestStore}
          savings={savings}
        />
      </div>
    </div>
  )
}
