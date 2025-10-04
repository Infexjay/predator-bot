import { useState, useEffect, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import './index.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

function App() {
  const [symbol, setSymbol] = useState('BTC-USD');
  const [prediction, setPrediction] = useState({ signal: 'N/A', confidence: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retrainStatus, setRetrainStatus] = useState('');
  const [modelInfo, setModelInfo] = useState(null);
  const [botStatus, setBotStatus] = useState('INACTIVE');
  const [isBotLoading, setIsBotLoading] = useState(true);
  const [marketData, setMarketData] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const API_URL = 'http://127.0.0.1:8000';

  const fetchModelInfo = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/model-info`);
      if (!response.ok) throw new Error('Failed to fetch model info');
      const data = await response.json();
      setModelInfo(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const fetchBotStatus = useCallback(async () => {
    setIsBotLoading(true);
    try {
      const response = await fetch(`${API_URL}/bot/status`);
      if (!response.ok) throw new Error('Failed to fetch bot status');
      const data = await response.json();
      setBotStatus(data.status);
    } catch (e) {
      console.error(e);
      setBotStatus('ERROR');
    } finally {
      setIsBotLoading(false);
    }
  }, []);

  const fetchMarketData = useCallback(async () => {
    if (!symbol) return;
    try {
      const response = await fetch(`${API_URL}/market/${symbol}?period=1d&interval=15m`);
      if (!response.ok) throw new Error(`Market data fetch error! status: ${response.status}`);
      const data = await response.json();
      setMarketData(data);
    } catch (e) {
      console.error(e);
      setMarketData([]);
    }
  }, [symbol]);

  useEffect(() => {
    fetchModelInfo();
    fetchBotStatus();
    fetchMarketData();
  }, [fetchModelInfo, fetchBotStatus, fetchMarketData]);

  const handleFetchPrediction = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
      });
      if (!response.ok) throw new Error(`Prediction error! status: ${response.status}`);
      const data = await response.json();
      setPrediction(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetrainModel = async () => {
    setRetrainStatus('Retraining initiated...');
    try {
      const response = await fetch(`${API_URL}/retrain`, { method: 'POST' });
      if (!response.ok) throw new Error(`Retrain error! status: ${response.status}`);
      const data = await response.json();
      setRetrainStatus(data.message || 'Request sent. Refresh model info when complete.');
    } catch (e) {
      setRetrainStatus(`Error: ${e.message}`);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus('');
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }
    setUploadStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_URL}/upload-data`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      const data = await response.json();
      setUploadStatus(data.message || 'Upload successful!');
      setSelectedFile(null); // Clear file input
    } catch (e) {
      setUploadStatus(`Error: ${e.message}`);
    }
  };

  const handleBotAction = async (action) => {
    setIsBotLoading(true);
    try {
        const response = await fetch(`${API_URL}/bot/${action}`, { method: 'POST'});
        if (!response.ok) throw new Error(`Bot ${action} error!`);
        const data = await response.json();
        setBotStatus(data.status);
    } catch (e) {
        console.error(e);
    } finally {
        setIsBotLoading(false);
    }
  }

  const chartData = {
    labels: marketData.map(d => new Date(d.Datetime)),
    datasets: [
      {
        label: `${symbol} Price (USD)`,
        data: marketData.map(d => d.Close),
        borderColor: '#06b6d4',
        backgroundColor: '#06b6d420',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: { unit: 'hour', tooltipFormat: 'MMM d, h:mm a' },
        grid: { color: '#ffffff10' },
        ticks: { color: '#9ca3af' },
      },
      y: {
        grid: { color: '#ffffff10' },
        ticks: { color: '#9ca3af' },
      },
    },
    plugins: {
      legend: { display: false },
    },
  };

  const BotStatusIndicator = ({ status }) => (
    <div className="flex items-center space-x-2">
      <span className={`h-3 w-3 rounded-full ${status === 'ACTIVE' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
      <span className="font-mono text-sm">{status}</span>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-gray-300 flex">
      {/* <!-- Sidebar --> */}
      <aside className="w-80 bg-gray-900/80 backdrop-blur-sm p-6 flex flex-col space-y-6 border-r border-gray-700/50">
        <h1 className="text-2xl font-bold text-cyan-400">Predator</h1>

        {/* Bot Control */}
        <div className="bg-gray-800/50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-gray-200 mb-3">Bot Control</h2>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm">Status</span>
            {isBotLoading ? <span className="text-yellow-400 text-sm">...</span> : <BotStatusIndicator status={botStatus} />}
          </div>
          <div className="flex space-x-2">
            <button onClick={() => handleBotAction('start')} disabled={botStatus === 'ACTIVE' || isBotLoading} className="btn-primary w-full bg-green-600 hover:bg-green-700">Start</button>
            <button onClick={() => handleBotAction('stop')} disabled={botStatus === 'INACTIVE' || isBotLoading} className="btn-primary w-full bg-red-600 hover:bg-red-700">Stop</button>
          </div>
        </div>

        {/* AI Prediction */}
        <div className="bg-gray-800/50 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-gray-200 mb-3">AI Prediction</h2>
          <div className="flex space-x-2 mb-2">
            <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="Symbol" className="input-primary w-full"/>
            <button onClick={handleFetchPrediction} disabled={isLoading} className="btn-primary bg-cyan-600 hover:bg-cyan-700">{isLoading ? '...' : 'Get'}</button>
          </div>
          {error && <p className="text-red-500 text-xs">Error: {error}</p>}
          <div className="text-center mt-3">
            <p className="text-sm">Signal: <span className={`font-bold text-xl ${prediction.signal === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>{prediction.signal}</span></p>
            <p className="text-xs mt-1">Confidence: <span className="font-semibold text-cyan-400">{ (prediction.confidence * 100).toFixed(2) }%</span></p>
          </div>
        </div>

        {/* Model Management */}
        <div className="bg-gray-800/50 p-4 rounded-lg flex-grow">
          <h2 className="text-lg font-semibold text-gray-200 mb-3">Model Management</h2>
          <div className="space-y-2 text-xs font-mono">
            {modelInfo ? (
              <>
                <p>Accuracy: <span className="text-cyan-400">{(modelInfo.accuracy * 100).toFixed(2)}%</span></p>
                <p>Last Trained: <span className="text-cyan-400">{new Date(modelInfo.last_trained).toLocaleDateString()}</span></p>
                <p>Symbols: <span className="text-cyan-400">{modelInfo.symbols_used?.length}</span></p>
              </>
            ) : <p>Loading model info...</p>}
          </div>
          <div className="flex space-x-2 mt-4">
            <button onClick={handleRetrainModel} className="btn-primary w-full bg-blue-600 hover:bg-blue-700">Retrain</button>
            <button onClick={fetchModelInfo} className="btn-primary bg-gray-600 hover:bg-gray-700">&#x21bb;</button>
          </div>
          {retrainStatus && <p className="mt-2 text-xs text-gray-400">{retrainStatus}</p>}

          {/* Data Upload Section */}
          <div className="mt-4 pt-4 border-t border-gray-700/50">
             <h3 className="text-md font-semibold text-gray-300 mb-2">Upload Custom Data</h3>
             <div className="space-y-2">
                <input
                    type="file"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
                    accept=".csv"
                />
                <button
                    onClick={handleFileUpload}
                    disabled={!selectedFile}
                    className="btn-primary w-full bg-purple-600 hover:bg-purple-700"
                >
                    Upload CSV
                </button>
             </div>
             {uploadStatus && <p className="mt-2 text-xs text-gray-400">{uploadStatus}</p>}
          </div>
        </div>
      </aside>

      {/* <!-- Main Content --> */}
      <main className="flex-1 p-6">
        <div className="h-full w-full bg-gray-800/30 rounded-lg p-4">
          <div className="h-full w-full">
            {marketData.length > 0 ? (
              <Line options={chartOptions} data={chartData} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p>Loading market data for {symbol}...</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App;