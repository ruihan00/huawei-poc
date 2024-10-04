"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import Box from "./box";

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
  const [image, setImage] = useState();
  const handleImageEvent = (data) => {
    setImage(data.image);
  };
  const handleEventEvent = (data) => {
    // edit receiver to handle event events
    for (const event of data.events) {
      console.log(event.type, event);
    }
  };
  const eventHandlers = {
    image: handleImageEvent,
    event: handleEventEvent,
  };
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    `${BASE_URL}/receiver`,
    {
      filter: () => false, // don't re-render on new websocket msg
      onMessage: (message) => {
        const data = JSON.parse(message.data);
        eventHandlers[data.type](data.data);
        sendMessage("ack");
      },
    }
  );

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  return (
    <>
      <p>Latency: {latency} ms</p>
      <div id="container" style={{ position: "relative" }}>
        <img id="result" src={image} />
      </div>
    </>
  );
}
