import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// Add declaration for the process.env
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
    }
  }
}

interface Producto {
  c_ClaveProdServ: string;
  Descripcion: string;
  Palabras_similares: string;
  tipo_num: number;
  Tipo: string;
  Div_num: number;
  Division: string;
  Grupo_num: number;
  Grupo: string;
  Clase_num: number;
  Clase: string;
}

function App() {
  const [busqueda, setBusqueda] = useState<string>('');
  const [resultados, setResultados] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);
  const [isMobile, setIsMobile] = useState<boolean>(false);
  
  // Determine the API base URL based on the current hostname
  const isProduction = window.location.hostname !== 'localhost';
  const apiBaseUrl = isProduction 
    ? 'https://api.tecfis.com'
    : 'http://localhost:8080';

  useEffect(() => {
    // Check if screen is mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 960);
    };
    
    // Initial check
    checkMobile();
    
    // Add event listener for resize
    window.addEventListener('resize', checkMobile);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const buscarProductos = async () => {
    if (!busqueda.trim()) return;
    
    try {
      setCargando(true);
      setError(null);
      const response = await axios.get(`${apiBaseUrl}/search_clave_prod_and_taxonomy?q=${encodeURIComponent(busqueda)}`);
      setResultados(response.data);
      setProductoSeleccionado(null); // Reset selected product when searching
    } catch (err) {
      setError('Error al buscar productos. Por favor, intente nuevamente.');
      console.error('Error buscando productos:', err);
    } finally {
      setCargando(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      buscarProductos();
    }
  };

  const handleProductClick = (producto: Producto) => {
    // Toggle product selection
    if (productoSeleccionado?.c_ClaveProdServ === producto.c_ClaveProdServ) {
      setProductoSeleccionado(null);
    } else {
      setProductoSeleccionado(producto);
      
      // Scroll to the selected product on mobile
      if (isMobile) {
        setTimeout(() => {
          const selectedElement = document.getElementById(`producto-${producto.c_ClaveProdServ}`);
          if (selectedElement) {
            selectedElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 100);
      }
    }
  };

  const renderProductoDetalle = () => {
    if (!productoSeleccionado) return null;
    
    return (
      <div id="detalle-producto" className="detalle-container">
        <h2>Detalle del Producto</h2>
        
        <div className="producto-header">
          <div className="producto-titulo">
            <h3>{productoSeleccionado.Descripcion}</h3>
            <div className="producto-clave-detalle">Clave: {productoSeleccionado.c_ClaveProdServ}</div>
          </div>
        </div>
        
        <div className="taxonomy-container">
          <div className="taxonomy-title">Clasificación Jerárquica</div>
          
          <div className="taxonomy-tree">
            <div className="taxonomy-level">
              <div className="level-label">Tipo ({productoSeleccionado.tipo_num}):</div>
              <div className="level-value">{productoSeleccionado.Tipo}</div>
            </div>
            
            <div className="taxonomy-arrow">↓</div>
            
            <div className="taxonomy-level">
              <div className="level-label">División ({productoSeleccionado.Div_num}):</div>
              <div className="level-value">{productoSeleccionado.Division}</div>
            </div>
            
            <div className="taxonomy-arrow">↓</div>
            
            <div className="taxonomy-level">
              <div className="level-label">Grupo ({productoSeleccionado.Grupo_num}):</div>
              <div className="level-value">{productoSeleccionado.Grupo}</div>
            </div>
            
            <div className="taxonomy-arrow">↓</div>
            
            <div className="taxonomy-level">
              <div className="level-label">Clase ({productoSeleccionado.Clase_num}):</div>
              <div className="level-value">{productoSeleccionado.Clase}</div>
            </div>
            
            <div className="taxonomy-arrow">↓</div>
            
            <div className="taxonomy-level final-level">
              <div className="level-label">Producto:</div>
              <div className="level-value">{productoSeleccionado.Descripcion}</div>
            </div>
          </div>
        </div>
        
        <div className="palabras-similares">
          <h4>Palabras Similares:</h4>
          <p>{productoSeleccionado.Palabras_similares}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Buscador de Taxonomía SAT</h1>
        <p className="subtitulo">Busca productos y servicios en el catálogo del SAT</p>
      </header>

      <div className="search-container">
        <div className="search-input-container">
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Buscar producto o servicio..."
            className="search-input"
          />
          <button 
            onClick={buscarProductos} 
            className="search-button"
            disabled={cargando || !busqueda.trim()}
          >
            {cargando ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
      </div>

      <div className="content-container">
        <div className="resultados-container">
          <h2>Resultados de la búsqueda</h2>
          
          {cargando ? (
            <div className="loading-spinner">Cargando resultados...</div>
          ) : resultados.length > 0 ? (
            <ul className="resultados-lista">
              {resultados.map((producto) => (
                <li key={producto.c_ClaveProdServ}>
                  <div 
                    id={`producto-${producto.c_ClaveProdServ}`}
                    className={`resultado-item ${productoSeleccionado?.c_ClaveProdServ === producto.c_ClaveProdServ ? 'selected' : ''}`}
                    onClick={() => handleProductClick(producto)}
                  >
                    <div className="producto-clave">{producto.c_ClaveProdServ}</div>
                    <div className="producto-descripcion">{producto.Descripcion}</div>
                  </div>
                  
                  {/* Show product details inline on mobile */}
                  {isMobile && 
                    productoSeleccionado?.c_ClaveProdServ === producto.c_ClaveProdServ && 
                    <div className="inline-details">
                      {renderProductoDetalle()}
                    </div>
                  }
                </li>
              ))}
            </ul>
          ) : busqueda.trim() ? (
            <div className="no-resultados">No se encontraron resultados para "{busqueda}"</div>
          ) : (
            <div className="instrucciones-busqueda">
              Ingrese un término de búsqueda para encontrar productos y servicios.
              <div className="ejemplo">Por ejemplo: "chancho", "computadora", "servicio"</div>
            </div>
          )}
        </div>

        {/* Show product details in separate container on desktop */}
        {!isMobile && productoSeleccionado && renderProductoDetalle()}
      </div>
      
      <footer className="app-footer">
        <p>Buscador de Taxonomía SAT © 2023 - Consulta el catálogo de productos y servicios</p>
      </footer>
    </div>
  )
}

export default App
