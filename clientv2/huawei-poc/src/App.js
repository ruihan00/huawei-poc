import React, { useState } from 'react';
import { ConfigProvider, theme } from 'antd';
import AppLayout from './components/AppLayout';
import 'antd/dist/reset.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <AppLayout isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
    </ConfigProvider>
  );
}

export default App;