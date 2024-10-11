"use client";
import { Layout } from "antd";

const { Footer } = Layout;

const PFooter = ({ title }) => {
  return (
    <Footer style={{ background: 'linear-gradient(to top, #b3d9ff 80%, #dbdbdb 100%)', color: '#000', textAlign: 'center', height: '64px' }}>
        {title} ©{new Date().getFullYear()} Created by BinaCloud
    </Footer>
  );
};

export default PFooter;