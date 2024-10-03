"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import Box from "./box";

const blobFromBase64String = base64String => {
  const byteArray = Uint8Array.from(
    atob(base64String)
      .split('')
      .map(char => char.charCodeAt(0))
  );
 return new Blob([byteArray], { type: 'image/png' });
};

export default function Receiver() {
  const [latency, setLatency] = useState();
  const [boxes, setBoxes] = useState([]);

  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/receiver`, {
    filter: () => false, // don't re-render on new websocket msg
    onMessage: (message) => {
      const data = JSON.parse(message.data);
      console.log("Received");

      setBoxes(data.objects);
      const latency = Date.now() - new Date(data.timestamp);
      setLatency(latency.toString())

      return;

      const blob = blobFromBase64String(data.image);
      const newUrl = URL.createObjectURL(blob);

      const img = document.getElementById("result");
      if (!img) {
        return;
      }


      const originalUrl = img.src;
      img.src = newUrl;

      // Clean up the original URL as it is no longer needed
      URL.revokeObjectURL(originalUrl);
    },
  });

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  const draw = boxes.map(box => {
    console.log("A box is ")
    console.log({
      x1: box.box[0],
      y1: box.box[1]
    })
    return <Box x1={box.box[0]} y1={box.box[1]} x2={box.box[2]} y2={box.box[3]}/>
  })

  return (
    <>
      <p>Latency: {latency} ms</p>
      <div id="container" style={{position: "relative"}}>
        <img id="result" width={1280}/>
        {draw}
      </div>
    </>
  );
}
