import React, { useState } from 'react';
import { Menu, theme, Input } from 'antd';
import mrtData from '../data/mrtData.json';


const { useToken } = theme;

const MrtMenu = ({ isDarkMode, setSelectedStation, selectedStation }) => {
  const [searchText, setSearchText] = useState('');

  const { Search } = Input;
  const { token } = useToken();

  const lineColors = {
    "NSL": "#FF0000", // Red
    "EWL": "#00FF00", // Green
    "CCL": "#FFA500", // Orange
    "DTL": "#0000FF", // Blue
    "NEL": "#800080", // Purple
    "TEL": "#A52A2A", // Brown
  };

  // Function to filter stations based on search text
  const filterStations = () => {
    const allStations = Object.values(mrtData).flat();
    
    // Ensure allStations exists and is an array before filtering
    return Array.isArray(allStations)
      ? allStations.filter((station) =>
          station.toLowerCase().includes(searchText.toLowerCase())
        )
      : [];
  };

  const onSearch = (value, _e, info) => console.log(info?.source, value);

  // Get the line color based on selected station
  const getLineColor = () => {
    const line = Object.keys(mrtData).find((line) =>
      mrtData[line].some((station) => station === selectedStation)
    );
    return line ? lineColors[line] : token.colorBgContainer; // Fallback to default
  };

  return (
    <>
      {/* Search Input */}
      <Input
        placeholder="Search stations..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ margin: '16px', width: 'calc(100% - 32px)' }}
      />

      {/* If there is search input */}
      {searchText ? (
        <Search
          placeholder="input search text"
          allowClear
          onSearch={onSearch}
          style={{
            width: 200,
          }}
        />
      ) : (
        /* Regular Menu when there is no search input */
        <Menu
          mode="inline"
          theme={isDarkMode ? 'dark' : 'light'}
          style={{ maxHeight: 'calc(100vh - 64px)', overflowY: 'auto' }}
        >
          {Object.keys(mrtData).map((line) => (
            <Menu.SubMenu key={line} title={line}>
              {mrtData[line].map((station) => (
                <Menu.Item
                  key={station}
                  onClick={() => setSelectedStation(station)}
                  style={{
                    backgroundColor:
                      station === selectedStation ? getLineColor() : 'transparent',
                    color: station === selectedStation ? '#fff' : 'inherit',
                  }}
                >
                  {station}
                </Menu.Item>
              ))}
            </Menu.SubMenu>
          ))}
        </Menu>
      )}
    </>
  );
};

export default MrtMenu;
