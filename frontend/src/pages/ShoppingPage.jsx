import React, { useEffect, useMemo, useState } from 'react'
import { fetchSupermarkets, compareBasket } from '../api'
import ShoppingList from '../components/ShoppingList'
import SupermarketsList from '../components/SupermarketsList'
import Results from '../components/Results'
import LoadingIndicator from '../components/LoadingIndicator'
import ErrorMessage from '../components/ErrorMessage'

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

  // Validation: At least 1 item and 1 store required
  const canCompare = useMemo(() => {
    return items.length > 0 && selectedStores.length > 0
  }, [items.length, selectedStores.length])

  const handleCompare = async () => {
    setError('')
    setResults(null)

    // Validate: No empty items
    if (!items.length) {
      setError('Please add at least one item to compare.')
      return
    }

    // Validate: At least 1 store selected
    if (!selectedStores.length) {
      setError('Please select at least one supermarket to compare.')
      return
    }

    setComparing(true)
    try {
      const resp = await compareBasket(items, selectedStores)
      setResults(resp)
    } catch (e) {
      setError(e.message || 'Failed to compare prices. Please try again.')
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
      <ErrorMessage message={error} type="error" />
      <LoadingIndicator isLoading={comparing} message="Comparing prices..." />

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
          canCompare={canCompare}
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
