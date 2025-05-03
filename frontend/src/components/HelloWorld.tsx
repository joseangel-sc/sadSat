import { useState, useEffect } from 'react';
import axios from 'axios';

interface HelloWorldResponse {
  message: string;
  timestamp: string;
}

const HelloWorld = () => {
  const [data, setData] = useState<HelloWorldResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get<HelloWorldResponse>('http://localhost:8000/hello_world');
        setData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch data from the server. Make sure the backend is running.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Poll every 10 seconds to show the time updating
    const intervalId = setInterval(fetchData, 10000);
    
    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  if (loading && !data) {
    return <div className="loading">Loading data from server...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <h2>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="hello-world">
      <h2>{data?.message}</h2>
      <p>Current server time: {data?.timestamp}</p>
      <p className="timestamp-info">
        (The timestamp is refreshed every 10 seconds)
      </p>
    </div>
  );
};

export default HelloWorld;

