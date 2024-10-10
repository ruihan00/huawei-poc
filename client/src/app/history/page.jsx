"use client";
import { Input, Select, List, Splitter, Avatar, Layout } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import React, { useState, useEffect, useMemo, Suspense } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { BASE_URL } from "../lib/api";
import { FaPersonFalling } from "react-icons/fa6";
import { IoTimeOutline } from "react-icons/io5";
import { FaWheelchair } from "react-icons/fa";
import PHeader from "../ui/layout/pheader";
import PFooter from "../ui/layout/pfooter";
import { useSearchParams } from "next/navigation";

const { Content } = Layout;
const { Option } = Select;

const HistoryPage = () => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const searchParams = useSearchParams();

  useEffect(() => {
    console.log("Loading initial data...");
    const loadData = async () => {
      await loadMoreData();  // Load the events first
    };
  
    loadData();
  }, []);
  
  useEffect(() => {
    if (events.length > 0) {
      const eventId = searchParams.get("selectedEvent");
      if (eventId) {
        const event = events.find((ev) => ev.id === eventId); // Find the event by ID from the loaded events
        if (event) {
          setSelectedEvent(event); // Set the selected event
        }
      }
    }
  }, [searchParams, events]); // Run this effect when searchParams or events change

  const fetchEvents = async () => {
    const response = await fetch(`${BASE_URL}/events`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
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
        setEvents((prevEvents) => [...prevEvents, ...newEvents]);
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
      case "Fall":
        return (
          <Avatar
            icon={
              <FaPersonFalling
                size={35}
                style={{
                  backgroundColor: "#4682B4",
                  color: "#FFF",
                  padding: "5px",
                }}
              />
            }
          />
        );
      case "Prolonged Time":
        return (
          <Avatar
            src={
              <IoTimeOutline
                size={35}
                style={{
                  backgroundColor: "#228B22",
                  color: "#FFF",
                  padding: "5px",
                }}
              />
            }
          />
        );
      case "Mobility Aid":
        return (
          <Avatar
            src={
              <FaWheelchair
                size={35}
                style={{
                  backgroundColor: "#DC143C",
                  color: "#FFF",
                  padding: "5px",
                }}
              />
            }
          />
        );
      default:
        return <Avatar />;
    }
  };

  const EVENT_TYPES = ["all", "fall", "prolonged time", "mobility aid"];

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const matchesSearch =
        event.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.type.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter =
        filterType === "all" ||
        event.type.toLowerCase() === filterType.toLowerCase();
      return matchesSearch && matchesFilter;
    });
  }, [events, searchTerm, filterType]);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Layout
        style={{ height: "100vh", display: "flex", flexDirection: "column" }}
      >
        <PHeader title="Event History" />
        <Content style={{ padding: "50px", backgroundColor: "#FFF" }}>
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              height: "calc(100vh - 152px)",
            }}
          >
            <Splitter
              style={{
                height: "90%",
                boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
                overflow: "hidden",
              }}
            >
              <Splitter.Panel defaultSize="60%" minSize="20%" maxSize="70%">
                <div
                  style={{
                    height: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: "#f2eed7",
                    overflow: "auto",
                    padding: "16px",
                  }}
                >
                  {selectedEvent ? (
                    <div>
                      <video
                        key={`${selectedEvent.id}-${new Date().getTime()}`}
                        autoPlay={true}
                        controls={true}
                        style={{
                          width: "640px",
                          height: "480px",
                        }}
                      >
                        <source src={selectedEvent.url} type="video/webm" />
                        Your browser does not support the video tag.
                      </video>
                    </div>
                  ) : (
                    <p>Select an event to view it!</p>
                  )}
                </div>
              </Splitter.Panel>
              <Splitter.Panel style={{ height: "100%", overflow: "hidden" }}>
                <div
                  id="scrollableDiv"
                  style={{
                    height: "100%",
                    overflow: "auto",
                    padding: "16px",
                    border: "1px solid rgba(140, 140, 140, 0.35)",
                  }}
                >
                  <div style={{ padding: "16px", display: "flex", gap: "10px" }}>
                    <Input
                      placeholder="Search events"
                      prefix={<SearchOutlined />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <Select
                      style={{ width: 150 }}
                      value={filterType}
                      onChange={setFilterType}
                    >
                      {EVENT_TYPES.map((type) => (
                        <Option key={type} value={type}>
                          {type === "all"
                            ? "All Types"
                            : type.charAt(0).toUpperCase() + type.slice(1)}
                        </Option>
                      ))}
                    </Select>
                  </div>
                  <InfiniteScroll
                    dataLength={filteredEvents.length}
                    next={loadMoreData}
                    hasMore={hasMore}
                    scrollableTarget="scrollableDiv"
                    inverse={true}
                    style={{ display: "flex", flexDirection: "column-reverse" }}
                  >
                    <List
                      dataSource={[...filteredEvents]}
                      renderItem={(item) => (
                        <List.Item
                          key={item.id}
                          onClick={() => showEventDetails(item)}
                          style={{
                            backgroundColor:
                              selectedEvent && selectedEvent.id === item.id
                                ? "#e6f7ff"
                                : "transparent",
                            transition: "background-color 0.3s",
                            cursor: "pointer",
                            padding: "16px"
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
        <PFooter title="Event History" />
      </Layout>
    </Suspense>
  );
};

export default HistoryPage;
