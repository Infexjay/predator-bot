import { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [symbol, setSymbol] = useState('BTC-USD');
  const [prediction, setPrediction] = useState({ signal: 'N/A', confidence: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retrainStatus, setRetrainStatus] = useState('');
  const [modelInfo, setModelInfo] = useState(null);
  const [botStatus, setBotStatus] = useState('INACTIVE'); // 'ACTIVE' or 'INACTIVE'
  const [isBotLoading, setIsBotLoading] = useState(true);

  const API_URL = 'http://127.0.0.1:8000';

  const fetchModelInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/model-info`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setModelInfo(data);
    } catch (e) {
      console.error("Failed to fetch model info:", e);
      setModelInfo(null); // Reset on error
    }
  };

  const fetchBotStatus = async () => {
    setIsBotLoading(true);
    // This will be implemented in a future step
    // For now, we'll just simulate a delay and set the status
    setTimeout(() => {
        // const response = await fetch(`${API_URL}/bot/status`);
        // const data = await response.json();
        // setBotStatus(data.status);
        setBotStatus('INACTIVE'); // Default to INACTIVE for now
        setIsBotLoading(false);
    }, 500);
  };

  useEffect(() => {
    fetchModelInfo();
    fetchBotStatus();
  }, []);

  const handleFetchPrediction = async () => {
    setIsLoading(true);
    setError(null);
    setPrediction({ signal: 'N/A', confidence: 0 });

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetrainModel = async () => {
    setRetrainStatus('Retraining started...');
    try {
      const response = await fetch(`${API_URL}/retrain`, { method: 'POST' });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRetrainStatus(data.message || 'Request sent. Refresh model info when complete.');
    } catch (e) {
      setRetrainStatus(`Error: ${e.message}`);
    }
  };

  const handleStartBot = async () => {
    // To be implemented with backend
    setBotStatus('ACTIVE');
    console.log("Bot start request sent.");
  };

  const handleStopBot = async () => {
    // To be implemented with backend
    setBotStatus('INACTIVE');
    console.log("Bot stop request sent.");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 p-4 shadow-md">
        <h1 className="text-3xl font-bold text-center text-cyan-400">Predator Trading Bot</h1>
      </header>
      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">

          {/* AI Prediction Card */}
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">AI Prediction</h2>
            <div className="flex space-x-2 mb-4">
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                placeholder="Enter symbol (e.g., BTC-USD)"
                className="bg-gray-700 text-white p-2 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
              <button
                onClick={handleFetchPrediction}
                disabled={isLoading}
                className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-500"
              >
                {isLoading ? '...' : 'Get'}
              </button>
            </div>
            {error && <p className="text-red-500">Error: {error}</p>}
            <p className="text-lg">Signal: <span className={`font-bold ${prediction.signal === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>{prediction.signal}</span></p>
            <p className="text-md mt-2">Confidence: <span className="font-semibold">{ (prediction.confidence * 100).toFixed(2) }%</span></p>
          </div>

          {/* Model Management Card */}
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Model Management</h2>
            <div className="space-y-3 text-sm">
                {modelInfo ? (
                    <>
                        <p>Last Trained: <span className="font-mono">{new Date(modelInfo.last_trained).toLocaleString()}</span></p>
                        <p>Accuracy: <span className="font-mono">{(modelInfo.accuracy * 100).toFixed(2)}%</span></p>
                        <p>Symbols: <span className="font-mono">{modelInfo.symbols_used.length}</span></p>
                    </>
                ) : <p>Loading model info...</p>}
            </div>
            <div className="flex space-x-2 mt-4">
                <button onClick={handleRetrainModel} className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full">
                    Retrain Model
                </button>
                <button onClick={fetchModelInfo} className="bg-gray-600 hover:bg-gray-700 text-white font-bold p-2 rounded">
                    &#x21bb;
                </button>
            </div>
            {retrainStatus && <p className="mt-4 text-sm text-gray-400">{retrainStatus}</p>}
          </div>

          {/* Bot Control Card */}
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-cyan-300">Bot Control</h2>
            <div className="flex items-center justify-between">
              <span className="text-lg">Status:</span>
              {isBotLoading ? <span className="text-yellow-400">Loading...</span> :
                <span className={`font-bold ${botStatus === 'ACTIVE' ? 'text-green-500' : 'text-red-500'}`}>
                  {botStatus}
                </span>
              }
            </div>
            <div className="mt-4 flex space-x-4">
              <button onClick={handleStartBot} disabled={botStatus === 'ACTIVE' || isBotLoading} className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-full disabled:bg-gray-500">Start</button>
              <button onClick={handleStopBot} disabled={botStatus === 'INACTIVE' || isBotLoading} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded w-full disabled:bg-gray-500">Stop</button>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}

export default App;