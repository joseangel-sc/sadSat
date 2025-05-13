import { useState, useEffect } from 'react';
import axios from 'axios';

interface DataViewerProps {
  // Removed onRefresh parameter as it's not used
}

const DataViewer = ({}: DataViewerProps) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/show_latest');
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data from the server. Make sure the backend is running and data exists.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const renderDataContent = () => {
    if (!data) return null;
    
    // Check if data contains image URLs
    if (data.image_url || (typeof data === 'object' && data.images)) {
      return (
        <div className="image-display">
          {data.image_url && (
            <div className="image-item">
              <img src={data.image_url} alt="Data" className="data-image" />
            </div>
          )}
          {data.images && Array.isArray(data.images) && data.images.map((img: string, index: number) => (
            <div key={index} className="image-item">
              <img src={img} alt={`Image ${index + 1}`} className="data-image" />
            </div>
          ))}
        </div>
      );
    }
    
    // Default to JSON display
    return (
      <div className="json-display">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className="data-viewer" style={{ color: 'black' }}>
      <h2>Catalog Data</h2>
      <div className="button-container" style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
        <button 
          onClick={fetchData} 
          className="show-button"
          disabled={loading}
          style={{ color: 'black' }}
        >
          {loading ? 'Loading...' : 'Show Latest Data'}
        </button>
      </div>
      
      {error && (
        <div className="error" style={{ color: 'red', marginBottom: '10px' }}>
          <p>{error}</p>
        </div>
      )}
      
      {loading ? (
        <div className="loading">Loading data from server...</div>
      ) : (
        <div className="data-container">
          {renderDataContent()}
        </div>
      )}
    </div>
  );
};

export default DataViewer; 