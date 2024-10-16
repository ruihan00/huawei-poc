"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import Box from "./box";
import { notification } from "antd";
import { FaPersonFalling } from "react-icons/fa6";
import { IoTimeOutline } from "react-icons/io5";
import { FaWheelchair } from "react-icons/fa";
import styles from "./receiver.css";

const blobFromBase64String = (base64String) => {
  const byteArray = Uint8Array.from(
    atob(base64String)
      .split("")
      .map((char) => char.charCodeAt(0))
  );
  return new Blob([byteArray], { type: "image/png" });
};

export default function Receiver() {
  const [latency, setLatency] = useState();
  const [boxes, setBoxes] = useState([]);
  const [image, setImage] = useState({});

  const handleImageMessage = (data) => {
    console.log(data);
    const senderId = data.id;
    setImage((prev) => ({
      ...prev,
      [senderId]: data.image,
    }));
  };
  const [api, contextHolder] = notification.useNotification();

  notification.config({
    placement: "topRight",
    maxCount: 5,
  });

  const openNotification = (event) => {
    let icon;
    let name = event.type;
    switch (event.type) {
      case "Fall":
        icon = (
          <FaPersonFalling
            size={60}
            style={{
              color: "#4682B4",
              paddingRight: "10px",
            }}
          />
        );
        break;
      case "Prolonged Time":
        icon = (
          <IoTimeOutline
            size={60}
            style={{
              color: "#228B22",
              paddingRight: "10px",
            }}
          />
        );
        break;
      case "Mobility Aid":
        icon = (
          <FaWheelchair
            size={60}
            style={{
              color: "#DC143C",
              paddingRight: "10px",
            }}
          />
        );
        name = "Mobility Aid (Wheelchair)";
        break;
    }

    notification.info({
      message: <strong style={{ paddingLeft: '30px' }}>Alert</strong>,
      description: <div style={{ paddingLeft: '30px' }}>Event type: {name}</div>,
      icon,
      onClick: () => {
        console.log("Notification clicked");
        sessionStorage.setItem("selectedEvent", JSON.stringify(event));
        window.open("/history", "_blank");
      },
      duration: 30, // to prevent auto-close
    });
  };
  const handleEventsMessage = (data) => {
    // edit receiver to handle event events
    for (const event of data.events) {
      console.log(event.type, event);
      openNotification(event);
    }
    setBoxes(data.objects);
  };
  const messageHandlers = {
    image: handleImageMessage,
    events: handleEventsMessage,
  };
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    `${BASE_URL}/receiver`,
    {
      filter: () => false, // don't re-render on new websocket msg
      onMessage: (message) => {
        const data = JSON.parse(message.data);
        const handler = messageHandlers[data.type];
        if (!handler) {
          return;
        }
        handler(data);
        sendMessage("ack");
      },
    }
  );

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  const drawnBoxes = boxes.map((box) => {
    return (
      <Box x1={box.box[0]} y1={box.box[1]} x2={box.box[2]} y2={box.box[3]} />
    );
  });

  return (
    <>
      {contextHolder}
      <div id="container" style={{ position: "relative" }}>
        {Object.keys(image).map((senderId) => (
          <div key={senderId}>
            <img
              id="result"
              style={{ width: "640px", height: "480px" }}
              src={image[senderId]}
              key={senderId}
            />
            {drawnBoxes}
          </div>
        ))}
      </div>
    </>
  );
}
