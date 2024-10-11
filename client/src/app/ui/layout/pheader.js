"use client";
import { Layout } from "antd";

const { Header } = Layout;

const PHeader = ({ title }) => {
  return (
    <Header style={{ background: 'linear-gradient(to bottom, #b3d9ff 80%, #dbdbdb 100%)', color: '#000', padding: 0, height: '64px' }}>
      <h1 style={{ margin: 0, padding: '0 16px' }}>{title}</h1>
    </Header>
  );
};

export default PHeader;