"use client";
import { List } from "antd";
import React, { useState, useEffect } from "react";
import styles from "./styles.module.css";
import InfiniteScroll from "react-infinite-scroll-component";

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
        if (!selectedEvent) {
          setSelectedEvent(newEvents[0]); // Select the first event initially
          setVideo(newEvents[0].videoUrl);
        }
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
    <div className={styles.page}>
      <div className={styles.videoPane}>
        <div className={styles.videoContainer}>
          {video ? (
            <video autoPlay={true} controls={true}>
              <source src={video} type="video/webm" />
            </video>
          ) : (
            <p>123</p>
          )}
        </div>
      </div>
      <div
        id="scrollableDiv"
        style={{
          height: 400,
          overflow: "auto",
          padding: "0 16px",
          border: "1px solid rgba(140, 140, 140, 0.35)",
        }}
      >
        <InfiniteScroll
          dataLength={events.length}
          next={loadMoreData}
          hasMore={hasMore}
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
                  title={item.eventType}
                  description={
                    <>
                      <p>{item.time}</p>
                      <p>{item.description}</p>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        </InfiniteScroll>
      </div>
    </div>
  );
};

export default HistoryPage;
