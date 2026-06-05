import React, { useState, useEffect } from 'react';
import { Search, Plane, AlertTriangle, CheckCircle, Clock, TrendingUp, Thermometer, Droplets, RefreshCw, X, ChevronRight, Info, Zap, Shield, Trash2 } from 'lucide-react';

// Inline styles - No Tailwind needed!
const styles = {
  app: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%)',
    color: '#ffffff',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  header: {
    borderBottom: '1px solid rgba(255,255,255,0.1)',
    backdropFilter: 'blur(20px)',
    backgroundColor: 'rgba(0,0,0,0.2)',
    padding: '1.5rem 2rem'
  },
  headerContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem'
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    margin: 0
  },
  subtitle: {
    fontSize: '0.75rem',
    color: '#22d3ee',
    fontWeight: '500'
  },
  nav: {
    display: 'flex',
    gap: '0.5rem'
  },
  navButton: {
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s',
    fontSize: '0.95rem',
    fontWeight: '500'
  },
  navButtonActive: {
    background: '#06b6d4',
    color: '#ffffff',
    boxShadow: '0 4px 14px rgba(6, 182, 212, 0.5)'
  },
  navButtonInactive: {
    background: 'transparent',
    color: '#9ca3af',
    border: '1px solid transparent'
  },
  main: {
    maxWidth: '1024px',
    margin: '0 auto',
    padding: '2rem 1rem'
  },
  card: {
    backdropFilter: 'blur(24px)',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: '1rem',
    border: '1px solid rgba(255,255,255,0.1)',
    padding: '2rem',
    boxShadow: '0 20px 25px -5px rgba(0,0,0,0.3)',
    marginBottom: '1.5rem'
  },
  searchForm: {
    display: 'flex',
    gap: '0.75rem',
    marginTop: '1.5rem'
  },
  input: {
    flex: 1,
    padding: '1rem 1rem 1rem 3rem',
    backgroundColor: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '0.75rem',
    color: '#ffffff',
    fontSize: '1rem',
    outline: 'none'
  },
  button: {
    padding: '1rem 2rem',
    background: 'linear-gradient(90deg, #06b6d4 0%, #3b82f6 100%)',
    color: '#ffffff',
    border: 'none',
    borderRadius: '0.75rem',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    transition: 'all 0.2s'
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed'
  },
  resultCard: {
    borderRadius: '1rem',
    overflow: 'hidden',
    border: '1px solid rgba(255,255,255,0.1)',
    backgroundColor: 'rgba(255,255,255,0.05)',
    backdropFilter: 'blur(24px)'
  },
  resultHeader: {
    background: 'linear-gradient(90deg, rgba(6,182,212,0.2) 0%, rgba(59,130,246,0.2) 100%)',
    padding: '1.5rem',
    borderBottom: '1px solid rgba(255,255,255,0.1)'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '1rem',
    marginTop: '1.5rem'
  },
  statCard: {
    backdropFilter: 'blur(8px)',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: '0.75rem',
    padding: '1rem',
    border: '1px solid rgba(255,255,255,0.1)'
  },
  riskIndicator: {
    borderRadius: '0.75rem',
    padding: '1.5rem',
    marginBottom: '1.5rem'
  },
  riskHigh: {
    backgroundColor: 'rgba(239,68,68,0.2)',
    border: '1px solid rgba(239,68,68,0.5)'
  },
  riskMedium: {
    backgroundColor: 'rgba(234,179,8,0.2)',
    border: '1px solid rgba(234,179,8,0.5)'
  },
  riskLow: {
    backgroundColor: 'rgba(34,197,94,0.2)',
    border: '1px solid rgba(34,197,94,0.5)'
  },
  progressBar: {
    height: '0.75rem',
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: '9999px',
    overflow: 'hidden',
    marginTop: '1rem',
    position: 'relative'
  },
  progressFill: {
    height: '100%',
    transition: 'width 1s ease-out',
    position: 'absolute',
    left: 0,
    top: 0
  },
  recommendationCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '0.75rem',
    padding: '1rem',
    marginBottom: '0.75rem'
  },
  flightCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '0.75rem',
    padding: '1.25rem',
    marginBottom: '1rem',
    transition: 'all 0.2s'
  },
  historyCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '0.75rem',
    padding: '1rem',
    marginBottom: '0.75rem',
    cursor: 'pointer',
    transition: 'all 0.2s'
  }
};

