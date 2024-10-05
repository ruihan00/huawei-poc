import React, { useState } from 'react';
import { Layout, Switch, theme } from 'antd';
import { SunOutlined, SunFilled, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import Dashboard from './Dashboard';
import MrtMenu from './MrtMenu';
import logo from '../data/cloud.png';

const { Header, Sider, Content } = Layout;
const { useToken } = theme;

const AppLayout = ({ isDarkMode, toggleTheme }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedStation, setSelectedStation] = useState('');
  const [stationLineColor, setStationLineColor] = useState('');
  const { token } = useToken();

  const handleStationSelection = (station, lineColor) => {
    setSelectedStation(station);
    setStationLineColor(lineColor);
  };

  return (
    <Layout style={{ minHeight: '100%' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed} 
        collapsedWidth={0} 
        breakpoint="lg" 
        style={{ background: token.colorBgContainer, height: '100vh' }}
      >
        <MrtMenu
          isDarkMode={isDarkMode} 
          setSelectedStation={handleStationSelection}
          selectedStation={selectedStation}
        />
        
      </Sider>

      <Layout>
        <Header style={{ padding: 0, background: token.colorBgContainer, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
            className: 'trigger',
            onClick: () => setCollapsed(!collapsed),
            style: { fontSize: '18px', padding: '0 24px' },
          })}
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h1 style={{ color: token.colorText, margin: 0 }}>SGTransaid</h1>
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            
            <img 
              src={logo}
              alt="Company Logo" 
              style={{ height: '32px', marginRight: '16px' }} 
            />
            <Switch
              checked={isDarkMode}
              onChange={toggleTheme}
              checkedChildren={<SunFilled />}
              unCheckedChildren={<SunOutlined />}
              style={{ marginRight: '24px' }}
            />
          </div>
        </Header>

        <Content style={{ margin: '24px 16px', padding: 24, background: token.colorBgContainer, minHeight: 280 }}>
          {selectedStation ? (
            <Dashboard location={selectedStation} lineColor={stationLineColor} />
          ) : (
            <p>Please select an MRT line and station from the menu.</p>
          )}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
