"use client";
import { List, Splitter, Avatar, Layout } from "antd";
import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { BASE_URL } from "../lib/api";
import PHeader from "../ui/layout/pheader"
import PFooter from "../ui/layout/pfooter"

const { Content } = Layout;

const HistoryPage = () => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    console.log("Loading initial data...");
    loadMoreData();
  }, []);
  
  const fetchEvents = async () => {
    const response = await fetch(`${BASE_URL}/events`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  };

  // Simulate loading more data
  const loadMoreData = async () => {
    if (loading) {
      return;
    }
    setLoading(true);
    try {
      const newEvents = await fetchEvents();
      if (newEvents.length === 0) {
        setHasMore(false);
      } else {
        setEvents(prevEvents => [...prevEvents, ...newEvents]);
      }
    } catch (error) {
      console.error("Error loading events:", error);
    } finally {
      setLoading(false);
    }
  };

  // Show event details and set video
  const showEventDetails = (item) => {
    setSelectedEvent(item);
  };

  const getAvatarByType = (type) => {
    switch (type) {
      case 'Fall':
        return <Avatar src={'/fall.png'}/>;
      case 'Prolonged Time':
        return <Avatar src={'/time.png'}/>;
      case 'Mobility Aid':
        return <Avatar src={'/mobaid.png'}/>;
      default:
        return <Avatar />
    }
  };

  return (
    <Layout style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <PHeader title="Event History"/>
      <Content style={{ padding: '50px', backgroundColor: '#FFF' }}>
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 152px)' 
        }}>
          <Splitter 
            style={{
              height: '90%',
              boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
              overflow: 'hidden'
            }}
          >
            <Splitter.Panel defaultSize='40%' minSize='20%' maxSize='70%'>
              <div style={{
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                backgroundColor: '#f2eed7', 
                overflow: 'auto',
                padding: '16px'
              }}>
                {selectedEvent ? (
                  <div>
                    <h1>ID: {selectedEvent.id}</h1>
                    <video key={selectedEvent.id} autoPlay={true} controls={true} style={{ maxWidth: '100%', maxHeight: 'calc(100% - 40px)' }}>
                      <source src={selectedEvent.url} type="video/webm" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                ) : (
                  <p>Select an event to view it!</p>
                )}
              </div>
            </Splitter.Panel>
            <Splitter.Panel style={{ height: '100%', overflow: 'hidden' }}>
              <div
                id="scrollableDiv"
                style={{
                  height: '100%',
                  overflow: "auto",
                  padding: "16px",
                  border: "1px solid rgba(140, 140, 140, 0.35)",
                }}
              >
                <InfiniteScroll
                  dataLength={events.length}
                  next={loadMoreData}
                  hasMore={hasMore}
                  scrollableTarget="scrollableDiv"
                  inverse={true}
                  style={{ display: 'flex', flexDirection: 'column-reverse' }} 
                >
                  <List
                    dataSource={[...events].reverse()}
                    renderItem={(item) => (
                      <List.Item
                        key={item.id}
                        onClick={() => showEventDetails(item)}
                        style={{
                          backgroundColor: selectedEvent && selectedEvent.id === item.id ? '#e6f7ff' : 'transparent',
                          transition: 'background-color 0.3s',
                          cursor: 'pointer',
                        }}
                      >
                        <List.Item.Meta
                          avatar={getAvatarByType(item.type)}
                          title={item.id}
                          description={
                            <div>
                              <p>{item.type}</p>
                              <p> {item.timestamp}</p>
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </InfiniteScroll>
              </div>
            </Splitter.Panel>
          </Splitter>
        </div>
      </Content>
      <PFooter title="Event History"/>
    </Layout>
  );
};

export default HistoryPage;