const FlightDelayApp = () => {
  const [flightNumber, setFlightNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [activeTab, setActiveTab] = useState('predict');
  const [error, setError] = useState(null);

  // Monitor and History states
  const [monitoredFlights, setMonitoredFlights] = useState([]);
  const [history, setHistory] = useState([]);

  // Load monitored flights and history from localStorage on mount
  useEffect(() => {
    const savedMonitored = localStorage.getItem('monitoredFlights');
    const savedHistory = localStorage.getItem('flightHistory');

    if (savedMonitored) {
      setMonitoredFlights(JSON.parse(savedMonitored));
    }
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('monitoredFlights', JSON.stringify(monitoredFlights));
  }, [monitoredFlights]);

  useEffect(() => {
    localStorage.setItem('flightHistory', JSON.stringify(history));
  }, [history]);

  const checkFlight = async (flightNum) => {
    setLoading(true);
    setError(null);
    setShowRecommendations(false);
    setRecommendations([]);

    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flight_number: flightNum })
      });

      const data = await response.json();

      if (data.success && data.data) {
        setPrediction(data.data);

        // Add to history
        const historyEntry = {
          ...data.data,
          timestamp: new Date().toISOString(),
          id: Date.now()
        };
        setHistory(prev => [historyEntry, ...prev.slice(0, 19)]); // Keep last 20
      } else {
        setError(data.error || 'Failed to retrieve flight data');
      }
    } catch (err) {
      console.error('API Error:', err);
      setError('Cannot connect to backend. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async (flightNum) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flight_number: flightNum })
      });

      const data = await response.json();

      if (data.success) {
        setRecommendations(data.recommendations || []);
        setShowRecommendations(true);
      } else {
        setError(data.error || 'Failed to get recommendations');
      }
    } catch (err) {
      console.error('API Error:', err);
      setError('Cannot connect to backend for recommendations.');
    } finally {
      setLoading(false);
    }
  };

  const addToMonitor = (flight) => {
    if (monitoredFlights.some(f => f.flight_number === flight.flight_number)) {
      alert(`${flight.flight_number} is already being monitored!`);
      return;
    }

    const monitoredFlight = {
      ...flight,
      addedAt: new Date().toISOString(),
      id: Date.now()
    };

    setMonitoredFlights(prev => [...prev, monitoredFlight]);
    alert(`✅ Now monitoring ${flight.flight_number}`);
  };

  const removeFromMonitor = (flightId) => {
    setMonitoredFlights(prev => prev.filter(f => f.id !== flightId));
  };

  const refreshMonitoredFlight = async (flightNum) => {
    await checkFlight(flightNum);
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      setHistory([]);
      localStorage.removeItem('flightHistory');
    }
  };

  const loadFromHistory = (historyItem) => {
    setPrediction(historyItem);
    setActiveTab('predict');
    setShowRecommendations(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (flightNumber.trim()) {
      checkFlight(flightNumber.trim().toUpperCase());
    }
  };

  const getRiskLevel = (prob) => {
    if (prob >= 0.75) return { level: 'CRITICAL', color: 'red', style: styles.riskHigh };
    if (prob >= 0.45) return { level: 'WARNING', color: 'yellow', style: styles.riskMedium };
    return { level: 'LOW RISK', color: 'green', style: styles.riskLow };
  };

  const getRiskColor = (prob) => {
    if (prob >= 0.75) return '#ef4444';
    if (prob >= 0.45) return '#eab308';
    return '#22c55e';
  };

  const getRecommendationIcon = (type) => {
    const iconProps = { size: 20 };
    switch (type) {
      case 'CRITICAL': return <AlertTriangle {...iconProps} color="#ef4444" />;
      case 'ALERT': return <AlertTriangle {...iconProps} color="#f97316" />;
      case 'WARNING': return <Zap {...iconProps} color="#eab308" />;
      case 'INFO': return <Info {...iconProps} color="#3b82f6" />;
      case 'SUCCESS': return <CheckCircle {...iconProps} color="#22c55e" />;
      default: return <Info {...iconProps} />;
    }
  };

  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.logo}>
            <Plane size={32} color="#22d3ee" />
            <div>
              <h1 style={styles.title}>FlightPredict AI</h1>
              <p style={styles.subtitle}>Intelligent Delay Prediction</p>
            </div>
          </div>
          <nav style={styles.nav}>
            <button
              onClick={() => setActiveTab('predict')}
              style={{
                ...styles.navButton,
                ...(activeTab === 'predict' ? styles.navButtonActive : styles.navButtonInactive)
              }}
            >
              Predict
            </button>
            <button
              onClick={() => setActiveTab('monitor')}
              style={{
                ...styles.navButton,
                ...(activeTab === 'monitor' ? styles.navButtonActive : styles.navButtonInactive)
              }}
            >
              Monitor ({monitoredFlights.length})
            </button>
            <button
              onClick={() => setActiveTab('history')}
              style={{
                ...styles.navButton,
                ...(activeTab === 'history' ? styles.navButtonActive : styles.navButtonInactive)
              }}
            >
              History ({history.length})
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={styles.main}>
        {activeTab === 'predict' && (
          <>
            {/* Search Card */}
            <div style={styles.card}>
              <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                Check Flight Delay Risk
              </h2>
              <p style={{ color: '#9ca3af', marginBottom: '1.5rem' }}>
                Enter a flight number to get AI-powered delay predictions
              </p>

              <form onSubmit={handleSubmit} style={styles.searchForm}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Search
                    style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }}
                    size={20}
                  />
                  <input
                    type="text"
                    value={flightNumber}
                    onChange={(e) => setFlightNumber(e.target.value)}
                    placeholder="e.g., AA100, DL123, UA456"
                    style={styles.input}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !flightNumber.trim()}
                  style={{
                    ...styles.button,
                    ...(loading || !flightNumber.trim() ? styles.buttonDisabled : {})
                  }}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={20} style={{ animation: 'spin 1s linear infinite' }} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap size={20} />
                      Predict
                    </>
                  )}
                </button>
              </form>

              {error && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  backgroundColor: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.3)',
                  borderRadius: '0.5rem',
                  color: '#f87171',
                  display: 'flex',
                  gap: '0.75rem'
                }}>
                  <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '0.125rem' }} />
                  <div>
                    <p style={{ fontWeight: '600', marginBottom: '0.25rem' }}>Error</p>
                    <p style={{ fontSize: '0.875rem' }}>{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Results */}
            {prediction && (
              <>
                <div style={styles.resultCard}>
                  <div style={styles.resultHeader}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                          <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{prediction.flight_number}</span>
                          <span style={{
                            padding: '0.25rem 0.75rem',
                            backgroundColor: 'rgba(6,182,212,0.2)',
                            color: '#22d3ee',
                            borderRadius: '9999px',
                            fontSize: '0.875rem',
                            fontWeight: '500'
                          }}>
                            {prediction.airline}
                          </span>
                        </div>
                        <div style={{ color: '#d1d5db', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span>{prediction.route}</span>
                          <span style={{ color: '#6b7280' }}>•</span>
                          <span>{prediction.departure_time}</span>
                          <span style={{ color: '#6b7280' }}>•</span>
                          <span>{prediction.date}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => addToMonitor(prediction)}
                        style={{
                          padding: '0.5rem 1rem',
                          backgroundColor: 'rgba(6,182,212,0.2)',
                          color: '#22d3ee',
                          border: '1px solid rgba(6,182,212,0.3)',
                          borderRadius: '0.5rem',
                          cursor: 'pointer',
                          fontSize: '0.875rem',
                          fontWeight: '500',
                          transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(6,182,212,0.3)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(6,182,212,0.2)'}
                      >
                        + Monitor
                      </button>
                    </div>
                  </div>

                  <div style={{ padding: '1.5rem' }}>
                    {/* Risk Indicator */}
                    {(() => {
                      const risk = getRiskLevel(prediction.delay_probability);
                      const percentage = Math.round(prediction.delay_probability * 100);

                      return (
                        <div style={{ ...styles.riskIndicator, ...risk.style }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <AlertTriangle size={24} color={risk.color === 'red' ? '#f87171' : risk.color === 'yellow' ? '#facc15' : '#4ade80'} />
                              <div>
                                <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: risk.color === 'red' ? '#f87171' : risk.color === 'yellow' ? '#facc15' : '#4ade80' }}>
                                  {risk.level}
                                </h3>
                                <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Confidence: {prediction.confidence}</p>
                              </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontSize: '2.25rem', fontWeight: 'bold', color: risk.color === 'red' ? '#f87171' : risk.color === 'yellow' ? '#facc15' : '#4ade80' }}>
                                {percentage}%
                              </div>
                              <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Delay Probability</div>
                            </div>
                          </div>

                          <div style={styles.progressBar}>
                            <div
                              style={{
                                ...styles.progressFill,
                                width: `${percentage}%`,
                                backgroundColor: risk.color === 'red' ? 'rgba(239,68,68,0.4)' : risk.color === 'yellow' ? 'rgba(234,179,8,0.4)' : 'rgba(34,197,94,0.4)'
                              }}
                            />
                          </div>
                        </div>
                      );
                    })()}

                    {/* Stats Grid */}
                    <div style={styles.statsGrid}>
                      <div style={styles.statCard}>
                        <Thermometer size={20} color="#fb923c" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Temperature</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: '600' }}>{prediction.weather.temperature}°C</div>
                      </div>
                      <div style={styles.statCard}>
                        <Droplets size={20} color="#60a5fa" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Humidity</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: '600' }}>{prediction.weather.humidity}%</div>
                      </div>
                      <div style={styles.statCard}>
                        <Info size={20} color="#9ca3af" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Pressure</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: '600' }}>{prediction.weather.pressure} hPa</div>
                      </div>
                      <div style={styles.statCard}>
                        <TrendingUp size={20} color="#22d3ee" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Distance</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: '600' }}>{prediction.distance} mi</div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
                      <button
                        onClick={() => getRecommendations(prediction.flight_number)}
                        disabled={loading}
                        style={{
                          flex: 1,
                          padding: '0.75rem 1.5rem',
                          background: 'linear-gradient(90deg, #a855f7 0%, #ec4899 100%)',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '0.75rem',
                          fontSize: '0.95rem',
                          fontWeight: '600',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '0.5rem',
                          opacity: loading ? 0.5 : 1,
                          transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => {
                          if (!loading) {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 10px 20px rgba(168, 85, 247, 0.3)';
                          }
                        }}
                        onMouseOut={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <Shield size={20} />
                        {loading ? 'Loading...' : 'Get Recommendations'}
                      </button>
                      <button
                        onClick={() => {
                          setPrediction(null);
                          setShowRecommendations(false);
                          setRecommendations([]);
                        }}
                        style={{
                          padding: '0.75rem 1.5rem',
                          backgroundColor: 'rgba(255,255,255,0.1)',
                          color: '#ffffff',
                          border: '1px solid rgba(255,255,255,0.2)',
                          borderRadius: '0.75rem',
                          cursor: 'pointer',
                          fontSize: '0.95rem'
                        }}
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                </div>

                {/* Recommendations Section */}
                {showRecommendations && recommendations.length > 0 && (
                  <div style={styles.card}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                      <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>
                        💡 Personalized Recommendations
                      </h3>
                      <button
                        onClick={() => setShowRecommendations(false)}
                        style={{
                          padding: '0.5rem',
                          background: 'transparent',
                          border: 'none',
                          color: '#9ca3af',
                          cursor: 'pointer',
                          borderRadius: '0.5rem',
                          transition: 'background 0.2s'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                        onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                      >
                        <X size={20} />
                      </button>
                    </div>

                    {recommendations.map((rec, idx) => (
                      <div key={idx} style={styles.recommendationCard}>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                          <div style={{ flexShrink: 0, marginTop: '0.25rem' }}>
                            {getRecommendationIcon(rec.type)}
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                              <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>{rec.title}</h4>
                              <span style={{
                                padding: '0.125rem 0.5rem',
                                backgroundColor: 'rgba(255,255,255,0.1)',
                                borderRadius: '9999px',
                                fontSize: '0.75rem',
                                color: '#9ca3af'
                              }}>
                                {rec.category}
                              </span>
                            </div>
                            <p style={{ margin: '0 0 0.75rem 0', color: '#d1d5db', fontSize: '0.875rem' }}>
                              {rec.message}
                            </p>
                            {rec.actionable && rec.action && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: '#22d3ee' }}>
                                <ChevronRight size={16} />
                                <span>{rec.action}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </>
        )}

        {activeTab === 'monitor' && (
          <div style={styles.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', margin: 0, marginBottom: '0.5rem' }}>
                  Monitored Flights
                </h2>
                <p style={{ color: '#9ca3af', margin: 0 }}>
                  Track multiple flights - saved in your browser
                </p>
              </div>
              {monitoredFlights.length > 0 && (
                <div style={{ color: '#22d3ee', fontSize: '0.875rem', fontWeight: '500' }}>
                  {monitoredFlights.length} flight{monitoredFlights.length !== 1 ? 's' : ''} monitored
                </div>
              )}
            </div>

            {monitoredFlights.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                <Plane size={64} color="#6b7280" style={{ margin: '0 auto 1rem' }} />
                <p style={{ color: '#9ca3af', marginBottom: '0.5rem' }}>No flights being monitored</p>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Check a flight and click "+ Monitor" to track it here
                </p>
              </div>
            ) : (
              monitoredFlights.map((flight) => (
                <div
                  key={flight.id}
                  style={styles.flightCard}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <Plane size={20} color="#22d3ee" />
                        <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{flight.flight_number}</span>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: 'rgba(6,182,212,0.2)',
                          color: '#22d3ee',
                          borderRadius: '9999px',
                          fontSize: '0.75rem'
                        }}>
                          {flight.airline}
                        </span>
                      </div>
                      <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                        {flight.route} • {flight.departure_time}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div
                            style={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: getRiskColor(flight.delay_probability)
                            }}
                          />
                          <span style={{ color: getRiskColor(flight.delay_probability), fontWeight: '600' }}>
                            {Math.round(flight.delay_probability * 100)}% delay risk
                          </span>
                        </div>
                        <span style={{ color: '#6b7280' }}>
                          Added {formatDate(flight.addedAt)}
                        </span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => refreshMonitoredFlight(flight.flight_number)}
                        style={{
                          padding: '0.5rem',
                          backgroundColor: 'rgba(6,182,212,0.2)',
                          color: '#22d3ee',
                          border: 'none',
                          borderRadius: '0.5rem',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        title="Refresh"
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(6,182,212,0.3)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(6,182,212,0.2)'}
                      >
                        <RefreshCw size={18} />
                      </button>
                      <button
                        onClick={() => removeFromMonitor(flight.id)}
                        style={{
                          padding: '0.5rem',
                          backgroundColor: 'rgba(239,68,68,0.2)',
                          color: '#ef4444',
                          border: 'none',
                          borderRadius: '0.5rem',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        title="Remove"
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(239,68,68,0.3)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(239,68,68,0.2)'}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div style={styles.card}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', margin: 0, marginBottom: '0.5rem' }}>
                  Prediction History
                </h2>
                <p style={{ color: '#9ca3af', margin: 0 }}>
                  Recent flight predictions - saved in your browser
                </p>
              </div>
              {history.length > 0 && (
                <button
                  onClick={clearHistory}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(239,68,68,0.2)',
                    color: '#ef4444',
                    border: '1px solid rgba(239,68,68,0.3)',
                    borderRadius: '0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(239,68,68,0.3)'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(239,68,68,0.2)'}
                >
                  Clear All
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                <Clock size={64} color="#6b7280" style={{ margin: '0 auto 1rem' }} />
                <p style={{ color: '#9ca3af', marginBottom: '0.5rem' }}>No prediction history</p>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Check some flights to see them here
                </p>
              </div>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  style={styles.historyCard}
                  onClick={() => loadFromHistory(item)}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <Plane size={18} color="#22d3ee" />
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontSize: '1rem', fontWeight: '600' }}>{item.flight_number}</span>
                          <span style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                            {item.route}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                          {formatDate(item.timestamp)}
                        </div>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        fontSize: '1.125rem',
                        fontWeight: '600',
                        color: getRiskColor(item.delay_probability)
                      }}>
                        {Math.round(item.delay_probability * 100)}%
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        {item.confidence}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }

        input:focus {
          border-color: #06b6d4;
          box-shadow: 0 0 0 3px rgba(6,182,212,0.2);
        }
      `}</style>
    </div>
  );
};

export default FlightDelayApp;