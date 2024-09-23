"use client";

import Sender from "../ui/sender/sender";
import { useRef, useEffect, useCallback, useState } from "react";

export default function Page() {
    const [fps, setFps] = useState(1);

  return (
    <main>
      <label>FPS</label>
      <input
        type="number"
        value={fps}
        onChange={(e) => setFps(e.target.value)}
      />
      <Sender fps={fps} />
    </main>
  );
}