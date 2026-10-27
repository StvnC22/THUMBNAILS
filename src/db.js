const DB_NAME = 'bannegfx-store'
const DB_VERSION = 1

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains('orders')) {
        db.createObjectStore('orders', { keyPath: 'id' })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

export async function saveOrder(order) {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('orders', 'readwrite')
    tx.objectStore('orders').put(order)
    tx.oncomplete = () => resolve(order)
    tx.onerror = () => reject(tx.error)
  })
}
