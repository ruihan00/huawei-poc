"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import Box from "./box";
import { notification } from "antd";
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
  const openNotification = (event) => {
    api.info({
      message: "Alert",
      description: `Event type: ${event.type}`,
      onClick: () => {
        console.log("Notification clicked");
        sessionStorage.setItem('selectedEvent', JSON.stringify(event));
        window.open('/history', '_blank');
      },
      duration: 0, // to prevent auto-close
    });
  };
  const handleEventsMessage = (data) => {
    // edit receiver to handle event events
    for (const event of data.events) {
      console.log(event.type, event);
      openNotification(event);
    }
    setBoxes(data.objects)
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
        messageHandlers[data.type](data);
        sendMessage("ack");
      },
    }
  );

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  const drawnBoxes = boxes.map(box => {
    return <Box x1={box.box[0]} y1={box.box[1]} x2={box.box[2]} y2={box.box[3]}/>
  })



  return (
    <>
      {contextHolder}
      <div id="container" style={{ position: "relative" }}>
        {Object.keys(image).map((senderId) => (
          <div key={senderId}>
            <img id="result" src={image[senderId]} key={senderId} />
            {drawnBoxes}
            <p>{senderId}</p>
          </div>
        ))}
      </div>
    </>
  );
}
