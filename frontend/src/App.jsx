import './App.css'

function App() {

  return (
    <>
      <div className="min-h-screen bg-gray-900 text-white">
        <header className="bg-gray-800 p-4 shadow-md">
          <h1 className="text-3xl font-bold text-center text-cyan-400">Predator Trading Bot</h1>
        </header>
        <main className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* <!-- Bot Control Card --> */}
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Bot Control</h2>
              <div className="flex items-center justify-between">
                <span className="text-lg">Status:</span>
                <span className="text-green-500 font-bold">ACTIVE</span>
              </div>
              <div className="mt-4 flex space-x-4">
                <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-full">Start</button>
                <button className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded w-full">Stop</button>
              </div>
            </div>

            {/* <!-- Market Overview Card --> */}
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Market Overview</h2>
              <div className="flex justify-between">
                <span>BTC/USDT:</span>
                <span className="text-green-400">$68,123.45</span>
              </div>
              <div className="flex justify-between mt-2">
                <span>ETH/USDT:</span>
                <span className="text-red-400">$3,456.78</span>
              </div>
            </div>

            {/* <!-- AI Prediction Card --> */}
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4 text-cyan-300">AI Prediction</h2>
              <p className="text-lg">Signal: <span className="font-bold text-yellow-400">HOLD</span></p>
              <p className="text-md mt-2">Confidence: <span className="font-semibold">62%</span></p>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}

export default App