import React, { useState, useMemo } from 'react';
import { Menu, theme, Input } from 'antd';
import mrtData from '../data/mrtData.json';

const { useToken } = theme;

const MrtMenu = ({ isDarkMode, setSelectedStation, selectedStation }) => {
  const [searchText, setSearchText] = useState('');

  const { token } = useToken();

  const lineColors = {
    "NSL": "#FF0000", // Red
    "EWL": "#004D00", // Green
    "CCL": "#FFA500", // Orange
    "DTL": "#000099", // Blue
    "NEL": "#800080", // Purple
    "TEL": "#A5682A", // Brown
  };

  const filteredStations = useMemo(() => {
    const allStations = Object.entries(mrtData).flatMap(([line, stations]) => 
      stations.map(station => ({ line, station }))
    );
    
    return allStations.filter(({ station }) =>
      station.toLowerCase().includes(searchText.toLowerCase())
    );
  }, [searchText]);

  const getLineColor = (line) => lineColors[line] || token.colorBgContainer;

  return (
    <>
      {/* Search Input */}
      <Input
        placeholder="Search stations..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ margin: '16px', width: 'calc(100% - 32px)' }}
      />

      <Menu
        mode="inline"
        theme={isDarkMode ? 'dark' : 'light'}
        style={{ maxHeight: 'calc(100vh - 64px)', overflowY: 'auto' }}
        selectedKeys={[selectedStation]}
      >
        {searchText ? (
          // Render filtered results
          filteredStations.map(({ line, station }) => (
            <Menu.Item
              key={station}
              onClick={() => setSelectedStation(station, getLineColor(line))}
              style={{
                backgroundColor:
                  station === selectedStation ? getLineColor(line) : 'transparent',
                color: station === selectedStation ? '#fff' : 'inherit',
              }}
            >
              {`${station} (${line})`}
            </Menu.Item>
          ))
        ) : (
          // Render full menu when there's no search input
          Object.entries(mrtData).map(([line, stations]) => (
            <Menu.SubMenu key={line} title={line}>
              {stations.map((station) => (
                <Menu.Item
                  key={station}
                  onClick={() => setSelectedStation(station, getLineColor(line))}
                  style={{
                    backgroundColor: station === selectedStation ? getLineColor(line) : 'transparent',
                    color: station === selectedStation ? '#fff' : 'inherit',
                  }}
                >
                  {station}
                </Menu.Item>
              ))}
            </Menu.SubMenu>
          ))
        )}
      </Menu>
    </>
  );
};

export default MrtMenu;