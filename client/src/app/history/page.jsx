"use client";
import { List, Splitter, Avatar, Layout } from "antd";
import React, { useState, useEffect } from "react";
import styles from "./styles.module.css";
import InfiniteScroll from "react-infinite-scroll-component";
import { BASE_URL } from "../lib/api";

const { Header, Content, Footer } = Layout;

// Fake data to mock events
const fakeEvents = Array.from({ length: 50 }, (_, index) => ({
  id: index + 1,
  eventType: `Event Type ${index + 1}`,
  time: `2024-10-08 12:0${index % 10}`,
  description: `Description for event ${index + 1}`,
  videoUrl: `https://www.example.com/videos/video${index + 1}.webm`
}));

const HistoryPage = () => {
  const [events, setEvents] = useState([]);
  const [video, setVideo] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/events`).then(data => {
      console.log(data)
    })
    console.log("Loading initial data..."); // Debug log
    loadMoreData();
  }, []);
  
  // Simulate loading more data
  const loadMoreData = async () => {
    if (loading) {
      return;
    }
    setLoading(true);
    try {
      const newEvents = fakeEvents.slice(events.length, events.length + 10); // Simulate loading next 10 events
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
    setVideo(item.videoUrl);
  };

  return (
    <Layout style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header style={{ background: '#fff', padding: 0, height: '64px' }}>
        <h1 style={{ margin: 0, padding: '0 16px' }}>Event History</h1>
      </Header>
      <Content style={{ padding: '50px' }}>
        <div style={{
          padding: 24,
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
        }}>
          <Splitter 
            style={{
              maxHeight: '70%',
              boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
              overflow: 'hidden'
            }}
          >
            <Splitter.Panel defaultSize='40%' minSize='20%' maxSize='70%'>
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f2eed7' }}>
                {video ? (
                  <div>
                    <h1>ID: {selectedEvent.id}</h1>
                    <video autoPlay={true} controls={true} style={{ maxWidth: '100%', maxHeight: 'calc(100% - 40px)' }}>
                      <source src={video} type="video/webm" />
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
                  loader={<h4>Loading...</h4>}
                  scrollableTarget="scrollableDiv"
                >
                  <List
                    dataSource={events}
                    renderItem={(item) => (
                      <List.Item
                        key={item.id}
                        onClick={() => showEventDetails(item)}
                        className={selectedEvent && selectedEvent.id === item.id ? styles.selectedItem : ""}
                      >
                        <List.Item.Meta
                          avatar={<Avatar src={`https://api.dicebear.com/7.x/miniavs/svg?seed=${item.id}`} />}
                          title={item.eventType}
                          description={<p>{item.time}</p>}
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
      <Footer style={{ textAlign: 'center', height: '64px' }}>
        {/* Add your footer content here */}
        Event History ©{new Date().getFullYear()} Created by BinaCloud
      </Footer>
    </Layout>
  );
};

export default HistoryPage;
