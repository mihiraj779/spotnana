import React, { useState, useEffect } from "react";
import { Form, Select, DatePicker, Button, Row, Col } from "antd";
import dayjs from "dayjs";
import PropTypes from "prop-types";
import { getAirports } from "../../services/flightSearchService";
import styles from "./SearchForm.module.scss";

const { Item } = Form;

const SearchForm = ({ onSearch, loading }) => {
  const [form] = Form.useForm();
  const [airports, setAirports] = useState([]);
  const [airportsLoading, setAirportsLoading] = useState(true);

  useEffect(() => {
    getAirports()
      .then(setAirports)
      .catch(() => setAirports([]))
      .finally(() => setAirportsLoading(false));
  }, []);

  const handleSubmit = (values) => {
    const date = values.date ? dayjs(values.date).format("YYYY-MM-DD") : "";
    const origin = values.origin
      ? String(values.origin).trim().toUpperCase()
      : "";
    const destination = values.destination
      ? String(values.destination).trim().toUpperCase()
      : "";
    onSearch({ origin, destination, date });
  };

  const airportOptions = airports.map((a) => ({
    label: `${a.code} - ${a.name}, ${a.city}`,
    value: a.code,
  }));

  return (
    <div className={styles.form}>
      <h2 className={styles.sectionTitle}>Search flights</h2>
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Row gutter={16}>
          <Col xs={24} sm={8} md={6}>
            <Item
              label="Origin"
              name="origin"
              rules={[{ required: true, message: "Select origin airport" }]}
            >
              <Select
                placeholder="Select origin"
                size="large"
                showSearch
                optionFilterProp="label"
                loading={airportsLoading}
                options={airportOptions}
                filterOption={(input, opt) =>
                  (opt?.label ?? "").toLowerCase().includes(input.toLowerCase())
                }
              />
            </Item>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Item
              label="Destination"
              name="destination"
              rules={[
                { required: true, message: "Select destination airport" },
              ]}
            >
              <Select
                placeholder="Select destination"
                size="large"
                showSearch
                optionFilterProp="label"
                loading={airportsLoading}
                options={airportOptions}
                filterOption={(input, opt) =>
                  (opt?.label ?? "").toLowerCase().includes(input.toLowerCase())
                }
              />
            </Item>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Item
              label="Date"
              name="date"
              rules={[{ required: true, message: "Select date" }]}
            >
              <DatePicker
                size="large"
                style={{ width: "100%" }}
                format="YYYY-MM-DD"
              />
            </Item>
          </Col>
          <Col xs={24} sm={24} md={6}>
            <Item label=" " colon={false}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                block
              >
                Search
              </Button>
            </Item>
          </Col>
        </Row>
      </Form>
    </div>
  );
};

SearchForm.propTypes = {
  onSearch: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

SearchForm.defaultProps = {
  loading: false,
};

export default SearchForm;
