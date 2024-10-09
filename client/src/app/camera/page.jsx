"use client";

import Sender from "../ui/sender/sender";
import { useState } from "react";
import { Layout } from "antd";
import PHeader from "../ui/layout/pheader"
import PFooter from "../ui/layout/pfooter"

const { Content } = Layout;

const Page = () => {
  const [fps, setFps] = useState(1);

  return (
    <Layout style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PHeader title="Camera"/>
      <Content style={{ backgroundColor: '#000', color: '#FFF', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
        <label>FPS</label>
        <input
          type="number"
          value={fps}
          onChange={(e) => setFps(e.target.value)}
        />
        <Sender fps={fps} />
      </Content>
      <PFooter title="Camera"/>
    </Layout>
  );
};

export default Page;
