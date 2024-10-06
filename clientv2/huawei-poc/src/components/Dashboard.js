import React, { useState, useEffect } from 'react';
import { Table, Spin, Modal, theme } from 'antd';

const { useToken } = theme;

// Mock function to simulate API call
const fetchEvents = (location) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const events = [];
        for (let i = 1; i <= 100; i++) {
          events.push({
            key: i,
            eventType: `Event Type ${i}`,
            url: `https://example.com/event${i}`,
            time: `14:${(i % 60).toString().padStart(2, '0')}:00`,
            details: `Details for Event Type ${i}`,
          });
        }
        resolve(events);
      }, 300);
    });
  };

const Dashboard = ({ location, lineColor }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    const getEvents = async () => {
      setLoading(true);
      try {
        const data = await fetchEvents(location);
        setEvents(data);
      } catch (error) {
        console.error('Error fetching events:', error);
      } finally {
        setLoading(false);
      }
    };

    getEvents();
  }, [location]);

  const showEventDetails = (event) => {
    setSelectedEvent(event);
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'S/N',
      dataIndex: 'key',
      key: 'sn',
      width: '10%',
      render: (text, record, index) => index + 1,
    },
    {
      title: 'Event Type',
      dataIndex: 'eventType',
      key: 'eventType',
      render: (text, record) => (
        <a onClick={() => showEventDetails(record)}>{text}</a>
      ),
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      render: (text) => (
        <a href={text} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      ),
    },
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
    },
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <h2 style={{ color: '#fff' }}> 
        <span 
          style={{ 
            backgroundColor: lineColor, 
            color: '#fff',
            padding: '8px 15px',
            borderRadius: '20px',
            display: 'inline-block',
            fontSize: '1.2em',
            fontWeight: 'bold'
          }}
        >
          Dashboard for {location}
        </span>
      </h2>
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <Spin size="large" />
        </div>
      ) : (
        <Table 
          columns={columns} 
          dataSource={events}
          pagination={{ 
            showSizeChanger: true, 
            pageSizeOptions: ['10', '20', '50', '100'],
            defaultPageSize: 10
          }}
          scroll={{ y: 'calc(100vh - 350px)' }}
        />
      )}
      <Modal
        visible={modalVisible}
        onOk={() => setModalVisible(false)}
        onCancel={() => setModalVisible(false)}
      >
        {selectedEvent && (
          <div>
            <h1><strong>{selectedEvent.eventType}</strong></h1>
            <p><strong>URL:</strong> <a href={selectedEvent.url} target="_blank" rel="noopener noreferrer">{selectedEvent.url}</a></p>
            <p><strong>Details:</strong> {selectedEvent.details}</p>
            <p><strong>Time:</strong> {selectedEvent.time}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Dashboard;