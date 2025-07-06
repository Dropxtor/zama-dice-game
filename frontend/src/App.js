import React, { useState, useEffect } from 'react';
import { initSDK, createInstance, SepoliaConfig } from '@zama-fhe/relayer-sdk/bundle';
import { ethers } from 'ethers';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [isRolling, setIsRolling] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [gameHistory, setGameHistory] = useState([]);
  const [stats, setStats] = useState({});
  const [showNFTModal, setShowNFTModal] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [zamaInstance, setZamaInstance] = useState(null);
  const [isZamaReady, setIsZamaReady] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  const environmentId = 'ead32e7f-5090-4060-9b60-97f68caa3cf8';

  useEffect(() => {
    checkWalletConnection();
    fetchStats();
    fetchGameHistory();
    initializeZama();
  }, []);

  const initializeZama = async () => {
    try {
      console.log('🔄 Initializing Zama FHE SDK...');
      
      // Initialize the FHE SDK
      await initSDK();
      console.log('✅ FHE SDK loaded successfully');
      
      // Create Zama instance when MetaMask is available
      if (window.ethereum) {
        const config = { 
          ...SepoliaConfig, 
          network: window.ethereum,
          environmentId: environmentId
        };
        
        const instance = await createInstance(config);
        setZamaInstance(instance);
        setIsZamaReady(true);
        console.log('✅ Zama instance created successfully');
        console.log('🌐 Environment ID:', environmentId);
      } else {
        console.log('⚠️ MetaMask not available, Zama instance will be created after wallet connection');
      }
      
    } catch (error) {
      console.error('❌ Error initializing Zama:', error);
      setError('Failed to initialize Zama FHE. Some features may be limited.');
    }
  };

  const checkWalletConnection = async () => {
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          setIsConnected(true);
          setWalletAddress(accounts[0]);
        }
      } catch (error) {
        console.error('Error checking wallet connection:', error);
      }
    }
  };

  const connectWallet = async () => {
    setError('');
    setLoading(true);
    
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setIsConnected(true);
        setWalletAddress(accounts[0]);
        
        // Switch to Sepolia network
        try {
          await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0xaa36a7' }], // Sepolia chain ID
          });
        } catch (switchError) {
          if (switchError.code === 4902) {
            await window.ethereum.request({
              method: 'wallet_addEthereumChain',
              params: [{
                chainId: '0xaa36a7',
                chainName: 'Sepolia Test Network',
                nativeCurrency: {
                  name: 'ETH',
                  symbol: 'ETH',
                  decimals: 18
                },
                rpcUrls: ['https://sepolia.infura.io/v3/'],
                blockExplorerUrls: ['https://sepolia.etherscan.io/']
              }]
            });
          }
        }
        
        // Initialize Zama instance after wallet connection if not already done
        if (!zamaInstance) {
          try {
            await initSDK();
            const config = { 
              ...SepoliaConfig, 
              network: window.ethereum,
              environmentId: environmentId
            };
            const instance = await createInstance(config);
            setZamaInstance(instance);
            setIsZamaReady(true);
            console.log('✅ Zama instance created after wallet connection');
          } catch (zamaError) {
            console.error('❌ Error creating Zama instance:', zamaError);
          }
        }
        
      } catch (error) {
        console.error('Error connecting wallet:', error);
        setError('Failed to connect wallet. Please try again.');
      }
    } else {
      setError('MetaMask not installed! Please install MetaMask extension.');
    }
    
    setLoading(false);
  };

  const playGame = async () => {
    setIsRolling(true);
    setGameResult(null);
    setError('');

    try {
      // Determine game mode based on Zama availability
      const gameMode = isZamaReady && zamaInstance ? 'fhe' : 'standard';
      
      console.log(`🎲 Playing game in ${gameMode} mode`);
      
      let encryptedData = null;
      
      if (gameMode === 'fhe' && isConnected) {
        try {
          // Generate encrypted dice roll using Zama FHE
          console.log('🔐 Generating encrypted dice roll...');
          
          // Create two random dice values (1-6)
          const dice1 = Math.floor(Math.random() * 6) + 1;
          const dice2 = Math.floor(Math.random() * 6) + 1;
          
          console.log(`🎯 Local dice values: ${dice1}, ${dice2}`);
          
          // Encrypt the dice values using Zama FHE
          const encryptedDice1 = await zamaInstance.encrypt32(dice1);
          const encryptedDice2 = await zamaInstance.encrypt32(dice2);
          
          encryptedData = {
            dice1: Array.from(encryptedDice1),
            dice2: Array.from(encryptedDice2),
            mode: 'fhe'
          };
          
          console.log('✅ Dice values encrypted successfully');
          
        } catch (fheError) {
          console.error('❌ FHE encryption failed:', fheError);
          console.log('🔄 Falling back to standard mode');
          gameMode = 'standard';
        }
      }

      const response = await fetch(`${backendUrl}/api/play`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_address: isConnected ? walletAddress : null,
          num_dice: 2,
          game_mode: gameMode,
          encrypted_data: encryptedData,
          environment_id: environmentId
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to play game');
      }

      const result = await response.json();
      
      // Simulate dice rolling animation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setGameResult(result);
      if (result.nft_generated) {
        setShowNFTModal(true);
      }
      
      // Update stats and history without blocking
      fetchStats();
      fetchGameHistory();
    } catch (error) {
      console.error('Error playing game:', error);
      setError(error.message || 'Failed to play game. Please try again.');
    } finally {
      setIsRolling(false);
    }
  };

  const fetchStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetch(`${backendUrl}/api/stats`);
      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setError('Failed to load statistics');
    } finally {
      setIsLoadingStats(false);
    }
  };

  const fetchGameHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const response = await fetch(`${backendUrl}/api/games?limit=5`);
      if (!response.ok) {
        throw new Error('Failed to fetch game history');
      }
      const data = await response.json();
      setGameHistory(data.games || []);
    } catch (error) {
      console.error('Error fetching game history:', error);
      setError('Failed to load game history');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  const getDiceIcon = (value) => {
    const icons = {
      1: '⚀',
      2: '⚁',
      3: '⚂',
      4: '⚃',
      5: '⚄',
      6: '⚅'
    };
    return icons[value] || '⚀';
  };

  const getRarityColor = (rarity) => {
    const colors = {
      'Common': 'text-gray-400',
      'Uncommon': 'text-green-400',
      'Rare': 'text-blue-400',
      'Legendary': 'text-purple-400'
    };
    return colors[rarity] || 'text-gray-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-purple-500/20">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              🎲 Zama Dice
            </div>
            <div className="text-sm text-gray-300">
              by <a href="https://x.com/0xDropxtor" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300">@0xDropxtor</a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-300">
              Network: <span className="text-green-400">Sepolia</span>
            </div>
            {isConnected ? (
              <div className="bg-green-600/20 text-green-400 px-4 py-2 rounded-lg border border-green-500/30">
                {formatAddress(walletAddress)}
              </div>
            ) : (
              <button
                onClick={connectWallet}
                disabled={loading}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    <span>Connecting...</span>
                  </>
                ) : (
                  <span>Connect Wallet</span>
                )}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 text-center">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 blur-3xl"></div>
        <div className="relative z-10">
          <h1 className="text-6xl font-bold text-white mb-6">
            🎲 Zama Dice Game
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Roll the dice, win NFTs! Experience the future of gaming with privacy-preserving blockchain technology.
          </p>
          <div className="flex justify-center space-x-8 mb-12">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400">
                {isLoadingStats ? (
                  <div className="loading-spinner mx-auto"></div>
                ) : (
                  stats.total_games || 0
                )}
              </div>
              <div className="text-gray-400">Games Played</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-pink-400">
                {isLoadingStats ? (
                  <div className="loading-spinner mx-auto"></div>
                ) : (
                  stats.total_nfts || 0
                )}
              </div>
              <div className="text-gray-400">NFTs Generated</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400">
                {isLoadingStats ? (
                  <div className="loading-spinner mx-auto"></div>
                ) : (
                  stats.total_users || 0
                )}
              </div>
              <div className="text-gray-400">Players</div>
            </div>
          </div>
        </div>
      </section>

      {/* Game Section */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/20">
            <h2 className="text-3xl font-bold text-white text-center mb-8">
              🎮 Play Now
            </h2>
            
            {/* Dice Display */}
            <div className="text-center mb-8">
              <div className="flex justify-center space-x-8 mb-6">
                {isRolling ? (
                  <>
                    <div className="dice-rolling text-8xl">🎲</div>
                    <div className="dice-rolling text-8xl">🎲</div>
                  </>
                ) : gameResult ? (
                  gameResult.dice_results.map((value, index) => (
                    <div key={index} className="text-8xl dice-result">
                      {getDiceIcon(value)}
                    </div>
                  ))
                ) : (
                  <>
                    <div className="text-8xl text-gray-600">⚀</div>
                    <div className="text-8xl text-gray-600">⚀</div>
                  </>
                )}
              </div>
              
              {gameResult && (
                <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-lg p-6 mb-6">
                  <div className="text-4xl font-bold text-white mb-2">
                    Score: {gameResult.total_score}
                  </div>
                  <div className="text-gray-300">
                    Dice: {gameResult.dice_results.join(' + ')} = {gameResult.dice_results.reduce((a, b) => a + b, 0)}
                  </div>
                  {gameResult.nft_generated && (
                    <div className="mt-4 text-green-400 font-semibold">
                      🎉 NFT Generated!
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-center mb-6">
                <div className="error-message max-w-md mx-auto">
                  <div className="flex items-center space-x-2">
                    <span className="text-red-400">⚠️</span>
                    <span>{error}</span>
                    <button
                      onClick={() => setError('')}
                      className="text-red-400 hover:text-red-300 ml-auto"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Play Button */}
            <div className="text-center">
              <button
                onClick={playGame}
                disabled={isRolling}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xl font-bold px-12 py-4 rounded-full transition-all duration-300 transform hover:scale-105 disabled:hover:scale-100 flex items-center space-x-3 mx-auto"
              >
                {isRolling ? (
                  <>
                    <div className="loading-spinner"></div>
                    <span>Rolling...</span>
                  </>
                ) : (
                  <>
                    <span>🎲</span>
                    <span>Roll Dice</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Game History */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-white text-center mb-8">
            📈 Recent Games
          </h2>
          <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6 border border-purple-500/20">
            {isLoadingHistory ? (
              <div className="text-center py-8">
                <div className="loading-spinner mx-auto mb-4"></div>
                <div className="text-gray-400">Loading game history...</div>
              </div>
            ) : gameHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                No games played yet. Start playing to see your history!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left game-table">
                  <thead>
                    <tr className="border-b border-purple-500/20">
                      <th className="text-gray-300 font-semibold py-3">Player</th>
                      <th className="text-gray-300 font-semibold py-3">Dice</th>
                      <th className="text-gray-300 font-semibold py-3">Score</th>
                      <th className="text-gray-300 font-semibold py-3">NFT</th>
                      <th className="text-gray-300 font-semibold py-3">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gameHistory.map((game, index) => (
                      <tr key={index} className="border-b border-purple-500/10">
                        <td className="py-3 text-gray-300">
                          {game.player_address ? formatAddress(game.player_address) : 'Anonymous'}
                        </td>
                        <td className="py-3">
                          <div className="flex space-x-2">
                            {game.dice_results.map((value, i) => (
                              <span key={i} className="text-2xl">{getDiceIcon(value)}</span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 text-white font-semibold">{game.total_score}</td>
                        <td className="py-3">
                          {game.nft_generated ? (
                            <span className="text-green-400">✅ Generated</span>
                          ) : (
                            <span className="text-gray-500">❌ None</span>
                          )}
                        </td>
                        <td className="py-3 text-gray-400 text-sm">
                          {new Date(game.timestamp).toLocaleTimeString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* NFT Modal */}
      {showNFTModal && gameResult && gameResult.nft_metadata && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowNFTModal(false)}>
          <div className="bg-black/80 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/20 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white mb-4">🎉 NFT Generated!</h3>
              <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-lg p-6 mb-4">
                <div className="text-6xl mb-4">
                  {gameResult.dice_results.map((value, index) => (
                    <span key={index}>{getDiceIcon(value)}</span>
                  ))}
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">
                  {gameResult.nft_metadata.name}
                </h4>
                <p className="text-gray-300 mb-4">
                  {gameResult.nft_metadata.description}
                </p>
                <div className="flex justify-center space-x-4 text-sm">
                  <div className="text-center">
                    <div className="text-gray-400">Rarity</div>
                    <div className={`font-semibold ${getRarityColor(gameResult.nft_metadata.attributes.rarity)}`}>
                      {gameResult.nft_metadata.attributes.rarity}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-400">Score</div>
                    <div className="text-white font-semibold">{gameResult.nft_metadata.attributes.total_score}</div>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setShowNFTModal(false)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-purple-500/20 py-8">
        <div className="container mx-auto px-4 text-center">
          <div className="text-gray-300 mb-4">
            Built with ❤️ by <a href="https://x.com/0xDropxtor" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300">@0xDropxtor</a>
          </div>
          <div className="text-gray-400 text-sm">
            Powered by Zama • Privacy-First Gaming • Sepolia Network
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;