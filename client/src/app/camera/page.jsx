"use client";

import Sender from "../ui/sender/sender";
import { useState } from "react";

const Page = () => {
  const [fps, setFps] = useState(1);

  return (
    <div>
      <label>FPS</label>
      <input
        type="number"
        value={fps}
        onChange={(e) => setFps(e.target.value)}
      />
      <Sender fps={fps} />
    </div>
  );
};

export default Page;
