"use client";
import { List } from "antd";
import React, { useState, useEffect } from "react";
import styles from "./styles.module.css";
import { BASE_URL } from "../lib/api";
const HistoryPage = () => {
  const [video, setVideo] = useState();

  useEffect(() => {
    const fetchVideo = async () => {
      const response = await fetch(BASE_URL + "/events");
      const data = await response.json();
      setVideo(data[0]);
    };

    fetchVideo();
  });
  return (
    <div className={styles.page}>
      <div className={styles.videoPane}>
        <div className={styles.videoContainer}>
          {video ? (
            <video autoPlay={true} controls={true}>
              <source src={video} type="video/webm" />
            </video>
          ) : (
            <p> Select a event to view it! </p>
          )}
        </div>
      </div>
      <div className={styles.listPane}></div>
    </div>
  );
};

export default HistoryPage;
