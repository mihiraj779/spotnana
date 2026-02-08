import React from "react";
import { Layout, Breadcrumb, Avatar, Typography, Space } from "antd";
import PropTypes from "prop-types";
import styles from "./Header.module.scss";

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header = ({ breadcrumbItems = [] }) => {
  const defaultBreadcrumb = [
    { title: "Home", key: "home" },
    { title: "Flight Search", key: "search" },
  ];
  const items = breadcrumbItems.length ? breadcrumbItems : defaultBreadcrumb;

  return (
    <AntHeader className={styles.header}>
      <div className={styles.left}>
        <img src="/assets/image.png" alt="Spotnana" className={styles.logo} />
        <Text strong className={styles.companyName}>
          Spotnana
        </Text>
      </div>
      <div className={styles.center}>
        <Breadcrumb items={items} className={styles.breadcrumb} />
      </div>
      <div className={styles.right}>
        <Space align="center" size="middle">
          <Avatar size="small" className={styles.avatar}>
            U
          </Avatar>
          <Text className={styles.profileName}>User</Text>
        </Space>
      </div>
    </AntHeader>
  );
};

Header.propTypes = {
  breadcrumbItems: PropTypes.arrayOf(
    PropTypes.shape({ title: PropTypes.node, key: PropTypes.string }),
  ),
};

export default Header;
